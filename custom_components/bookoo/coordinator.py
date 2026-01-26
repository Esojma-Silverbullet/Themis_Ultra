"""Coordinator for Bookoo integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiobookoo_ultra.bookooscale import BookooScale
from aiobookoo_ultra.exceptions import BookooDeviceNotFound, BookooError
from bleak.backends.device import BLEDevice
from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from bleak_retry_connector import BleakNotFoundError, BleakOutOfConnectionSlotsError

from homeassistant.components.bluetooth import async_ble_device_from_address
try:
    from homeassistant.components.bluetooth import (
        async_register_bleak_retry_connector,
    )
except ImportError:
    async_register_bleak_retry_connector = None

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_IS_VALID_SCALE

SCAN_INTERVAL = timedelta(seconds=5)

_LOGGER = logging.getLogger(__name__)

type BookooConfigEntry = ConfigEntry[BookooCoordinator]


class BookooCoordinator(DataUpdateCoordinator[None]):
    """Class to handle fetching data from the scale."""

    config_entry: BookooConfigEntry

    def __init__(self, hass: HomeAssistant, entry: BookooConfigEntry) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="bookoo coordinator",
            update_interval=SCAN_INTERVAL,
            config_entry=entry,
        )

        self._address = entry.data[CONF_ADDRESS]
        self._scale = BookooScale(
            address_or_ble_device=self._address,
            name=entry.title,
            is_valid_scale=entry.data[CONF_IS_VALID_SCALE],
            notify_callback=self.async_update_listeners,
        )
        self._client: BleakClientWithServiceCache | None = None
        self._async_register_bleak_connector(entry)

    @property
    def scale(self) -> BookooScale:
        """Return the scale object."""
        return self._scale

    async def _async_update_data(self) -> None:
        """Fetch data."""

        # scale is already connected, return
        if self._scale.connected:
            return

        if self._client and self._client.is_connected:
            self._sync_scale_client(self._client)
            if hasattr(self._scale, "attach_client"):
                await self._scale.attach_client(self._client, setup_tasks=False)
            else:
                await self._scale.connect(setup_tasks=False)
            self._ensure_process_queue_task()
            return

        if not (ble_device := async_ble_device_from_address(
            self.hass, self._address, connectable=True
        )):
            _LOGGER.debug("No BLE device available for %s", self._address)
            return

        await self._async_establish_link(ble_device)
        if self._client and self._client.is_connected:
            if hasattr(self._scale, "attach_client"):
                await self._scale.attach_client(self._client, setup_tasks=False)
            else:
                await self._scale.connect(setup_tasks=False)
            self._ensure_process_queue_task()

    async def _async_establish_link(self, ble_device: BLEDevice) -> None:
        """Establish the BLE link via the retry connector."""
        try:
            try:
                self._client = await establish_connection(
                    BleakClientWithServiceCache,
                    ble_device,
                    disconnected_callback=self._async_handle_link_loss,
                    name="bookoo",
                    timeout=20.0,
                )
            except TypeError:
                self._client = await establish_connection(
                    ble_device,
                    disconnected_callback=self._async_handle_link_loss,
                    name="bookoo",
                    timeout=20.0,
                )
        except (
            BleakError,
            BleakNotFoundError,
            BleakOutOfConnectionSlotsError,
            BookooDeviceNotFound,
            BookooError,
            TimeoutError,
        ) as ex:
            _LOGGER.debug(
                "Could not establish BLE link to scale: %s, Error: %s",
                self.config_entry.data[CONF_ADDRESS],
                ex,
            )
            self._scale.device_disconnected_handler(notify=False)
            self._client = None
            return

        self._scale.address_or_ble_device = ble_device
        self._sync_scale_client(self._client)

    def _sync_scale_client(self, client: BleakClientWithServiceCache | None) -> None:
        """Ensure the scale uses the established BLE client."""
        if client is None:
            return

        for attr_name in ("client", "_client", "bleak_client", "_bleak_client"):
            if hasattr(self._scale, attr_name):
                setattr(self._scale, attr_name, client)
        if ble_device := async_ble_device_from_address(
            self.hass, self._address, connectable=True
        ):
            for attr_name in ("device", "_device", "ble_device", "_ble_device"):
                if hasattr(self._scale, attr_name):
                    setattr(self._scale, attr_name, ble_device)

    @callback
    def _async_handle_link_loss(
        self, _client: BleakClientWithServiceCache | None = None
    ) -> None:
        """Handle link losses triggered by the retry connector."""
        self._scale.device_disconnected_handler(notify=False)
        self._client = None

    def _ensure_process_queue_task(self) -> None:
        """Ensure the processing queue task is running."""
        if not self._scale.process_queue_task or self._scale.process_queue_task.done():
            self._scale.process_queue_task = (
                self.config_entry.async_create_background_task(
                    hass=self.hass,
                    target=self._scale.process_queue(),
                    name="bookoo_process_queue_task",
                )
            )

    def _async_register_bleak_connector(self, entry: BookooConfigEntry) -> None:
        """Ensure bleak connections are routed through the retry connector."""
        if not async_register_bleak_retry_connector:
            _LOGGER.debug(
                "BLE retry connector helper is unavailable; skipping connector registration"
            )
            return

        try:
            entry.async_on_unload(
                async_register_bleak_retry_connector(
                    self.hass,
                    entry,
                    self._address,
                    self._async_handle_link_loss,
                    connectable=True,
                )
            )
        except TypeError:
            entry.async_on_unload(
                async_register_bleak_retry_connector(  # type: ignore[call-arg]
                    self.hass,
                    entry,
                    self._address,
                    self._async_handle_link_loss,
                )
            )
