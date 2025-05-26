import pytest
from fastapi.testclient import TestClient

from app import models
from app.main import app
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config import settings
from app.database import get_db
from app.models import Base
from fastapi import status
from app.oauth2 import create_access_token

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


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})



@pytest.fixture
def authorized_clients(client, token):
    client.headers.update({
        'Authorization': f"Bearer {token}",
    })
    return client

@pytest.fixture
def test_posts(session, test_user):
    posts_data = [     {
            "title": "post_title 1",
            "content": "some content of post title 1",
            "owner_id": test_user['id'],
        },
        {
            "title": "post_title 2",
            "content": "some content of post title 2",
            "owner_id": test_user['id'],
        },
        {
            "title": "post_title 3",
            "content": "some content of post title 3",
            "owner_id": test_user['id'],
        },
        {
            "title": "post_title 4",
            "content": "some content of post title 4",
            "owner_id": test_user['id'],
        }
    ]

    def create_posts(posts):
        return models.Post(**posts)

    post_map = map(create_posts, posts_data)
    posts = list(post_map)

    session.add_all(posts)
    session.commit()

    posts = session.query(models.Post).all()
    return posts