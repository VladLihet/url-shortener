import os

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app

if not os.environ.get("DATABASE_URL", "").endswith("_test"):
    raise RuntimeError(
        "Refusing to run tests: DATABASE_URL must point to a database ending in '_test'"
    )


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
