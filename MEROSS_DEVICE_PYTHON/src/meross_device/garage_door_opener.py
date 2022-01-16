from fhem import Fhem
from meross_iot.controller.mixins.garage import GarageOpenerMixin
from meross_iot.model.enums import Namespace

from src.meross_device.meross_device import _logger
from src.meross_device.meross_fhem_device import MerossFhemDevice


class GarageDoorOpener(MerossFhemDevice):

    STATE_OPEN = "open"
    STATE_CLOSE = "close"

    def __init__(self, meross_device: GarageOpenerMixin, fhem: Fhem):
        __meross_device = meross_device
        MerossFhemDevice.__init__(self, meross_device, fhem)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        if namespace == Namespace.GARAGE_DOOR_STATE:
            self._set_fhem_state(self.STATE_CLOSE if data['togglex'][0]['open'] == 0 else self.STATE_OPEN)

    async def on_fhem_action(self, action):
        _logger.debug("New Action: " + str(action))
        if action['reading'] == 'STATE':
            if action['value'] == self.STATE_OPEN:
                await self._open()
            elif action['value'] == self.STATE_CLOSE:
                await self._close()
            elif action['value'] == "getStatus":
                self._set_fhem_state(self._is_open())
            elif action['value'] == "getDeviceType":
                self._set_fhem_device_type(self.__meross_device.type)
        elif action['reading'] == "position":
            if action['value'] == "0":
                await self._close()
            elif action['value'] == "1":
                await self._open()

    def _is_open(self):
        return self.__merossDevice.get_is_open()

    async def _open(self):
        _logger.info(f"Opening {self.__meross_device.name}...")
        await self.__merossDevice.async_open()
        _logger.debug("Door opened!")

    async def _close(self):
        _logger.info(f"Closing {self.__meross_device.name}...")
        await self.__merossDevice.async_close()
        _logger.debug("Door closed!")
