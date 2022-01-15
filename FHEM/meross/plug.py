from fhem import Fhem
from meross_iot.controller.device import BaseDevice
from meross_iot.controller.mixins.toggle import ToggleMixin
from meross_iot.model.enums import Namespace

from FHEM.meross.meross_device import _logger
from FHEM.meross.meross_fhem_device import MerossFhemDevice


class Plug(MerossFhemDevice):

    def __init__(self, meross_device: BaseDevice, fhem: Fhem):
        MerossFhemDevice.__init__(self, meross_device, fhem)

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        if namespace == Namespace.CONTROL_TOGGLEX:
            state: str = "on" if data['togglex'][0]['onoff'] == 0 else "off"
            self._set_fhem_state(state)

    async def on_fhem_action(self, action):
        _logger.debug("New Action: " + str(action))
        if action['reading'] == 'STATE':
            if action['value'] == 'on':
                if not self._is_on():
                    await self._turn_on()
            elif action['value'] == 'off':
                if self._is_on():
                    await self._turn_off()
            elif action['value'] == "getStatus":
                self._set_fhem_state(self._meross_device_is_open())
            elif action['value'] == "getDeviceType":
                self._set_fhem_device_type(self._meross_device_type())

    def _is_on(self):
        return ToggleMixin(self._merossDevice).is_on()

    async def _turn_on(self):
        _logger.info(f"Set {self._meross_device_name()} on...")
        await ToggleMixin(self._merossDevice).async_turn_on()
        _logger.debug("Door opened!")

    async def _turn_off(self):
        _logger.info(f"Set {self._meross_device_name()} off...")
        await ToggleMixin(self._merossDevice).async_turn_off()
        _logger.debug("Door closed!")
