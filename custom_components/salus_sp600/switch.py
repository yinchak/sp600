"""Switch platform for Salus SP600 Smart Plug."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.zha.entity import ZhaEntity
from homeassistant.components.zha.core.const import (
    CLUSTER_HANDLER_ON_OFF,
    CLUSTER_HANDLER_METERING,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the switch platform."""
    _LOGGER.debug("Setting up Salus SP600 switch platform")
    zha_devices = hass.data.get("zha", {}).get("devices", {})
    entities = []
    for device in zha_devices.values():
        if CLUSTER_HANDLER_ON_OFF in device.cluster_handlers:
            entities.append(SalusSP600Switch(hass, device, entry))
    if entities:
        async_add_entities(entities)
        _LOGGER.info("Discovered %d Salus SP600 devices", len(entities))
    else:
        _LOGGER.warning("No Salus SP600 devices found with OnOff cluster")

class SalusSP600Switch(ZhaEntity, SwitchEntity):
    """Salus SP600 switch entity."""

    def __init__(self, hass: HomeAssistant, zha_device, entry: ConfigEntry):
        """Initialize the Salus SP600 switch."""
        super().__init__(zha_device)
        self._hass = hass
        self._zha_device = zha_device
        self._entry = entry
        self._attr_name = f"Salus SP600 {zha_device.ieee[-4:]}"
        self._attr_unique_id = f"salus_sp600_switch_{zha_device.ieee}"
        self._state = False
        self._power = None
        self._on_off_handler = zha_device.cluster_handlers.get(CLUSTER_HANDLER_ON_OFF)
        self._metering_handler = zha_device.cluster_handlers.get(CLUSTER_HANDLER_METERING)

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
        if self._on_off_handler:
            try:
                await self._on_off_handler.cluster.command(0x01)  # On
                self._state = True
                self.async_write_ha_state()
                _LOGGER.debug("Salus SP600 %s turned on", self._attr_unique_id)
            except Exception as err:
                _LOGGER.error("Failed to turn on Salus SP600: %s", err)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        if self._on_off_handler:
            try:
                await self._on_off_handler.cluster.command(0x00)  # Off
                self._state = False
                self.async_write_ha_state()
                _LOGGER.debug("Salus SP600 %s turned off", self._attr_unique_id)
            except Exception as err:
                _LOGGER.error("Failed to turn off Salus SP600: %s", err)

    async def async_update(self):
        """Update the entity state."""
        if self._on_off_handler:
            try:
                result = await self._on_off_handler.cluster.read_attributes(["on_off"])
                self._state = result.get("on_off", False)

                if self._metering_handler:
                    result = await self._metering_handler.cluster.read_attributes(["current_summation_delivered"])
                    self._power = result.get("current_summation_delivered", 0) / 1000  # kWh
                self.async_write_ha_state()
                _LOGGER.debug("Updated Salus SP600 %s: state=%s, power=%s", self._attr_unique_id, self._state, self._power)
            except Exception as err:
                _LOGGER.error("Failed to update Salus SP600 state: %s", err)
                self._state = None
                self._power = None
