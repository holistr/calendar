import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from core.serializers import ProfileSerializer


# ok
@pytest.mark.django_db
def test_create(client: APIClient) -> None:
    response = client.post(reverse('signup'),
                           data={'username': 'newtestuser',
                                 'first_name': 'testfirst',
                                 'last_name': 'testlast',
                                 'email': 'email@mail.ru',
                                 'password': 'super1Password',
                                 'password_repeat': 'super1Password'})

    expected_response = {'id': response.data.get('id'),
                         'last_login': None,
                         'is_superuser': False,
                         'username': 'newtestuser',
                         'first_name': 'testfirst',
                         'last_name': 'testlast',
                         'email': 'email@mail.ru',
                         'is_staff': False,
                         'is_active': False,
                         'date_joined': response.data.get('date_joined'),
                         'groups': [],
                         'user_permissions': []
                         }

    assert response.status_code == 201
    assert response.data == expected_response


# ok
@pytest.mark.django_db
def test_profile(auth_user: APIClient, add_user: User) -> None:
    response = auth_user.get(reverse('profile'))
    expected_response = ProfileSerializer(instance=add_user).data

    assert response.status_code == 200
    assert response.data == expected_response


# ok
@pytest.mark.django_db
def test_update_password(auth_user: APIClient, add_user: User) -> None:
    response = auth_user.put(
        reverse('update_password'),
        data={
            'new_password': 'SuperPassword1022362',
            'old_password': 'test1234',
        },
    )

    assert response.status_code == 200
