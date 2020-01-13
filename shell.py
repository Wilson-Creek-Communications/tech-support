from paramiko.auth_handler import AuthenticationException
from paramiko import SSHClient, AutoAddPolicy
from logging import getLogger, DEBUG
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from errors import GeneralError, ShellError

"""Remote host object."""
class Remote:
    """Remote host SSH client."""

    def __init__(self, config, connected):
        self.remote_url = config.remote_url
        self.remote_port = config.remote_port
        self.remote_user = config.remote_user
        self.remote_pass = config.remote_pass
        self.connected = connected
        self.remote = None
        self.LOGGER = getLogger('wilson-creek.remote-shell')
        self.LOGGER.setLevel(DEBUG)

    def __connect(self):
        """Connect to remote."""
        if self.remote is None:
            try:
                remote = SSHClient()
                remote.load_system_host_keys()
                remote.set_missing_host_key_policy(AutoAddPolicy())
                remote.connect(self.remote_url, port=self.remote_port,
                               username=self.remote_user, password=self.remote_pass)
                self.connected.set()
            except AuthenticationException:
                raise AuthenticationException('Authentication failed')
            finally:
                return remote
        return self.remote

    def execute(self, cmd, result, timeout=None):
        """Execute a single unix command."""
        self.remote = self.__connect()
        self.LOGGER.debug('=> %s', cmd)
        try:
            stdin, stdout, stderr = self.remote.exec_command(cmd, timeout=timeout)

            self.LOGGER.debug('%r', stdout.readlines())

            exitcode = stdout.channel.recv_exit_status()

            if exitcode != 0:
                raise CalledProcessError(exitcode, cmd)

            result.append(exitcode)
            result.append(stdout)

            return stdout.readlines()

        except CalledProcessError as exception:
            raise ShellError(self.LOGGER, '{} Failed: {}'.format(cmd, exception))
        else:
            self.LOGGER.debug('%s finished successfully', cmd)

    def disconnect(self):
        """Close ssh connection."""
        self.remote.close()


class Local:

    def __init__(self):
        self.LOGGER = getLogger('wilson-creek.local-shell')
        self.LOGGER.setLevel(DEBUG)

    # Run a shell command.
    def run(self, command, result):
        '''
        A subprocess.Popen wrapper with logging.
        Arguments:
            command: The shell command to run.
        '''
        self.LOGGER.debug('=> %s', command)
        try:
            process = Popen(command, stdout=PIPE, stderr=STDOUT)

            result[1] = []

            with process.stdout:
                for stdout in iter(process.stdout.readline, b''):
                    self.LOGGER.debug('%r', stdout)
                    result[1].append(stdout)

            exitcode = process.wait()

            if exitcode != 0:
                raise CalledProcessError(exitcode, command)

            result[0] = exitcode

            return process

        except CalledProcessError as exception:
            raise ShellError(self.LOGGER, '{} Failed: {}'.format(command, exception))
        else:
            self.LOGGER.debug('%s finished successfully', command)
