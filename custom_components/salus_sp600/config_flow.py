"""Config flow for Salus SP600 Smart Plug integration."""
import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.components.zha import DOMAIN as ZHA_DOMAIN

_LOGGER = logging.getLogger(__name__)

class SalusSP600ConfigFlow(config_entries.ConfigFlow, domain="salus_sp600"):
    """Handle a config flow for Salus SP600."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("Starting Salus SP600 config flow")
        errors = {}

        # Check if ZHA is configured
        if not self.hass.data.get(ZHA_DOMAIN):
            _LOGGER.error("ZHA integration not configured")
            errors["base"] = "ZHA integration not configured. Please set up ZHA first."

        if user_input is not None:
            zigbee_port = user_input["zigbee_port"]
            _LOGGER.debug("User input Zigbee port: %s", zigbee_port)
            try:
                # Validate port format
                if not zigbee_port.startswith(("/dev/", "COM")):
                    raise ValueError("Invalid port format. Use /dev/ttyACM0 or COM3")
                # Store configuration
                return self.async_create_entry(
                    title=f"Salus SP600 ({zigbee_port})",
                    data={"zigbee_port": zigbee_port}
                )
            except ValueError as err:
                _LOGGER.error("Invalid port format: %s", err)
                errors["base"] = str(err)
            except Exception as err:
                _LOGGER.error("Configuration failed: %s", err)
                errors["base"] = f"Configuration failed: {err}"

        # Show input form
        _LOGGER.debug("Showing Salus SP600 input form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("zigbee_port", default="/dev/ttyACM0"): str,
            }),
            errors=errors,
            description_placeholders={
                "example_ports": "e.g., /dev/ttyACM0, /dev/ttyUSB0, or COM3",
                "zha_tip": "Ensure ZHA is set up with the correct Zigbee stick"
            }
        )
