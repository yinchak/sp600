"""Salus SP600 整合嘅設定流程."""
import asyncio
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
import zigpy
import zigpy.config

_LOGGER = logging.getLogger(__name__)

class SalusSP600ConfigFlow(config_entries.ConfigFlow, domain="salus_sp600"):
    """處理 Salus SP600 嘅設定流程."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """處理初始設定步驟."""
        errors = {}

        if user_input is not None:
            zigbee_port = user_input["zigbee_port"]
            try:
                # 測試 Zigbee 端口連繫
                _LOGGER.debug(f"試連 Zigbee 端口：{zigbee_port}")
                app_config = zigpy.config.SCHEMA({"device": {"path": zigbee_port}})
                app = await zigpy.application.ControllerApplication.new(app_config)
                await app.startup()
                await app.shutdown()  # 測試完即關閉
                _LOGGER.info(f"Zigbee 端口 {zigbee_port} 連繫成功")
                return self.async_create_entry(
                    title=f"Salus SP600 (Zigbee {zigbee_port})",
                    data={"zigbee_port": zigbee_port}
                )
            except zigpy.exceptions.ControllerException as err:
                _LOGGER.error(f"Zigbee 控制器錯誤：{err}")
                errors["base"] = f"無法連繫 Zigbee 端口：{err}"
            except asyncio.TimeoutError:
                _LOGGER.error("連繫 Zigbee 端口超時")
                errors["base"] = "連繫 Zigbee 端口超時"
            except Exception as err:
                _LOGGER.error(f"未知錯誤：{err}")
                errors["base"] = f"設定失敗：{err}"

        # 顯示輸入表單
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("zigbee_port", default="/dev/ttyUSB0"): str,
            }),
            errors=errors,
            description_placeholders={
                "example_ports": "例如：/dev/ttyUSB0, /dev/ttyACM0, 或 Windows 的 COM3"
            }
        )
