from fhem import Fhem
from meross_iot.model.enums import Namespace

from src.meross_device.fhem_device import FhemDevice
from src.meross_device.meross_device import MerossDevice


class MerossFhemDevice(MerossDevice, FhemDevice):

    def __init__(self, meross_device, fhem: Fhem):
        self.__meross_device = meross_device
        MerossDevice.__init__(self, meross_device)
        FhemDevice.__init__(self, fhem, meross_device.uuid)

    def __str__(self):
        return self.__meross_device.name + " [" + self._fhem_device_name() + "] - " + self.__meross_device.uuid

    async def on_fhem_action(self, action):
        raise NotImplementedError('FHEM action handling not implemented.')

    async def _on_meross_push_notification(self, namespace: Namespace, data: dict, device_internal_id: str):
        raise NotImplementedError('Push notification handling not implemented for deviceId ' + device_internal_id)

    def id(self):
        return self.__meross_device.uuid

    def name(self):
        return self._fhem_device_name()