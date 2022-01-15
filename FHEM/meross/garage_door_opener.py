from fhem import Fhem
from meross_iot.controller.device import BaseDevice
from meross_iot.controller.mixins.garage import GarageOpenerMixin
from meross_iot.model.enums import Namespace

from FHEM.meross.meross_device import _logger
from FHEM.meross.meross_fhem_device import MerossFhemDevice


class GarageDoorOpener(MerossFhemDevice):

    def __init__(self, meross_device: BaseDevice, fhem: Fhem):
        MerossFhemDevice.__init__(self, meross_device, fhem)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        _logger.debug(">>>> ONPUSH " + str(namespace) + " [" + str(device_internal_id) + "]")
        _logger.debug("\t" + str(data))
        _logger.debug("<<<")

        if namespace == Namespace.GARAGE_DOOR_STATE:
            self._set_fhem_state(data['state'][0]['open'])

    async def on_fhem_action(self, action):
        _logger.debug("New Action: " + str(action))
        if action['reading'] == 'STATE':
            if action['value'] == 'open':
                await self._open()
            elif action['value'] == 'close':
                await self._close()
            elif action['value'] == "getStatus":
                self._set_fhem_state(self._is_open())
            elif action['value'] == "getDeviceType":
                self._set_fhem_device_type(self._meross_device_type())
        elif action['reading'] == "position":
            if action['value'] == "0":
                await self._close()
            elif action['value'] == "1":
                await self._open()

    def _is_open(self):
        return GarageOpenerMixin(self._merossDevice).get_is_open()

    async def _open(self):
        _logger.info(f"Opening {self._meross_device_name()}...")
        await GarageOpenerMixin(self._merossDevice).async_open(chanel=0)
        _logger.debug("Door opened!")

    async def _close(self):
        _logger.info(f"Closing {self._meross_device_name()}...")
        await GarageOpenerMixin(self._merossDevice).async_close()
        _logger.debug("Door closed!")
