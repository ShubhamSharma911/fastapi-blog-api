from tests.conftest import authorized_clients


def test_get_all_posts(authorized_clients, test_posts):
    response = authorized_clients.get('/posts/')
    print(response.json())
    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200

