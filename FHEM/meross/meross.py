import asyncio
import configparser
import logging.config
from queue import Queue
import threading
from threading import Thread

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
                self._devices_by_uuid[meross_device.meross_id()] = meross_device
                self._devices_by_fhem_name[meross_device.fhem_name()] = meross_device
            if dev.type == "mss310":
                meross_device = Plug(dev, fhem_connection)
                await meross_device.async_update()
                _logger.debug("NEW DEVICE: " + str(meross_device))
                self._devices_by_uuid[meross_device.meross_id()] = meross_device
                self._devices_by_fhem_name[meross_device.fhem_name()] = meross_device

        _logger.info("----- START LISTEN TO FHEM -----")
        que = Queue()
        t = threading.Thread(target=self.start_listen_to_fhem, args=(que,))
        t.daemon = True
        t.start()

        _logger.info("----- Initialization finished -----")

    async def shutdown(self):
        _logger.info("---- Shutting down ----")
        self._meross.close()
        await self._http_api_client.async_logout()
        self._fhem_event_queue.close()
        asyncio.get_event_loop().call_soon_threadsafe(asyncio.get_event_loop().stop)

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


def start():
    loop = asyncio.get_event_loop()
    thread = Thread(target=loop.run_forever)
    thread.start()
    app = asyncio.run_coroutine_threadsafe(Meross().run(), loop)
    app.result()


if __name__ == '__main__':
    start()
