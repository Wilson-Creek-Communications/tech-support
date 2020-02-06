#!/usr/bin/env python3

from shell import Remote, Local
from getpass import getpass
from logging import Logger
from threading import Event, Thread
from time import sleep
from classes import iPerfConfig, GeneralError
from typing import List
from re import search, Match

# RegEx to match a string that is like '####.## Mbits/sec', and return only the numbers
MBIT_PATTERN: str = '([0-9]{1,4}\\.[0-9][0-9])(?= Mbits)'


class iperf(object):
    ''' An iperf controller.'''

    def __init__(self, LOGGER: Logger, config: iPerfConfig) -> None:
        '''Initialize an iperf controller.

        Arguments:
            LOGGER
            config
        '''
        self.config: iPerfConfig = config  # Localize the iPerfConfig
        self.LOGGER: Logger = LOGGER  # Localize the logger

        if self.config.remote_url == '' or self.config.remote_user == '' or self.config.remote_pass == '':
            raise GeneralError(LOGGER, 'Invalid iPerf Config.')

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

        remote_result: list = [None, None]
        local_result: list = [None, None]

        # We want to concurrently run shell commands because iperf won't exit until we finish the test
        # Prepare the remote server thread
        remoteThread: Thread = Thread(
            target=self.remote.execute, args=('iperf -s', remote_result,))
        localThread: Thread = Thread(target=self.local.execute, args=(
            ['iperf', '-c', self.config.remote_url, '-P', str(self.config.tcp_connections)], local_result,))  # Prepare the local client thread

        remoteThread.start()   # Queue the iperf server starter thread for the remote device
        self.connected.wait()  # Wait for SSH connection
        # Sleep a little while we wait for the server to start
        sleep(1)
        localThread.start()    # Queue the iperf client starter thread for the local device

        localThread.join()  # Wait for speedtest to finish

        self.remote.disconnect()  # Disconnect from remote

        # Get a regex match of all megabit results
        speeds: Match = search(MBIT_PATTERN, local_result[1])

        if self.config.tcp_connections > 1:
            # If we have more than 1 tcp connection, return the sums
            return [speeds.group(self.config.tcp_connections), speeds.group((self.config.tcp_connections * 2) + 1)]

        # Otherwise, return the result
        return [speeds.group(0), speeds.group(1)]
