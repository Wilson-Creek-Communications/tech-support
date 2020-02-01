#!/usr/bin/env python3

from logging import Logger, getLogger, basicConfig
from iperf import iperf
from classes import RemoteConfig
from getpass import getpass

if __name__ == "__main__":
    LOGGER: Logger = getLogger('wilson-creek.techsupport')

    # Logger format
    log_datefmt: str = '%H:%M:%S'
    log_format: str = '%(asctime)s:%(msecs)03d %(levelname)-8s: %(name)-20s: %(message)s'

    # Configure Logger
    basicConfig(datefmt=log_datefmt, format=log_format)

    remoteConfig: RemoteConfig = RemoteConfig()
    remoteConfig.remote_url = input('IP Address: ')
    remoteConfig.remote_port = 22
    remoteConfig.remote_user = input('Username: ')
    remoteConfig.remote_pass = getpass()

    iperfController: iperf = iperf(LOGGER, remoteConfig)

    results = iperfController.conductTest()

    print(results[0])
    print(results[1])