import logging
from typing import Generator

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def logger() -> logging.Logger:
    return logging.getLogger("mail-service-unit-tests")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    from src.main import app

    with TestClient(app) as test_client:
        yield test_client
