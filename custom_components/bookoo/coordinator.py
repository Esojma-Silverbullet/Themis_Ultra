"""Coordinator for Bookoo integration."""

from __future__ import annotations

from datetime import timedelta
import inspect
import logging
from typing import Any, Iterable

from aiobookoo_ultra.bookooscale import BookooScale
from aiobookoo_ultra.exceptions import BookooDeviceNotFound, BookooError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

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

        if ble_device := async_ble_device_from_address(
            self.hass, self._address, connectable=True
        ):
            self._scale.address_or_ble_device = ble_device

        if not ble_device:
            _LOGGER.debug(
                "BLE device not found for address %s",
                self.config_entry.data[CONF_ADDRESS],
            )
            self._scale.device_disconnected_handler(notify=False)
            return

        try:
            client = await establish_connection(
                BleakClientWithServiceCache,
                ble_device,
                self._address,
                disconnected_callback=self._async_handle_disconnect,
            )
            self._attach_ble_client(client)
            await self._async_setup_scale_connection(client, ble_device)
        except (BookooDeviceNotFound, BookooError, TimeoutError) as ex:
            _LOGGER.debug(
                "Could not connect to scale: %s, Error: %s",
                self.config_entry.data[CONF_ADDRESS],
                ex,
            )
            self._scale.device_disconnected_handler(notify=False)
            return

        # connected, set up background tasks

        if not self._scale.process_queue_task or self._scale.process_queue_task.done():
            self._scale.process_queue_task = (
                self.config_entry.async_create_background_task(
                    hass=self.hass,
                    target=self._scale.process_queue(),
                    name="bookoo_process_queue_task",
                )
            )

    @callback
    def _async_handle_disconnect(self) -> None:
        """Handle disconnects triggered by the retry connector."""
        self._scale.device_disconnected_handler(notify=False)

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
                    self._async_handle_disconnect,
                    connectable=True,
                )
            )
        except TypeError:
            entry.async_on_unload(
                async_register_bleak_retry_connector(  # type: ignore[call-arg]
                    self.hass,
                    entry,
                    self._address,
                    self._async_handle_disconnect,
                )
            )

    def _attach_ble_client(self, client: BleakClientWithServiceCache) -> None:
        """Attach an established BLE client to the scale if supported."""
        for attr_name in ("bleak_client", "client", "_client"):
            if hasattr(self._scale, attr_name):
                setattr(self._scale, attr_name, client)
                return

    async def _async_setup_scale_connection(
        self, client: BleakClientWithServiceCache, ble_device: Any
    ) -> None:
        """Run any optional scale setup hooks without direct client connect calls."""
        await self._async_call_optional(
            self._scale,
            (
                "setup_connection",
                "setup_notifications",
                "start_notifications",
                "start_notify",
                "initialize",
                "async_initialize",
                "setup",
                "async_setup",
                "setup_tasks",
            ),
            bleak_client=client,
            client=client,
            ble_device=ble_device,
            disconnected_callback=self._async_handle_disconnect,
        )

    async def _async_call_optional(
        self, obj: Any, method_names: Iterable[str], **kwargs: Any
    ) -> None:
        """Call the first available method from a list, awaiting if needed."""
        for method_name in method_names:
            method = getattr(obj, method_name, None)
            if not method:
                continue
            parameters = inspect.signature(method).parameters
            call_kwargs = {key: value for key, value in kwargs.items() if key in parameters}
            result = method(**call_kwargs)
            if inspect.isawaitable(result):
                await result
            return
