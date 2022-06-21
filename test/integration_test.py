import os
import subprocess
import pytest
import requests
import logging
from time import sleep

LOGGER = logging.getLogger(__name__)

PATCHES_PATH = 'kustomize/patches'
ALLOWED_HTTP_PATH = '/get'
FORBIDDEN_HTTP_PATH = '/?id=\'or+1=1--a-<script>prompt(1)</script>\''

patchList = []
for patchPath in os.listdir(PATCHES_PATH):
    patchList.append(patchPath)


class Helpers:
    @staticmethod
    def subprocess_run(cmd: str) -> subprocess.CompletedProcess:
        LOGGER.info(f'Command: {cmd}')
        completed_process = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        LOGGER.info(f'Finished with exit code: {completed_process.returncode}')

        return completed_process

    @staticmethod
    def create_namespace(namespace: str) -> subprocess.CompletedProcess:
        cmd = f'kubectl create namespace {namespace}'
        LOGGER.info('Create namespace ...')

        return Helpers.subprocess_run(cmd)

    @staticmethod
    def create(path: str, namespace: str) -> subprocess.CompletedProcess:
        cmd = f'kubectl create -k {path}/ --namespace {namespace}'
        LOGGER.info('Create configuration ...')

        return Helpers.subprocess_run(cmd)

    @staticmethod
    def wait(namespace: str, timeout: str = '180s') -> subprocess.CompletedProcess:
        cmd = f'kubectl wait --for=condition=Ready pods --all --timeout={timeout} --namespace {namespace}'
        LOGGER.info('Wait for all Pods will be ready ...')

        return Helpers.subprocess_run(cmd)

    @staticmethod
    def delete_namespace(namespace: str) -> subprocess.CompletedProcess:
        cmd = f'kubectl delete namespace {namespace}'
        LOGGER.info('Delete namespace ...')
        return Helpers.subprocess_run(cmd)


@pytest.fixture
def helpers():
    return Helpers


@pytest.fixture(scope="session")
def host(pytestconfig):
    return pytestconfig.getoption("host")


@pytest.fixture(scope="session")
def port(pytestconfig):
    return pytestconfig.getoption("port")


class TestMainFunctionality:
    @pytest.mark.parametrize("config", patchList)
    def test_main_functionality(self, config, helpers, host, port, teardown):
        config_path = f'{PATCHES_PATH}/{config}'
        namespace = config.replace('_', '-')
        base_url = f'http://{host}:{port}'
        allowed_url = base_url + ALLOWED_HTTP_PATH
        forbidden_url = base_url + FORBIDDEN_HTTP_PATH

        # Register teardown
        teardown['namespace'] = namespace

        namespace_created = helpers.create_namespace(namespace)
        assert namespace_created.returncode == 0, namespace_created.stderr

        create = helpers.create(config_path, namespace)
        assert create.returncode == 0, create.stderr

        wait = helpers.wait(namespace)
        assert wait.returncode == 0, wait.stderr

        sleep(5)
        LOGGER.info(f'Performing allowed request: {allowed_url} ...')
        allowed_request = requests.get(allowed_url)
        assert allowed_request.status_code == 200

        LOGGER.info(f'Performing forbidden request: {forbidden_url} ...')
        forbidden_request = requests.get(forbidden_url)
        assert forbidden_request.status_code == 403

    @pytest.fixture(scope="function")
    def teardown(self, helpers):
        config = {}
        yield config
        namespace = config.get('namespace')
        LOGGER.info('Teardown ...')
        helpers.delete_namespace(namespace)
