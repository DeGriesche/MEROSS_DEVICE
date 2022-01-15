from fhem import Fhem
from meross_iot.controller.device import BaseDevice
from meross_iot.model.enums import Namespace

from FHEM.meross.fhem_device import FhemDevice
from FHEM.meross.meross_device import MerossDevice


class MerossFhemDevice(MerossDevice, FhemDevice):

    def __init__(self, meross_device: BaseDevice, fhem: Fhem):
        MerossDevice.__init__(self, meross_device)
        FhemDevice.__init__(self, fhem, meross_device.uuid)

    def __str__(self):
        return self._meross_device_name() + " [" + self._fhem_device_name() + "] - " + self._meross_device_id()

    async def on_fhem_action(self, action):
        raise NotImplementedError('FHEM action handling not implemented.')

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        raise NotImplementedError('Push notification handling not implemented for deviceId ' + device_internal_id)

    def id(self):
        return self._meross_device_id()

    def name(self):
        return self._fhem_device_name()