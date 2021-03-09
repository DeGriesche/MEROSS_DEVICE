import logging

from fhem import Fhem
from meross_iot.controller.device import BaseDevice
from meross_iot.model.enums import Namespace, OnlineStatus

_logger = logging.getLogger("meross_device")


class FhemDeviceError(object):
    pass


class GarageDoorOpener:

    def __init__(self, device: BaseDevice, fhem: Fhem):
        self._device = device
        self._fhem = fhem
        fhem_devices = fhem.get(device_type=["MEROSS_DEVICE"], filters={"deviceId": str(device.uuid)})
        if len(fhem_devices) > 0:
            self._fhem_device = fhem_devices[0]
        else:
            raise FhemDeviceError('No FHEM MEROSS_DEVICE found for deviceId ' + device.uuid)
        device.register_push_notification_handler_coroutine(self.on_meross_push_notification)

    def __str__(self):
        return str(self.meross_name()) + " [" + str(self.fhem_name()) + "] - " + str(self.meross_id())

    async def async_update(self):
        if self._device.online_status == OnlineStatus.ONLINE:
            await self._device.async_update()

    def meross_id(self):
        return self._device.uuid

    def meross_name(self):
        return self._device.name

    def fhem_name(self):
        return self._fhem_device['Name']

    def status(self):
        return self._device.online_status

    def device_type(self):
        return self._device.type

    def is_open(self):
        return self._device.get_is_open()

    async def open(self):
        _logger.info(f"Opening {self.meross_name(self)}...")
        await self._device.async_open(chanel=0)
        await self.async_update()
        _logger.debug("Door opened!")

    async def close(self):
        _logger.info(f"Closing {self.meross_name(self)}...")
        await self._device.async_close()
        await self.async_update()
        _logger.debug("Door closed!")

    def set_fhem_state(self, opened: bool):
        cmd: str = "setreading {} state {}".format(self.fhem_name(), "opened" if opened else "closed")
        _logger.info("FHEM: " + cmd)
        self._fhem.send_cmd(cmd)

    def set_fhem_device_type(self, device_type: str):
        cmd: str = "setreading {} deviceType {}".format(self.fhem_name(), device_type)
        _logger.info("FHEM: " + cmd)
        self._fhem.send_cmd(cmd)

    async def on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        _logger.debug(">>>> ONPUSH " + str(namespace) + " [" + str(device_internal_id) + "]")
        _logger.debug("\t" + str(data))
        _logger.debug("<<<")

        if namespace == Namespace.GARAGE_DOOR_STATE:
            self.set_fhem_state(data['state'][0]['open'])

    async def on_fhem_action(self, action):
        _logger.debug("New Action: " + str(action))
        if action['reading'] == 'STATE':
            if action['value'] == 'open':
                await self.open()
            elif action['value'] == 'close':
                await self.close()
            elif action['value'] == "getStatus":
                self.set_fhem_state(self.is_open())
            elif action['value'] == "getDeviceType":
                self.set_fhem_device_type(self.device_type())
