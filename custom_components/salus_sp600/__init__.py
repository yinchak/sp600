"""Salus SP600 Smart Plug integration for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .zigbee import SP600ZigbeeCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Salus SP600 integration."""
    _LOGGER.debug("Initializing Salus SP600 integration")
    if "salus_sp600" in config:
        _LOGGER.warning("Salus SP600 does not support YAML configuration")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Salus SP600 from a config entry."""
    _LOGGER.debug("Setting up Salus SP600 with port: %s", entry.data.get("zigbee_port"))
    coordinator = SP600ZigbeeCoordinator(hass, entry.data["zigbee_port"])
    hass.data.setdefault("salus_sp600", {})
    hass.data["salus_sp600"][entry.entry_id] = coordinator
    try:
        await coordinator.start()
        await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
        _LOGGER.info("Salus SP600 setup completed for port: %s", entry.data["zigbee_port"])
        return True
    except Exception as err:
        _LOGGER.error("Failed to setup Salus SP600: %s", err)
        return False

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading Salus SP600 entry: %s", entry.entry_id)
    coordinator = hass.data["salus_sp600"].pop(entry.entry_id)
    await coordinator.shutdown()
    await hass.config_entries.async_unload_platforms(entry, ["switch"])
    return True
