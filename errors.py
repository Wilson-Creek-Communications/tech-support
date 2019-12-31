###################
#  Error Classes  #
###################

# A general error, typically used for unexpected failures.


class GeneralError(Exception):
    '''
    General error handler.
    '''

    def __init__(self, LOGGER, message, *args):
        super(GeneralError, self).__init__(message)
        self.message = message
        LOGGER.exception('GeneralError: %s', self.message, *args)


# General shell command error handler.
class ShellError(Exception):
    '''
    A shell error. Used when a shell command doesn't exist or exits non-zero.
    '''

    def __init__(self, LOGGER, message, *args):
        super(ShellError, self).__init__(message)
        self.message = message
        LOGGER.exception('ShellError: %s', self.message, *args)
