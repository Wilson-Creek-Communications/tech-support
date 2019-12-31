from atexit import register as atexit
from flask import Flask, render_template, request
from subprocess import Popen, CalledProcessError, PIPE, STDOUT
from logging import basicConfig, getLogger, INFO, DEBUG, WARNING
import sys
from paramiko import SSHClient

##########################
#  Initialize Variables  #
##########################

LOGGER = getLogger('wilson-creek.techsupport')
app = Flask(__name__)
ssh = SSHClient()


###################
#  Error Classes  #
###################

# A general error, typically used for unexpected failures.
class GeneralError(Exception):
    '''
    General error handler.
    '''

    def __init__(self, message, *args):
        super(GeneralError, self).__init__(message)
        self.message = message
        LOGGER.exception('GeneralError: %s', self.message, *args)
        #exit(1)


# General shell command error handler.
class ShellError(Exception):
    '''
    A shell error. Used when a shell command doesn't exist or exits non-zero.
    '''

    def __init__(self, message, *args):
        super(ShellError, self).__init__(message)
        self.message = message
        LOGGER.exception('ShellError: %s', self.message, *args)
        #exit(2)


####################
#  Shell Commands  #
####################

# Run a shell command.
def run(command):
    '''
    A subprocess.Popen wrapper with logging.
    Arguments:
        command: The shell command to run.
    '''
    LOGGER.debug('=> %s', command)
    try:
        process = Popen(command, stdout=PIPE, stderr=STDOUT)

        exitcode = process.wait()

        with process.stdout:
            for stdout in iter(process.stdout.readline, b''):
                LOGGER.debug('%s: %r', command, stdout)

        if exitcode != 0:
            raise CalledProcessError(exitcode, command)

        return process

    except CalledProcessError as exception:
        raise ShellError('{} Failed: {}'.format(command, exception))
    else:
        LOGGER.debug('%s finished successfully', command)

# Start the iPerf Servers
def startIperfServers() -> list:
    '''
    Start up iPerf Servers for client connection.
    '''
    LOGGER.info('Starting iPerf Servers...')
    iperf2_process = Popen(['iperf2', '-s'], stdout=PIPE, stderr=STDOUT)
    iperf3_process = Popen(['iperf3', '-s'], stdout=PIPE, stderr=STDOUT)

    return [iperf2_process, iperf3_process]

# Kill the iPerf Servers
def killIperfServers(processes: list):
    '''
    Kill all iPerf Servers.
    '''
    LOGGER.info('Killing iPerf Servers...')
    processes[0].terminate()
    processes[1].terminate()


##########
#  Main  #
##########

@atexit
def shutdown():
    killIperfServers(iperf_processes)

@app.route("/")
def index() -> render_template:
    return render_template("index.html")

@app.route("/iperf")
def iperf() -> render_template:
    return render_template("iperf.html")

@app.route("/iperf_ssh", methods=['POST'])
def iperf_ssh():
    ip_address = request.form['ip_address']
    password = request.form['password']
    return ip_address

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
    iperf_processes = startIperfServers()
    app.run(debug=True)
    
