"""Salus SP600 整合嘅設定流程."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class SalusSP600ConfigFlow(config_entries.ConfigFlow, domain="salus_sp600"):
    """處理 Salus SP600 設定流程."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """處理初始設定步驟."""
        _LOGGER.debug("開始 Salus SP600 UI 設定流程")
        errors = {}

        if user_input is not None:
            zigbee_port = user_input["zigbee_port"]
            _LOGGER.debug(f"用戶輸入 Zigbee 端口：{zigbee_port}")
            try:
                # 簡單驗證端口格式
                if not zigbee_port.startswith(("/dev/", "COM")):
                    raise ValueError("端口格式無效，應為 /dev/ttyACM0 或 COM3")
                # 儲存配置（假設 ZHA 已處理 Zigbee 連繫）
                return self.async_create_entry(
                    title=f"Salus SP600 (Zigbee {zigbee_port})",
                    data={"zigbee_port": zigbee_port}
                )
            except ValueError as err:
                _LOGGER.error(f"端口格式錯誤：{err}")
                errors["base"] = str(err)
            except Exception as err:
                _LOGGER.error(f"設定失敗：{err}")
                errors["base"] = f"設定失敗：{err}"

        # 顯示輸入表單
        _LOGGER.debug("顯示 Zigbee 端口輸入表單")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("zigbee_port", default="/dev/ttyACM0"): str,
            }),
            errors=errors,
            description_placeholders={
                "example_ports": "例如：/dev/ttyACM0, /dev/ttyUSB0, 或 COM3",
                "permission_tip": "如果報錯，試喺終端機執行：sudo chmod 666 /dev/ttyACM0"
            }
        )
