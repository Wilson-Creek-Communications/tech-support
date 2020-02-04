#!/usr/bin/env python3

from logging import Logger, getLogger, basicConfig, DEBUG
from iperf import iperf
from classes import RemoteConfig
from getpass import getpass
from flask import Flask, render_template, request, session, redirect, url_for
from paramiko import AuthenticationException

app = Flask(__name__)
app.secret_key = b'\x1f4\x95\xaf\x088\xe2\x01\xd0\x7fN\xda\xfc9\xa9\xb9'
app.run(host=0.0.0.0)

LOGGER: Logger = getLogger('wilson-creek.techsupport')

remoteConfig: RemoteConfig = RemoteConfig()
remoteConfig.remote_port = 22
remoteConfig.remote_user = 'wccAdmin'


@app.route('/')
def index() -> render_template:
    return render_template('index.html')


@app.route('/iperf')
def test_page() -> render_template:
    return render_template('iperf.html')


@app.route('/iperf_results')
def test_results():
    down: str = request.args.get('down', 'Not tested')
    up: str = request.args.get('up', 'Not tested')
    return render_template('iperf_results.html', down=down, up=up)


@app.route('/iperf_ssh', methods=['POST'])
def run_test():
    remoteConfig.remote_url = request.form['ip_address']
    remoteConfig.remote_port = request.form['port']
    remoteConfig.remote_user = request.form['username']
    remoteConfig.remote_pass = request.form['password']

    print(remoteConfig.remote_url, remoteConfig.remote_port,
          remoteConfig.remote_user, remoteConfig.remote_pass)

    iperfController: iperf = iperf(LOGGER, remoteConfig)

    results = iperfController.conductTest()
    return redirect(url_for('test_results', down=results[0], up=results[1]))


if __name__ == '__main__':
    # Logger format
    log_datefmt: str = '%H:%M:%S'
    log_format: str = '%(asctime)s:%(msecs)03d %(levelname)-8s: %(name)-20s: %(message)s'

    # Configure Logger
    basicConfig(datefmt=log_datefmt, format=log_format)

    # Logger output threshold customization
    LOGGER.setLevel(DEBUG)

    # Main
    LOGGER.info('Wilson Creek Techsupport Webserver')
    app.run(debug=True)
