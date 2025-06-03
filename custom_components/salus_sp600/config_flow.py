"""Salus SP600 整合嘅設定流程."""
from homeassistant import config_entries
import voluptuous as vol

class SalusSP600ConfigFlow(config_entries.ConfigFlow, domain="salus_sp600"):
    """處理 Salus SP600 嘅設定流程."""

    async def async_step_user(self, user_input=None):
        """處理初始設定步驟."""
        errors = {}
        if user_input is not None:
            zigbee_port = user_input["zigbee_port"]
            try:
                # 測試 Zigbee 端口（簡單檢查）
                return self.async_create_entry(
                    title=f"Salus SP600 (Zigbee {zigbee_port})",
                    data={"zigbee_port": zigbee_port}
                )
            except Exception as err:
                errors["base"] = f"連繫錯誤：{err}"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("zigbee_port", default="/dev/ttyUSB0"): str,
            }),
            errors=errors,
        )
