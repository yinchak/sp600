"""Config flow for Salus SP600 Smart Plug integration."""
import logging
import voluptuous as vol
import zigpy_znp
from homeassistant import config_entries
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class SalusSP600ConfigFlow(config_entries.ConfigFlow, domain="salus_sp600"):
    """Handle a config flow for Salus SP600."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        _LOGGER.debug("Initiating Salus SP600 config flow")
        errors = {}

        if user_input is not None:
            zigbee_port = user_input["zigbee_port"]
            _LOGGER.debug("Received Zigbee port input: %s", zigbee_port)
            try:
                # Validate port format
                if not zigbee_port.startswith(("/dev/", "COM")):
                    raise ValueError("Invalid port format. Expected /dev/ttyACM0 or COM3")
                # Test connection to Zigbee USB
                async with zigpy_znp.ZNP({"device": {"path": zigbee_port}}) as znp:
                    await znp.connect()
                return self.async_create_entry(
                    title=f"Salus SP600 ({zigbee_port})",
                    data={"zigbee_port": zigbee_port}
                )
            except ValueError as err:
                _LOGGER.error("Invalid port format: %s", err)
                errors["base"] = str(err)
            except Exception as err:
                _LOGGER.error("Failed to connect to Zigbee USB: %s", err)
                errors["base"] = f"Failed to connect to Zigbee USB: {err}"

        # Display input form
        _LOGGER.debug("Displaying Salus SP600 config form")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("zigbee_port", default="/dev/ttyACM0"): str,
            }),
            errors=errors,
            description_placeholders={
                "example_ports": "e.g., /dev/ttyACM0, /dev/ttyUSB0, or COM3"
            }
        )
