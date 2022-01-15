import logging

from meross_iot.controller.device import BaseDevice
from meross_iot.model.enums import Namespace, OnlineStatus

_logger = logging.getLogger("meross_device")


class MerossDevice:

    def __init__(self, meross_device: BaseDevice):
        self._merossDevice = meross_device
        self._merossDevice.register_push_notification_handler_coroutine(self._on_meross_push_notification)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        raise NotImplementedError('Push notification handling not implemented for deviceId ' + device_internal_id)

    def _meross_device_id(self):
        return str(self._merossDevice.uuid)

    def _meross_device_name(self):
        return str(self._merossDevice.name)

    def _meross_device_status(self):
        return self._merossDevice.online_status

    def _meross_device_type(self):
        return self._merossDevice.type

    async def async_update(self):
        if self._merossDevice.online_status == OnlineStatus.ONLINE:
            await self._merossDevice.async_update()