#!/usr/bin/env python3

from logging import Logger, getLogger, basicConfig, DEBUG
from iperf import iperf
from classes import iPerfConfig
from getpass import getpass
from flask import Flask, render_template, request, session, redirect, url_for, Response
from paramiko import AuthenticationException

app = Flask(__name__)
app.secret_key = b'\x1f4\x95\xaf\x088\xe2\x01\xd0\x7fN\xda\xfc9\xa9\xb9'

LOGGER: Logger = getLogger('wilson-creek.techsupport')

iPerfConfig: iPerfConfig = iPerfConfig()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/iperf')
def test_page():
    return render_template('iperf.html')


@app.route('/iperf_results')
def test_results():
    down: str = request.args.get('down', 'Not tested')
    up: str = request.args.get('up', 'Not tested')
    return render_template('iperf_results.html', down=down, up=up)


@app.route('/iperf_ssh', methods=['POST'])
def run_test() -> Response:
    iPerfConfig.remote_url = request.form['ip_address']
    iPerfConfig.remote_port = request.form['port']
    iPerfConfig.remote_user = request.form['username']
    iPerfConfig.remote_pass = request.form['password']
    iPerfConfig.tcp_connections = request.form['connections']

    iPerfController: iperf = iperf(LOGGER, iPerfConfig)

    results = iPerfController.conductTest()
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
    app.run(debug=True, host='0.0.0.0', port='8080')
