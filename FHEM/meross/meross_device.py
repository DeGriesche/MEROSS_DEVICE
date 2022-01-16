from meross_iot.model.enums import Namespace, OnlineStatus


class MerossDevice:

    def __init__(self, meross_device):
        self._channel = 0
        self.__meross_device = meross_device
        self.__meross_device.register_push_notification_handler_coroutine(self._on_meross_push_notification)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        raise NotImplementedError('Push notification handling not implemented for deviceId ' + device_internal_id)

    async def async_update(self):
        if self.__meross_device.online_status == OnlineStatus.ONLINE:
            await self.__meross_device.async_update()

    def _meross_device_name(self):
        return self.__meross_device.name

    def _meross_device_type(self):
        return self.__meross_device.type
