import logging

from meross_iot.model.enums import Namespace, OnlineStatus

_logger = logging.getLogger("meross_device")


class MerossDevice:

    def __init__(self, meross_device):
        self._channel = 0
        self.__merossDevice = meross_device
        self.__merossDevice.register_push_notification_handler_coroutine(self._on_meross_push_notification)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        raise NotImplementedError('Push notification handling not implemented for deviceId ' + device_internal_id)

    async def async_update(self):
        if self.__merossDevice.online_status == OnlineStatus.ONLINE:
            await self.__merossDevice.async_update()