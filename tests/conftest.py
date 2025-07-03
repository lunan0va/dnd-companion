"""
Konfigurationsdatei für Pytest.

Stellt gemeinsam genutzte Fixtures für die Testsuite zur Verfügung,
insbesondere für die Einrichtung der Test-Datenbank und des FastAPI TestClients.
"""
import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

load_dotenv(dotenv_path=".env.test")

SQLALCHEMY_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def db_engine():
    """
    Stellt die DB-Engine für die gesamte Test-Session bereit.
    Erstellt und löscht die Tabellen nur einmal pro Testlauf.
    """
    assert "test" in str(engine.url), "Gefahr! Es wird keine Test-DB verwendet."
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Stellt eine saubere DB-Transaktion für jeden einzelnen Test bereit.
    Anstatt Tabellen zu löschen, wird die Transaktion zurückgerollt.
    Das ist extrem schnell und isoliert die Tests perfekt.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Stellt einen TestClient zur Verfügung, der die echte DB-Dependency
    mit unserer Test-DB-Session überschreibt.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_client(client):
    """
    Erstellt einen Test-Benutzer, loggt ihn ein und gibt einen
    TestClient zurück, der mit dem Authentifizierungs-Header versehen ist.
    """
    client.post(
        "/register",
        json={"username": "auth_test_user", "password": "a_secure_password"}
    )

    login_response = client.post(
        "/login",
        data={"username": "auth_test_user", "password": "a_secure_password"}
    )
    token = login_response.json()["access_token"]

    client.headers = {
        "Authorization": f"Bearer {token}"
    }
    return client