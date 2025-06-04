"""Simple Zigbee control for Salus SP600."""
import logging
import asyncio
import serial
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)

# Simple ZNP commands for TI CC2652P (SONOFF Zigbee Dongle)
SYS_PING = bytes([0xFE, 0x00, 0x21, 0x01, 0x20])
ZB_START_REQUEST = bytes([0xFE, 0x00, 0x26, 0x00, 0x26])
ZB_PERMIT_JOIN = bytes([0xFE, 0x02, 0x26, 0x08, 0xFF, 0xFF, 0x00])
ON_OFF_CMD = lambda state: bytes([0xFE, 0x03, 0x04, 0x02, 0x01, 0x00, state, 0x00])
METERING_READ = bytes([0xFE, 0x04, 0x0B, 0x04, 0x01, 0x00, 0x00, 0x00, 0x00])

class SP600ZigbeeCoordinator:
    """Manages Zigbee communication for Salus SP600."""

    def __init__(self, hass: HomeAssistant, port: str):
        """Initialize Zigbee coordinator."""
        self.hass = hass
        self.port = port
        self.serial = None
        self.devices = {}
        self.listeners = []

    async def start(self):
        """Start Zigbee communication."""
        _LOGGER.debug("Starting Zigbee communication on %s", self.port)
        try:
            self.serial = serial.Serial(self.port, baudrate=115200, timeout=1)
            # Send SYS_PING to test connection
            self.serial.write(SYS_PING)
            response = self.serial.read(10)
            if not response:
                raise RuntimeError("No response from Zigbee dongle")
            # Start Zigbee network
            self.serial.write(ZB_START_REQUEST)
            await asyncio.sleep(1)
            # Enable pairing
            self.serial.write(ZB_PERMIT_JOIN)
            _LOGGER.info("Zigbee network started on %s", self.port)
            # Start listening for devices
            self.hass.async_create_task(self._listen())
        except Exception as err:
            _LOGGER.error("Failed to start Zigbee communication: %s", err)
            raise

    async def shutdown(self):
        """Shutdown Zigbee communication."""
        if self.serial:
            self.serial.close()
            self.serial = None
            _LOGGER.debug("Zigbee communication shutdown")

    async def _listen(self):
        """Listen for new devices."""
        while self.serial and self.serial.is_open:
            try:
                data = self.serial.read(32)
                if data and len(data) > 4:
                    # Simple device discovery (mock IEEE for SP600)
                    ieee = f"sp600_{data.hex()[-8:]}"
                    if ieee not in self.devices:
                        self.devices[ieee] = {"state": False, "power": None}
                        _LOGGER.info("Discovered Salus SP600 device: %s", ieee)
                        self.hass.bus.async_fire("salus_sp600_device_discovered", {"ieee": ieee})
                await asyncio.sleep(0.1)
            except Exception as err:
                _LOGGER.error("Error listening for devices: %s", err)
                break

    async def send_command(self, ieee, command):
        """Send command to device."""
        if self.serial and ieee in self.devices:
            try:
                self.serial.write(command)
                await asyncio.sleep(0.1)
                response = self.serial.read(32)
                return response
            except Exception as err:
                _LOGGER.error("Failed to send command to %s: %s", ieee, err)

    def add_listener(self, listener):
        """Add listener for device updates."""
        self.listeners.append(listener)

async def test_zigbee_connection(port):
    """Test Zigbee connection."""
    serial_conn = None
    try:
        serial_conn = serial.Serial(port, baudrate=115200, timeout=1)
        serial_conn.write(SYS_PING)
        response = serial_conn.read(10)
        if not response:
            raise RuntimeError("No response from Zigbee dongle")
    finally:
        if serial_conn:
            serial_conn.close()
