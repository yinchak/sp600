"""Zigbee network management for Salus SP600."""
import logging
import zigpy
import zigpy_znp
from zigpy.device import Device as ZigpyDevice
from zigpy.zcl.clusters.general import OnOff
from zigpy.zcl.clusters.measurement import Metering

_LOGGER = logging.getLogger(__name__)

class SP600ZigbeeCoordinator:
    """Manages Zigbee network for Salus SP600."""

    def __init__(self, hass, port):
        """Initialize Zigbee coordinator."""
        self.hass = hass
        self.port = port
        self.app = None
        self.devices = {}

    async def start(self):
        """Start Zigbee network."""
        _LOGGER.debug("Starting Zigbee network on %s", self.port)
        try:
            config = {"device": {"path": self.port}}
            self.app = zigpy_znp.ZNPApplication(config)
            await self.app.startup(auto_form=True)
            self.app.add_listener(self)
            _LOGGER.info("Zigbee network started on %s", self.port)
        except Exception as err:
            _LOGGER.error("Failed to start Zigbee network: %s", err)
            raise

    async def shutdown(self):
        """Shutdown Zigbee network."""
        if self.app:
            await self.app.shutdown()
            _LOGGER.debug("Zigbee network shutdown")

    def device_initialized(self, device: ZigpyDevice):
        """Handle new device joining."""
        _LOGGER.debug("Device initialized: %s", device.ieee)
        if any(
            ep for ep in device.endpoints.values()
            if OnOff.cluster_id in ep.in_clusters
        ):
            self.devices[device.ieee] = device
            _LOGGER.info("Discovered Salus SP600 device: %s", device.ieee)
            self.hass.bus.async_fire("salus_sp600_device_discovered", {"ieee": str(device.ieee)})
