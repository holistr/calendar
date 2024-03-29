import json

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from core.models import User
from goals.models import GoalComment, Goal
from goals.serializers import GoalCommentSerializer


# ok
@pytest.mark.django_db
def test_create(auth_user: APIClient, add_user: User, goal: Goal, board_participant) -> None:
    response = auth_user.post(
        reverse('create_comment'),
        data={
           'text': 'tests comment',
           'user': add_user.pk,
           'goal': goal.pk,
        },
    )
    expected_response = {
        'id': response.data.get('id'),
        'text': 'tests comment',
        'goal': goal.pk,
        'created': response.data.get('created'),
        'updated': response.data.get('updated'),
    }

    assert response.status_code == 201
    assert response.data == expected_response


# ok
@pytest.mark.django_db
def test_retrieve(auth_user: APIClient, add_user: User, comment: GoalComment, goal: Goal) -> None:
    response = auth_user.get(reverse('retrieve_comment', args=[comment.pk]))

    expected_response = GoalCommentSerializer(instance=comment).data

    assert response.status_code == 200
    assert response.data == expected_response


# ok
@pytest.mark.django_db
def test_delete(auth_user: APIClient, goal: Goal, comment: GoalComment) -> None:
    response = auth_user.delete(reverse('retrieve_comment', args=[comment.pk]))

    assert response.status_code == 204


# ok
@pytest.mark.django_db
def test_update(auth_user: APIClient, goal: Goal, add_user: User, comment: GoalComment) -> None:
    response = auth_user.put(
        reverse('retrieve_comment', args=[comment.pk]),
        data=json.dumps({
            'text': 'put comment',
            'goal': goal.pk
        }),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.data.get('text') == 'put comment'
