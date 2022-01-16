from logging import Logger

from fhem import Fhem
from meross_iot.controller.mixins.garage import GarageOpenerMixin
from meross_iot.model.enums import Namespace

from meross_fhem_device import MerossFhemDevice


class GarageDoorOpener(MerossFhemDevice):

    STATE_OPEN = "open"
    STATE_CLOSE = "close"

    def __init__(self, meross_device: GarageOpenerMixin, fhem: Fhem, logger: Logger):
        self.__meross_device = meross_device
        self.__logger = logger
        MerossFhemDevice.__init__(self, meross_device, fhem, logger)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        if namespace == Namespace.GARAGE_DOOR_STATE:
            self._set_fhem_state(self.STATE_CLOSE if data['togglex'][0]['open'] == 0 else self.STATE_OPEN)

    async def on_fhem_action(self, action):
        self.__logger.debug("New Action: " + str(action))
        if action['reading'] == 'STATE':
            if action['value'] == self.STATE_OPEN:
                await self._open()
            elif action['value'] == self.STATE_CLOSE:
                await self._close()
            elif action['value'] == "getStatus":
                self._set_fhem_state(self.STATE_OPEN if self._is_open() else self.STATE_CLOSE)
            elif action['value'] == "getDeviceType":
                self._set_fhem_device_type(self._meross_device_type())
        elif action['reading'] == "position":
            if action['value'] == "0":
                await self._close()
            elif action['value'] == "1":
                await self._open()

    def _is_open(self):
        return self.__meross_device.get_is_open()

    async def _open(self):
        self.__logger.info(f"Opening {self._meross_device_name()}...")
        await self.__meross_device.async_open()
        self.__logger.debug("Door opened!")

    async def _close(self):
        self.__logger.info(f"Closing {self._meross_device_name}...")
        await self.__meross_device.async_close()
        self.__logger.debug("Door closed!")
