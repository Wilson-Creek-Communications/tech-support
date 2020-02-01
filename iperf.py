#!/usr/bin/env python3

from shell import Remote, Local
from getpass import getpass
from logging import Logger
from threading import Event, Thread
from time import sleep
from classes import RemoteConfig
from typing import List


class iperf(object):
    ''' An iperf controller.'''
    def __init__(self, LOGGER: Logger, config: RemoteConfig) -> None:
        '''Initialize an iperf controller.

        Arguments:
            LOGGER
            config
        '''
        self.config: RemoteConfig = config
        self.LOGGER: Logger = LOGGER

        # Initialize a Thread Event to detect when the remote has connected
        self.connected: Event = Event()
        # Initialize a remote shell handler
        self.remote: Remote = Remote(self.config, self.connected)
        # Initialize a local shell handler
        self.local: Local = Local()

    def conductTest(self) -> List[str]:
        '''Run an iperf test between the computer and the requested remote device.'''
        # Let's start!
        self.LOGGER.info('Conducting iPerf test...')

        remote_result: list = [None, []]
        local_result: list = [None, []]

        # We want to concurrently run shell commands because iperf won't exit until we finish the test
        # Prepare the remote server thread
        remoteThread: Thread = Thread(
            target=self.remote.execute, args=('iperf -s', remote_result,))
        localThread: Thread = Thread(target=self.local.execute, args=(
            ['iperf', '-c', self.config.remote_url, '-r'], local_result,))  # Prepare the local client thread

        remoteThread.start()   # Queue the iperf server starter thread for the remote device
        self.connected.wait()  # Wait for SSH connection
        sleep(1)               # Sleep a little while we wait for the server to start
        localThread.start()    # Queue the iperf client starter thread for the local device

        localThread.join()  # Wait for speedtest to finish

        self.remote.disconnect()  # Disconnect from remote

        return [local_result[1][10].decode().split('  ')[4], local_result[1][12].decode().split('  ')[4]]
