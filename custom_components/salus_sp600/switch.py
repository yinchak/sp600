"""Switch platform for Salus SP600 Smart Plug."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from .zigbee import ON_OFF_CMD, METERING_READ

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
        entities.append(SalusSP600Switch(hass, coordinator, ieee, entry))
        async_add_entities(entities)
        _LOGGER.info("Added Salus SP600 switch for device: %s", ieee)

    hass.bus.async_listen("salus_sp600_device_discovered", device_discovered)
    coordinator.add_listener(device_discovered)

class SalusSP600Switch(SwitchEntity):
    """Salus SP600 switch entity."""

    def __init__(self, hass: HomeAssistant, coordinator, ieee: str, entry: ConfigEntry):
        """Initialize the Salus SP600 switch."""
        self._hass = hass
        self._coordinator = coordinator
        self._ieee = ieee
        self._entry = entry
        self._attr_name = f"Salus SP600 {ieee[-4:]}"
        self._attr_unique_id = f"salus_sp600_switch_{ieee}"
        self._state = False
        self._power = None

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
        try:
            await self._coordinator.send_command(self._ieee, ON_OFF_CMD(0x01))
            self._state = True
            self.async_write_ha_state()
            _LOGGER.debug("Salus SP600 %s turned on", self._attr_unique_id)
        except Exception as err:
            _LOGGER.error("Failed to turn on Salus SP600: %s", err)

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            await self._coordinator.send_command(self._ieee, ON_OFF_CMD(0x00))
            self._state = False
            self.async_write_ha_state()
            _LOGGER.debug("Salus SP600 %s turned off", self._attr_unique_id)
        except Exception as err:
            _LOGGER.error("Failed to turn off Salus SP600: %s", err)

    async def async_update(self):
        """Update the entity state."""
        try:
            response = await self._coordinator.send_command(self._ieee, METERING_READ)
            if response:
                # Mock power consumption (parse response as needed)
                self._power = len(response) / 1000  # Placeholder
            self.async_write_ha_state()
            _LOGGER.debug("Updated Salus SP600 %s: state=%s, power=%s", self._attr_unique_id, self._state, self._power)
        except Exception as err:
            _LOGGER.error("Failed to update Salus SP600 state: %s", err)
            self._power = None
