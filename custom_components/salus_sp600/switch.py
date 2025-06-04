"""Switch platform for Salus SP600 Smart Plug."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from zigpy.zcl.clusters.general import OnOff
from zigpy.zcl.clusters.measurement import Metering

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the switch platform."""
    _LOGGER.debug("Setting up Salus SP600 switch platform")
    coordinator = hass.data["salus_sp600"][entry.entry_id]
    entities = []

    @callback
    def device_discovered(event_data):
        """Handle new SP600 device discovery."""
        ieee = event_data["ieee"]
        device = coordinator.devices.get(ieee)
        if device:
            entities.append(SalusSP600Switch(hass, device, entry))
            async_add_entities(entities)
            _LOGGER.info("Added Salus SP600 switch for device: %s", ieee)

    hass.bus.async_listen("salus_sp600_device_discovered", device_discovered)

class SalusSP600Switch(SwitchEntity):
    """Salus SP600 switch entity."""

    def __init__(self, hass: HomeAssistant, device, entry: ConfigEntry):
        """Initialize the Salus SP600 switch."""
        self._hass = hass
        self._device = device
        self._entry = entry
        self._attr_name = f"Salus SP600 {device.ieee[-4:]}"
        self._attr_unique_id = f"salus_sp600_switch_{device.ieee}"
        self._state = False
        self._power = None
        self._on_off_cluster = None
        self._metering_cluster = None

        # Find OnOff and Metering clusters
        for endpoint in device.endpoints.values():
            if OnOff.cluster_id in endpoint.in_clusters:
                self._on_off_cluster = endpoint.in_clusters[OnOff.cluster_id]
            if Metering.cluster_id in endpoint.in_clusters:
                self._metering_cluster = endpoint.in_clusters[Metering.cluster_id]

    @property
    def is_on(self):
        """Return if the switch is on."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {"power_consumption": self._power}

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        if self._on_off_cluster:
            try:
                await self._on_off_cluster.command(0x01)  # On
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
                _LOGGER.debug("Updated Salus SP600 %s: state=%s, power=%s", self._attr_unique_id, self._state, self._power)
            except Exception as err:
                _LOGGER.error("Failed to update Salus SP600 state: %s", err)
                self._state = None
                self._power = None
