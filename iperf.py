from shell import Remote, Local
from getpass import getpass
from logging import basicConfig, getLogger, INFO, DEBUG, WARNING
from threading import Event, Thread
from time import sleep

##########################
#  Initialize Variables  #
##########################

LOGGER = getLogger('wilson-creek.techsupport')

class RemoteConfig:
    remote_url = input('IP Address: ')
    remote_port = 22
    remote_user = input('Username: ')
    remote_pass = getpass()

connected = Event()
remote = Remote(RemoteConfig, connected)
local = Local()


##########
#  Main  #
##########

if __name__ == "__main__":
    # Logger format
    log_datefmt = '%H:%M:%S'
    log_format = '%(asctime)s:%(msecs)03d %(levelname)-8s: %(name)-20s: %(message)s'

    # Configure Logger
    basicConfig(datefmt=log_datefmt, format=log_format)

    # Logger output threshold customization
    LOGGER.setLevel(DEBUG)

    # Main
    LOGGER.info('Wilson Creek Techsupport Webserver')
    LOGGER.info('Starting...')

    remoteThread = Thread(target=remote.execute, args=('iperf -s', 30,))
    localThread = Thread(target=local.run, args=(['iperf2', '-c', RemoteConfig.remote_url, '-r'],))

    remoteThread.start()
    connected.wait()
    localThread.start()

    remoteThread.join()
    localThread.join()

    remote.disconnect()
