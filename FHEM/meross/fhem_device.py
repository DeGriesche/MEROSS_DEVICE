from logging import Logger

from fhem import Fhem


class FhemDeviceError(Exception):
    pass


class FhemDevice:

    def __init__(self, fhem: Fhem, device_id: str, logger: Logger):
        self._fhem = fhem
        self.__logger = logger
        fhem_devices = fhem.get(device_type=["MEROSS_DEVICE"], filters={"deviceId": device_id})

        if fhem_devices is not None and len(fhem_devices) > 0:
            self._fhem_device = fhem_devices[0]
        else:
            raise FhemDeviceError('No FHEM MEROSS_DEVICE found for deviceId ' + device_id)

    async def on_fhem_action(self, action):
        raise NotImplementedError('FHEM action handling not implemented.')

    def _fhem_device_name(self):
        return str(self._fhem_device['Name'])

    def _set_fhem_state(self, value: str):
        cmd: str = "setreading {} state {}".format(self._fhem_device_name(), value)
        self.__logger.debug("FHEM: " + cmd)
        self._fhem.send_cmd(cmd)

    def _set_fhem_device_type(self, device_type: str):
        cmd: str = "setreading {} deviceType {}".format(self._fhem_device_name(), device_type)
        self.__logger.debug("FHEM: " + cmd)
        self._fhem.send_cmd(cmd)
