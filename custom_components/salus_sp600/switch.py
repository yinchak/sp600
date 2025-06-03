"""Salus SP600 嘅開關平台."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import zigpy.zcl.clusters.general as general
import zigpy.zcl.clusters.smartenergy as smartenergy

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """設置開關平台."""
    _LOGGER.debug("設置 Salus SP600 開關平台")
    app = hass.data["salus_sp600"][entry.entry_id]["zigbee_app"]
    devices = [device for device in app.devices.values() if device.get(0x0006)]  # OnOff 集群
    entities = [SalusSP600Switch(device) for device in devices]
    async_add_entities(entities)
    _LOGGER.info(f"發現 {len(entities)} 個 Salus SP600 設備")

class SalusSP600Switch(SwitchEntity):
    """Salus SP600 開關實體."""

    def __init__(self, device):
        self._device = device
        self._attr_name = f"Salus SP600 Switch {device.ieee[-4:]}"
        self._attr_unique_id = f"salus_sp600_{device.ieee}"
        self._state = False
        self._power = None

    @property
    def is_on(self):
        """返還開關狀態."""
        return self._state

    @property
    def extra_state_attributes(self):
        """返還額外狀態屬性（耗電量）."""
        return {"power_consumption": self._power}

    async def async_turn_on(self, **kwargs):
        """開啟插座."""
        try:
            cluster = self._device[0x0006]  # OnOff 集群
            await cluster.command(0x01)  # 開啟命令
            self._state = True
            self.async_write_ha_state()
            _LOGGER.debug(f"Salus SP600 {self._attr_unique_id} 已開啟")
        except Exception as err:
            _LOGGER.error(f"開啟 Salus SP600 失敗：{err}")

    async def async_turn_off(self, **kwargs):
        """關閉插座."""
        try:
            cluster = self._device[0x0006]  # OnOff 集群
            await cluster.command(0x00)  # 關閉命令
            self._state = False
            self.async_write_ha_state()
            _LOGGER.debug(f"Salus SP600 {self._attr_unique_id} 已關閉")
        except Exception as err:
            _LOGGER.error(f"關閉 Salus SP600 失敗：{err}")

    async def async_update(self):
        """更新開關同耗電量狀態."""
        try:
            cluster = self._device[0x0006]  # OnOff 集群
            result = await cluster.read_attributes(["on_off"])
            self._state = result[0].get("on_off", False)

            if 0x0B04 in self._device:
                metering = self._device[0x0B04]  # Metering 集群
                result = await metering.read_attributes(["current_summation_delivered"])
                self._power = result[0].get("current_summation_delivered", 0) / 1000  # 單位：kWh
            self.async_write_ha_state()
            _LOGGER.debug(f"更新 Salus SP600 {self._attr_unique_id} 狀態：{self._state}, 耗電量：{self._power}")
        except Exception as err:
            _LOGGER.error(f"更新 Salus SP600 狀態失敗：{err}")
            self._state = None
            self._power = None
