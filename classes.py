from logging import Logger

###################
#  Error Classes  #
###################


class GeneralError(Exception):
    '''
    A general error, typically used for unexpected failures..
    '''

    def __init__(self, LOGGER: Logger, message: str, *args) -> None:
        super(GeneralError, self).__init__(message)
        LOGGER.exception('GeneralError: %s', message, *args)


class ShellError(Exception):
    '''
    A shell error. Used when a shell command doesn't exist or exits non-zero.
    '''

    def __init__(self, LOGGER: Logger, message: str, *args) -> None:
        '''Initialize the error.

        Arguments:
            LOGGER
        '''
        super(ShellError, self).__init__(message)
        LOGGER.exception('ShellError: %s', message, *args)


class RemoteConfig(object):
    remote_url: str
    remote_port: int
    remote_user: str
    remote_pass: str