import asyncio
import os
from meross_iot.http_api import MerossHttpClient
from meross_iot.manager import MerossManager
import configparser
import logging.config

#_configApplication = "/opt/fhem/FHEM/meross/config.ini"
#_configLogging = "/opt/fhem/FHEM/meross/logging.conf"
from meross_iot.model.enums import Namespace

_configApplication = "config.ini"
_configLogging = "logging.conf"

logging.config.fileConfig(_configLogging)
_logger = logging.getLogger("meross_device")

async def main():

    _config = configparser.ConfigParser()
    _config.read(_configApplication)

    # Setup the HTTP client API from user-password
    config = _config["MEROSS"]
    http_api_client = await MerossHttpClient.async_from_user_password(email=config["user"], password=config["password"])

    # Setup and start the device manager
    manager = MerossManager(http_client=http_api_client)
    await manager.async_init()

    # Retrieve all the MSS310 devices that are registered on this account
    await manager.async_device_discovery()

    devices = manager.find_devices()
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


    if len(plugs) < 1:
        print("No MSS310 plugs found...")
    else:
        # Turn it on channel 0
        # Note that channel argument is optional for MSS310 as they only have one channel
        dev = plugs[0]

        # The first time we play with a device, we must update its status
        await dev.async_update()

        dev.register_push_notification_handler_coroutine(dev_push_handler)
        manager.register_push_notification_handler_coroutine(dev_push_handler)

        while True:
            await asyncio.Event().wait()

        dev.unregister_push_notification_handler_coroutine(dev_push_handler)
        manager.unregister_push_notification_handler_coroutine(dev_push_handler)


    # Close the manager and logout from http_api
    manager.close()
    await http_api_client.async_logout()

async def dev_push_handler(namespace, data, device_internal_id):
    _logger.info(">>>> ONPUSH " + str(namespace) + " [" + str(device_internal_id) + "]")

if __name__ == '__main__':
    # Windows and python 3.8 requires to set up a specific event_loop_policy.
    #  On Linux and MacOSX this is not necessary.
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()