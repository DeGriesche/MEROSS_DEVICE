import asyncio
import configparser
import logging.config
import os
import threading
from queue import Queue

import fhem
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

from FHEM.meross.plug import Plug
from garage_door_opener import GarageDoorOpener

#_configApplication = "/opt/fhem/FHEM/meross/config.ini"
#_configLogging = "/opt/fhem/FHEM/meross/logging.conf"
_configApplication = "config.ini"
_configLogging = "logging.conf"

logging.config.fileConfig(_configLogging)
_logger = logging.getLogger("meross_device")

class Meross:

    def __init__(self):
        self._devices_by_uuid = {}
        self._devices_by_fhem_name = {}
        self._meross = None
        self._http_api_client = None
        self._fhem_event_queue = None

        self._config = configparser.ConfigParser()
        self._config.read(_configApplication)

    async def run(self):
        _logger.info("----- CONNECTING TO FHEM -----")
        fhem_connection = self.connect_fhem()

        _logger.info("----- CONNECTING TO MEROSS -----")
        self._meross = await self.connect_meross()

        _logger.info("----- INITIALIZING DEVICES -----")
        devices = self._meross.find_devices()
        for dev in devices:
            if dev.type == "msg100":
                meross_device = GarageDoorOpener(dev, fhem_connection)
                await meross_device.async_update()
                _logger.debug("NEW DEVICE: " + str(meross_device))
                self._devices_by_uuid[meross_device.id()] = meross_device
                self._devices_by_fhem_name[meross_device.id()] = meross_device
            if dev.type == "mss310":
                meross_device = Plug(dev, fhem_connection)
                await meross_device.async_update()
                _logger.debug("NEW DEVICE: " + str(meross_device))
                self._devices_by_uuid[meross_device.id()] = meross_device
                self._devices_by_fhem_name[meross_device.name()] = meross_device

        _logger.info("----- START LISTEN TO FHEM -----")
        que = Queue()
        t = threading.Thread(target=self.start_listen_to_fhem, args=(que,))
        t.daemon = True
        t.start()

        _logger.info("----- Initialization finished -----")

        while True:
            await asyncio.Event().wait()

    def connect_fhem(self):
        _logger.info('Establishing FHEM connection')
        config = self._config["FHEM"]
        return fhem.Fhem(config["basePath"], protocol=config["protocol"], port=config["port"], username=config["user"], password=config["password"])

    async def connect_meross(self):
        config = self._config["MEROSS"]
        self._http_api_client = await MerossHttpClient.async_from_user_password(email=config["user"], password=config["password"])
        meross = MerossManager(http_client=self._http_api_client)
        await meross.async_init()
        await meross.async_device_discovery()
        return meross

    def start_listen_to_fhem(self, que: Queue):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.listen_to_fhem(que))
        loop.close()

    async def listen_to_fhem(self, que: Queue):
        self._fhem_event_queue = fhem.FhemEventQueue(self._config["FHEM"]["basePath"], que)
        while True:
            ev = que.get()
            if ev['devicetype'] == "MEROSS_DEVICE":
                _logger.debug(ev)
                if ev['value'] == "shutdown":
                    await self.shutdown()
                else:
                    meross_device = self._devices_by_fhem_name.get(ev['device'])
                    await meross_device.on_fhem_action(ev)
            que.task_done()


if __name__ == '__main__':
    # Windows and python 3.8 requires to set up a specific event_loop_policy.
    #  On Linux and MacOSX this is not necessary.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(Meross().run())
    loop.close()

