from shell import Remote, Local
from getpass import getpass
from logging import basicConfig, getLogger, INFO, DEBUG, WARNING
from threading import Event, Thread
from time import sleep

##########################
#  Initialize Variables  #
##########################

# Basic configuration for SSH
class RemoteConfig:
    remote_url = input('IP Address: ')
    remote_port = 22
    remote_user = input('Username: ')
    remote_pass = getpass()


LOGGER = getLogger('wilson-creek.techsupport') # Custom logger for our program

connected = Event()                      # Initialize a Thread Event to detect when the remote has connected
remote = Remote(RemoteConfig, connected) # Initialize a remote shell handler
local = Local()                          # Initialize a local shell handler


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

    # Let's start!
    LOGGER.info('Wilson Creek Techsupport Webserver')
    LOGGER.info('Starting...')

    remote_result = [None, []]
    local_result = [None, []]

    # We want to concurrently run shell commands because iperf won't exit until we finish the test
    remoteThread = Thread(target=remote.execute, args=('iperf -s', remote_result,))                              # Prepare the remote server thread
    localThread = Thread(target=local.run, args=(['iperf', '-c', RemoteConfig.remote_url, '-r'], local_result,)) # Prepare the local client thread

    remoteThread.start() # Queue the iperf server starter thread for the remote device
    connected.wait()     # Wait for SSH connection
    sleep(1)             # Sleep a little while we wait for the server to start
    localThread.start()  # Queue the iperf client starter thread for the local device

    localThread.join() # Wait for speedtest to finish

    remote.disconnect() # Disconnect from remote

    print("RESULTS:")
    print("Download: {}".format(local_result[1][10].decode().split('  ')[4]))
    print("Upload: {}".format(local_result[1][12].decode().split('  ')[4]))
