def pytest_addoption(parser):
    parser.addoption("--host", action="store", default="0.0.0.0")
    parser.addoption("--port", action="store", default="30000")
