import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config import settings
from app.database import get_db, Base
from fastapi import status



SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test'
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {"email": "123@gmail.com", "password": "Hello123"}
    response = client.post("/users", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    new_user = response.json()
    new_user['password'] = user_data['password']
    return new_user

