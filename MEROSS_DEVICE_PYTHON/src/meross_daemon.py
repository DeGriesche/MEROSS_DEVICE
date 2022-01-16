import daemon

from meross import start

with daemon.DaemonContext():
    start()