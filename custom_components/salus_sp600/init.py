"""Salus SP600 Smart Plug 整合 for Home Assistant."""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import zigpy
import zigpy.config

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """從 configuration.yaml 設置整合."""
    if "salus_sp600" not in config:
        return True

    zigbee_port = config["salus_sp600"].get("zigbee_port")
    if not zigbee_port:
        _LOGGER.error("未提供 Zigbee 端口")
        return False

    try:
        app_config = zigpy.config.SCHEMA({"device": {"path": zigbee_port}})
        app = await zigpy.application.ControllerApplication.new(app_config)
        await app.startup()
        hass.data.setdefault("salus_sp600", {})["zigbee_app"] = app
        _LOGGER.info(f"Zigbee 端口 {zigbee_port} 連繫成功")
    except Exception as err:
        _LOGGER.error(f"無法連繫 Zigbee 端口 {zigbee_port}：{err}")
        return False

    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """從 UI config flow 設置整合."""
    hass.data.setdefault("salus_sp600", {})
    zigbee_port = entry.data.get("zigbee_port")
    try:
        app_config = zigpy.config.SCHEMA({"device": {"path": zigbee_port}})
        app = await zigpy.application.ControllerApplication.new(app_config)
        await app.startup()
        hass.data["salus_sp600"][entry.entry_id] = {"zigbee_app": app}
        # 啟動設備掃描
        await hass.config_entries.async_forward_entry_setups(entry, ["switch"])
    except Exception as err:
        raise ConfigEntryNotReady(f"連繫唔到 Zigbee 端口 {zigbee_port}：{err}")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸載整合."""
    await hass.config_entries.async_unload_platforms(entry, ["switch"])
    app = hass.data["salus_sp600"][entry.entry_id]["zigbee_app"]
    await app.shutdown()
    hass.data["salus_sp600"].pop(entry.entry_id)
    return True
