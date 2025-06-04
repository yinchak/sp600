"""Salus SP600 Smart Plug integration for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.zha import DOMAIN as ZHA_DOMAIN

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
    if not hass.data.get(ZHA_DOMAIN):
        _LOGGER.error("ZHA integration is not configured")
        return False
    hass.data.setdefault("salus_sp600", {})
    hass.data["salus_sp600"][entry.entry_id] = {"zigbee_port": entry.data.get("zigbee_port")}
    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    _LOGGER.info("Salus SP600 setup completed for port: %s", entry.data.get("zigbee_port"))
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.debug("Unloading Salus SP600 entry: %s", entry.entry_id)
    await hass.config_entries.async_unload_platforms(entry, ["switch"])
    hass.data["salus_sp600"].pop(entry.entry_id)
    return True
