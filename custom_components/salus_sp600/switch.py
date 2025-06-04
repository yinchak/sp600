"""Switch platform for Salus SP600 Smart Plug."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.zha import ZhaDevice
from homeassistant.const import Platform

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the switch platform."""
    _LOGGER.debug("Setting up Salus SP600 switch platform")
    zha_devices = hass.data.get("zha", {}).get("devices", {})
    entities = []
    for device in zha_devices.values():
        if device.available and any(
            ep for ep in device.device.cluster_by_endpoint.values()
            if 0x0006 in ep.in_clusters  # OnOff cluster
        ):
            entities.append(SalusSP600Switch(hass, device, entry))
    if entities:
        async_add_entities(entities)
        _LOGGER.info("Discovered %d Salus SP600 devices", len(entities))
    else:
        _LOGGER.warning("No Salus SP600 devices found with OnOff cluster")

class SalusSP600Switch(SwitchEntity):
    """Salus SP600 switch entity."""

    def __init__(self, hass: HomeAssistant, zha_device: ZhaDevice, entry: ConfigEntry):
        """Initialize the Salus SP600 switch."""
        self._hass = hass
        self._zha_device = zha_device
        self._entry = entry
        self._attr_name = f"Salus SP600 {zha_device.ieee[-4:]}"
        self._attr_unique_id = f"salus_sp600_switch_{zha_device.ieee}"
        self._attr_device_info = zha_device.device_info
        self._state = None
        self._power = None
        # Find OnOff and Metering clusters
        self._on_off_cluster = None
        self._metering_cluster = None
        for endpoint in zha_device.device.cluster_by_endpoint.values():
            if 0x0006 in endpoint.in_clusters:  # OnOff
                self._on_off_cluster = endpoint.in_clusters[0x0006]
            if 0x0B04 in endpoint.in_clusters:  # Metering
                self._metering_cluster = endpoint.in_clusters[0x0B04]

    @property
    def is_on(self):
        """Return if the switch is on."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {"power": {"consumption": self._power}}

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        if self._on_off_cluster:
            try:
                await self._on_off_cluster.command(0x0006, 0x01)  # On
                self._state = True
                self.async_write_ha_state()
                _LOGGER.debug("Salus SP600 %s turned on", self._attr_unique_id)
            except Exception as err:
                _LOGGER.error("Failed to turn on Salus SP600: %s", err)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        if self._on_off_cluster:
            try:
                await self._on_off_cluster.command(0x00)  # Off
                self._state = False
                self.async_write_ha_state()
                _LOGGER.debug("Salus SP600 %s turned off", self._attr_unique_id)
            except Exception as err:
                _LOGGER.error("Failed to turn off Salus SP600: %s", err)

    async def async_update(self):
        """Update the entity state."""
        if self._on_off_cluster:
            try:
                result = await self._on_off_cluster.read_attributes(["on_off"])
                self._state = result.get("on_off", False)

                if self._metering_cluster:
                    result = await self._metering_cluster.read_attributes(["current_summation_delivered"])
                    self._power = result.get("current_summation_delivered", 0) / 1000  # kWh
                self.async_write_ha_state()
                _LOGGER.debug("Successfully Updated Salus SP600 %s: state=%s, power=%s", self._attr_unique_id, self._state, self._power)
            except Exception as err:
                _LOGGER.error("Failed to update Salus SP600 state: %s", err)
                self._state = None
                self._power = None
