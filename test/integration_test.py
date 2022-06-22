import os
import subprocess
import pytest
import requests
import logging
import shlex
from time import sleep

logger = logging.getLogger(__name__)

ALLOWED_HTTP_PATH = '/get'
FORBIDDEN_HTTP_PATH = '/?id=\'or+1=1--a-<script>prompt(1)</script>\''
PATCHES_PATH = 'kustomize/patches'
WAIT_PODS_TIMEOUT = '180s'

patchList = []
for patchPath in os.listdir(PATCHES_PATH):
    patchList.append(patchPath)


class Helpers:
    @staticmethod
    def subprocess_run(cmd: str) -> subprocess.CompletedProcess:
        logger.info(f'Command: {cmd}')
        completed_process = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
        logger.info(f'Finished with exit code: {completed_process.returncode}')
        return completed_process

    @staticmethod
    def create_namespace(namespace: str) -> subprocess.CompletedProcess:
        cmd = f'kubectl create namespace {namespace}'
        logger.info('Create namespace ...')
        return Helpers.subprocess_run(cmd)

    @staticmethod
    def create_resources(path: str, namespace: str) -> subprocess.CompletedProcess:
        cmd = f'kubectl create -k {path}/ --namespace {namespace}'
        logger.info('Create configuration ...')
        return Helpers.subprocess_run(cmd)

    @staticmethod
    def wait_pods(namespace: str, timeout: str = WAIT_PODS_TIMEOUT) -> subprocess.CompletedProcess:
        cmd = f'kubectl wait --for=condition=Ready pods --all --timeout={timeout} --namespace {namespace}'
        logger.info('Wait for all Pods ready ...')
        return Helpers.subprocess_run(cmd)

    @staticmethod
    def delete_namespace(namespace: str) -> subprocess.CompletedProcess:
        cmd = f'kubectl delete namespace {namespace}'
        logger.info('Delete namespace ...')
        return Helpers.subprocess_run(cmd)

    @staticmethod
    def setup_resources(path: str, namespace: str) -> subprocess.CompletedProcess:
        create_namespace = Helpers.create_namespace(namespace)
        if create_namespace.returncode != 0:
            return create_namespace
        create_resources = Helpers.create_resources(path, namespace)
        if create_resources.returncode != 0:
            return create_resources
        return Helpers.wait_pods(namespace)


@pytest.fixture(scope="function")
def helpers():
    return Helpers


@pytest.fixture(scope="session")
def base_url(pytestconfig):
    return f'http://{pytestconfig.getoption("host")}:{pytestconfig.getoption("port")}'


@pytest.fixture(scope="function")
def teardown_namespace():
    config = {}
    yield config
    namespace = config.get('namespace')
    logger.info('Teardown namespace ...')
    Helpers.delete_namespace(namespace)


class TestMainFunctionality:
    @pytest.mark.parametrize("config", patchList)
    def test_main_functionality(self, config, helpers, base_url, teardown_namespace):
        config_path = f'{PATCHES_PATH}/{config}'
        namespace = config.replace('_', '-')
        allowed_url = base_url + ALLOWED_HTTP_PATH
        forbidden_url = base_url + FORBIDDEN_HTTP_PATH

        # Register teardown
        teardown_namespace['namespace'] = namespace

        setup_resources = helpers.setup_resources(config_path, namespace)
        assert setup_resources.returncode == 0, setup_resources.stderr

        # Need delay here to ensure that service is ready to send traffic to pods
        sleep(2)

        logger.info(f'Performing allowed request: {allowed_url} ...')
        allowed_request = requests.get(allowed_url)
        assert allowed_request.status_code == 200

        logger.info(f'Performing forbidden request: {forbidden_url} ...')
        forbidden_request = requests.get(forbidden_url)
        assert forbidden_request.status_code == 403
