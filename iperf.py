#!/usr/bin/env python3

from shell import Remote, Local
from getpass import getpass
from logging import Logger
from threading import Event, Thread
from time import sleep
from classes import RemoteConfig, GeneralError
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

        if self.config.remote_url == '' or self.config.remote_port == '' or self.config.remote_user == '' or self.config.remote_pass == '':
            raise GeneralError(LOGGER, 'Invalid Remote Config.')

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
            ['iperf', '-c', self.config.remote_url], local_result,))  # Prepare the local client thread ['iperf', '-c', self.config.remote_url, '-r'], local_result,

        remoteThread.start()   # Queue the iperf server starter thread for the remote device
        self.connected.wait()  # Wait for SSH connection
        # Sleep a little while we wait for the server to start
        sleep(1)
        localThread.start()    # Queue the iperf client starter thread for the local device

        localThread.join()  # Wait for speedtest to finish

        self.remote.disconnect()  # Disconnect from remote

        return [local_result[1][6].decode().split('  ')[4], local_result[1][8].decode().split('  ')[4]]
