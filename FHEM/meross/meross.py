import asyncio
import configparser
import logging
import queue
from threading import Thread

import fhem
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager

from FHEM.meross.garage_door_opener import GarageDoorOpener

_logger = logging.getLogger("meross_device")


def connect_fhem(basePath: str, protocol: str, port: str, user: str, password: str):
    _logger.info('Establishing FHEM connection')
    return fhem.Fhem(basePath, protocol=protocol, port=port, username=user, password=password)


async def connect_meross(user: str, password: str):
    global http_api_client
    http_api_client = await MerossHttpClient.async_from_user_password(email=user, password=password)
    meross = MerossManager(http_client=http_api_client)
    await meross.async_init()
    await meross.async_device_discovery()
    return meross


async def disconnect_meross():
    meross.close()
    await http_api_client.async_logout()


async def listen_to_fhem(basePath: str):
    _logger.info('Establishing FHEM event queue')
    que = queue.Queue()
    fhemev = fhem.FhemEventQueue(basePath, que)
    while True:
        ev = que.get()
        if ev['devicetype'] == "MEROSS_DEVICE":
            meross_device = devices_by_fhem_name.get(ev['device'])
            await meross_device.on_fhem_action(ev)
        que.task_done()


async def main(loop):
    global meross
    global devices_by_uuid
    global devices_by_fhem_name

    devices_by_uuid = {}
    devices_by_fhem_name = {}

    config = configparser.ConfigParser()
    config.read('config.ini')

    _logger.info("----- CONNECTING TO FHEM -----")
    fhem_connection = connect_fhem(config["FHEM"]["basePath"], config["FHEM"]["protocol"], config["FHEM"]["port"],
                                   config["FHEM"]["user"], config["FHEM"]["password"])

    _logger.info("----- CONNECTING TO MEROSS -----")
    meross = await connect_meross(config["MEROSS"]["user"], config["MEROSS"]["password"])

    _logger.info("----- INITIALIZING DEVICES -----")
    devices = meross.find_devices()
    for dev in devices:
        if dev.type == "msg100":
            meross_device = GarageDoorOpener(dev, fhem_connection)
            await meross_device.async_update()
            _logger.debug("NEW DEVICE: " + str(meross_device))
            devices_by_uuid[meross_device.meross_id()] = meross_device
            devices_by_fhem_name[meross_device.fhem_name()] = meross_device

    _logger.info("----- LISTEN TO FHEM -----")
    asyncio.run_coroutine_threadsafe(listen_to_fhem(config["FHEM"]["basePath"]), loop)

    _logger.info("----- Initialization finished -----\n\n\n\n")

    # await disconnect_meross()


if __name__ == '__main__':
    meross_root_logger = logging.getLogger("meross_iot")
    meross_root_logger.setLevel(logging.INFO)

    # On Windows + Python 3.8, you should uncomment the following
    #    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    #    loop = asyncio.get_event_loop()
    #    loop.run_until_complete(main())
    #    loop.close()

    loop = asyncio.get_event_loop()
    loop.set_debug(True)
    thread = Thread(target=loop.run_forever)
    thread.start()
    app = asyncio.run_coroutine_threadsafe(main(loop), loop)
    app.result()
