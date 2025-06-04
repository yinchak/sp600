"""Salus SP600 嘅開關平台."""
import logging
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.zha.core.device import ZHADevice
from homeassistant.components.zha.core.const import CLUSTER_HANDLER_ON_OFF, CLUSTER_HANDLER_METERING

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """設置開關平台."""
    _LOGGER.debug("設置 Salus SP600 開關平台")
    zha_devices = hass.data.get("zha", {}).get("devices", {})
    entities = []
    for device in zha_devices.values():
        if CLUSTER_HANDLER_ON_OFF in device.cluster_handlers:
            entities.append(SalusSP600Switch(device))
    async_add_entities(entities)
    _LOGGER.info(f"發現 {len(entities)} 個 Salus SP600 設備")

class SalusSP600Switch(SwitchEntity):
    """Salus SP600 開關實體."""

    def __init__(self, zha_device: ZHADevice):
        self._zha_device = zha_device
        self._attr_name = f"Salus SP600 Switch {zha_device.ieee[-4:]}"
        self._attr_unique_id = f"salus_sp600_switch_{zha_device.ieee}"
        self._state = False
        self._power = None
        self._on_off_handler = zha_device.cluster_handlers.get(CLUSTER_HANDLER_ON_OFF)
        self._metering_handler = zha_device.cluster_handlers.get(CLUSTER_HANDLER_METERING)

    @property
    def is_on(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {"power_consumption": self._power}

    async def async_turn_on(self, **kwargs):
        if self._on_off_handler:
            try:
                await self._on_off_handler.cluster.command(0x01)  # 開啟
                self._state = True
                self.async_write_ha_state()
                _LOGGER.debug(f"Salus SP600 {self._attr_unique_id} 已開啟")
            except Exception as err:
                _LOGGER.error(f"開啟 Salus SP600 失敗：{err}")

    async def async_turn_off(self, **kwargs):
        if self._on_off_handler:
            try:
                await self._on_off_handler.cluster.command(0x00)  # 關閉
                self._state = False
                self.async_write_ha_state()
                _LOGGER.debug(f"Salus SP600 {self._attr_unique_id} 已關閉")
            except Exception as err:
                _LOGGER.error(f"關閉 Salus SP600 失敗：{err}")

    async def async_update(self):
        if self._on_off_handler:
            try:
                result = await self._on_off_handler.cluster.read_attributes(["on_off"])
                self._state = result[0].get("on_off", False)

                if self._metering_handler:
                    result = await self._metering_handler.cluster.read_attributes(["current_summation_delivered"])
                    self._power = result[0].get("current_summation_delivered", 0) / 1000  # kWh
                self.async_write_ha_state()
                _LOGGER.debug(f"更新 Salus SP600 {self._attr_unique_id} 狀態：{self._state}, 耗電量：{self._power}")
            except Exception as err:
                _LOGGER.error(f"更新 Salus SP600 狀態失敗：{err}")
                self._state = None
                self._power = None
