from paramiko.auth_handler import AuthenticationException
from paramiko import SSHClient, AutoAddPolicy
from logging import getLogger, DEBUG
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from classes import GeneralError, ShellError, RemoteConfig
from typing import List, Any


class Remote(object):
    '''Remote host SSH client.'''

    def __init__(self, config: RemoteConfig, connected) -> None:
        self.config = config
        self.connected = connected
        self.remote: SSHClient
        self.LOGGER = getLogger('wilson-creek.remote-shell')
        self.LOGGER.setLevel(DEBUG)

    def __connect(self) -> None:
        '''Connect to remote.'''
        try:
            self.remote = SSHClient()
            self.remote.load_system_host_keys()
            self.remote.set_missing_host_key_policy(AutoAddPolicy())
            self.remote.connect(self.config.remote_url, port=self.config.remote_port,
                                username=self.config.remote_user, password=self.config.remote_pass)
            self.connected.set()
        except AuthenticationException:
            raise AuthenticationException('Authentication failed')

    def execute(self, cmd: str, result: List[Any], timeout: int = None) -> List[Any]:
        ''''Execute a commmand on a remote system.

        Arguments:
            cmd: The shell command to run.
            result: A list that contains the exit code and the stdout of the command.
            timeout: The amount of time in seconds to wait before giving up on the command to finish on its own.
        '''
        self.__connect()
        self.LOGGER.debug('=> %s', cmd)
        try:
            stdin: str
            stdout: str
            stderr: str
            stdin, stdout, stderr = self.remote.exec_command(
                cmd, timeout=timeout)

            self.LOGGER.debug('%r', stdout.readlines())

            exitcode = stdout.channel.recv_exit_status()

            result[0] = exitcode
            result[1] = stdout.readlines()

            if exitcode != 0:
                raise CalledProcessError(exitcode, cmd)

            return result

        except CalledProcessError as exception:
            raise ShellError(
                self.LOGGER, '{} Failed: {}'.format(cmd, exception))
        else:
            self.LOGGER.debug('%s finished successfully', cmd)

    def disconnect(self):
        """Close ssh connection."""
        self.remote.close()


class Local(object):

    def __init__(self) -> None:
        self.LOGGER = getLogger('wilson-creek.local-shell')
        self.LOGGER.setLevel(DEBUG)

    # Execute a shell command locally.
    def execute(self, cmd: List[str], result: List[Any]) -> List[Any]:
        '''A subprocess.Popen wrapper with logging.

        Arguments:
            cmd: The shell command to run.
            result: A list that contains the exit code and the stdout of the command.
        '''
        self.LOGGER.debug('=> %s', cmd)
        try:
            process = Popen(cmd, stdout=PIPE, stderr=STDOUT)

            stdout_list: List[str] = []

            with process.stdout:
                for stdout in iter(process.stdout.readline, b''):
                    self.LOGGER.debug('%r', stdout)
                    stdout_list.append(stdout)

            exitcode = process.wait()

            result[0] = exitcode
            result[1] = stdout_list

            if exitcode != 0:
                raise CalledProcessError(exitcode, cmd)

            return result

        except CalledProcessError as exception:
            raise ShellError(
                self.LOGGER, '{} Failed: {}'.format(cmd, exception))
        else:
            self.LOGGER.debug('%s finished successfully', cmd)
