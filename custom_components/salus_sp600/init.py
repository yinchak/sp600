"""Salus SP600 Smart Plug 整合 for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import zigpy
import zigpy.config

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """整合設置（無 YAML 支援）."""
    _LOGGER.debug("開始 Salus SP600 整合設置")
    if "salus_sp600" in config:
        _LOGGER.warning("Salus SP600 不支援 YAML 配置，請用 UI 設定")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """從 UI config flow 設置整合."""
    _LOGGER.debug(f"從 config entry 設置 Salus SP600，端口：{entry.data.get('zigbee_port')}")
    hass.data.setdefault("salus_sp600", {})
    zigbee_port = entry.data.get("zigbee_port")
    try:
        app_config = zigpy.config.SCHEMA({"device": {"path": zigbee_port}})
        app = await zigpy.application.ControllerApplication.new(app_config)
        await app.startup()
        hass.data["salus_sp600"][entry.entry_id] = {"zigbee_app": app}
        await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
        _LOGGER.info(f"Salus SP600 整合設置成功，端口：{zigbee_port}")
    except Exception as err:
        _LOGGER.error(f"連繫唔到 Zigbee 端口 {zigbee_port}：{err}")
        raise ConfigEntryNotReady(f"連繫唔到 Zigbee 端口 {zigbee_port}：{err}")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸載整合."""
    _LOGGER.debug(f"卸載 Salus SP600 整合，entry ID：{entry.entry_id}")
    await hass.config_entries.async_unload_platforms(entry, ["switch"])
    app = hass.data["salus_sp600"][entry.entry_id]["zigbee_app"]
    await app.shutdown()
    hass.data["salus_sp600"].pop(entry.entry_id)
    return True
