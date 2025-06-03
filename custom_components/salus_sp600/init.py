"""Salus SP600 Smart Plug 整合 for Home Assistant."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import zigpy

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """設置 Salus SP600 整合."""
    hass.data.setdefault("salus_sp600", {})
    zigbee_port = entry.data.get("zigbee_port")
    try:
        # 初始化 Zigbee 應用
        app = await zigpy.application.ControllerApplication.new(
            zigpy.config.SCHEMA({"device": {"path": zigbee_port}})
        )
        await app.startup()
        hass.data["salus_sp600"][entry.entry_id] = {"zigbee_app": app}
    except Exception as err:
        raise ConfigEntryNotReady(f"連繫唔到 Zigbee 協調器 ({zigbee_port})：{err}")
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """卸載整合."""
    app = hass.data["salus_sp600"][entry.entry_id]["zigbee_app"]
    await app.shutdown()
    hass.data["salus_sp600"].pop(entry.entry_id)
    return True
