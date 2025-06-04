"""Salus SP600 Smart Plug 整合 for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.zha import DOMAIN as ZHA_DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """整合設置（無 YAML 支援）."""
    _LOGGER.debug("開始 Salus SP600 整合設置")
    if "salus_sp600" in config:
        _LOGGER.warning("Salus SP600 不支援 YAML 配置，請用 UI 設定")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """從 UI config flow 設置整合."""
    _LOGGER.debug(f"設置 Salus SP600，端口：{entry.data.get('zigbee_port')}")
    if not hass.data.get(ZHA_DOMAIN):
        _LOGGER.error("ZHA 整合未設置，無法啟動 Salus SP600")
        return False
    hass.data.setdefault("salus_sp600", {})
    hass.data["salus_sp600"][entry.entry_id] = {"zigbee_port": entry.data.get("zigbee_port")}
    await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    _LOGGER.info(f"Salus SP600 設置成功，端口：{entry.data.get('zigbee_port')}")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸載整合."""
    _LOGGER.debug(f"卸載 Salus SP600，entry ID：{entry.entry_id}")
    await hass.config_entries.async_unload_platforms(entry, ["switch"])
    hass.data["salus_sp600"].pop(entry.entry_id)
    return True
