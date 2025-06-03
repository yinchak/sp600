"""Salus SP600 嘅開關平台."""
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import zigpy.zcl.clusters.general as general

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """設置開關平台."""
    app = hass.data["salus_sp600"][entry.entry_id]["zigbee_app"]
    # 假設 SP600 已配對，搵到設備
    devices = app.devices.values()
    entities = [SalusSP600Switch(device) for device in devices if device.get(0x0006)]  # OnOff 集群
    async_add_entities(entities)

class SalusSP600Switch(SwitchEntity):
    """Salus SP600 開關實體."""

    def __init__(self, device):
        self._device = device
        self._attr_name = f"Salus SP600 Switch"
        self._attr_unique_id = f"salus_sp600_{device.ieee}"
        self._state = False

    @property
    def is_on(self):
        """返還開關狀態."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """開啟插座."""
        cluster = self._device[0x0006]  # OnOff 集群
        await cluster.command(0x01)  # 開啟命令
        self._state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """關閉插座."""
        cluster = self._device[0x0006]  # OnOff 集群
        await cluster.command(0x00)  # 關閉命令
        self._state = False
        self.async_write_ha_state()

    async def async_update(self):
        """更新開關狀態."""
        cluster = self._device[0x0006]  # OnOff 集群
        result = await cluster.read_attributes(["on_off"])
        self._state = result[0].get("on_off", False)
