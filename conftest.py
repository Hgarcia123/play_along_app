# conftest.py
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path, override=True)

import pytest
from play_along import create_app
from play_along.db import init_db

@pytest.fixture(scope="module")
def app(tmp_path_factory):
    app = create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path_factory.mktemp("db") / "test.sqlite")
    })

    with app.app_context():
        init_db()
        yield app

@pytest.fixture(scope="module")
def client(app):
    return app.test_client()