import strawberry
import strawberry_django
import pytest
from strawberry_django import auto, field
from typing import List
from . import models

from strawberry_django import utils

@pytest.fixture
def user_group(users, groups):
    users[0].group = groups[0]
    users[0].save()

@strawberry_django.type2(models.User)
class User:
    id: auto
    name: auto
    group: 'Group'

@strawberry_django.type2(models.Group)
class Group:
    id: auto
    name: auto
    users: List[User]

@strawberry_django.type2
class Query:
    user: User
    users: List[User]
    group: Group
    groups: List[Group]


def generate_query(query):
    schema = strawberry.Schema(query=query)
    def query(query, variable_values=None):
        if utils.is_async():
            return schema.execute(query, variable_values=variable_values)
        else:
            return schema.execute_sync(query, variable_values=variable_values)
    return query

@pytest.fixture
def query(db):
    return generate_query(Query)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.django_db(transaction=True),
]

async def test_single(query, user):
    result = await query('{ user { name } }')

    assert not result.errors
    assert result.data['user'] == { 'name': user.name }

async def test_many(query, users):
    result = await query('{ users { name } }')

    assert not result.errors
    assert result.data['users'] == [
        { 'name': users[0].name },
        { 'name': users[1].name },
        { 'name': users[2].name },
    ]

async def test_relation(query, users, groups, user_group):
    result = await query('{ users { name group { name } } }')

    assert not result.errors
    assert result.data['users'] == [
        { 'name': users[0].name, 'group': { 'name': groups[0].name } },
        { 'name': users[1].name, 'group': None },
        { 'name': users[2].name, 'group': None },
    ]

async def test_reverse_relation(query, users, groups, user_group):
    result = await query('{ groups { name users { name } } }')

    assert not result.errors
    assert result.data['groups'] == [
        { 'name': groups[0].name, 'users': [{ 'name': users[0].name }] },
        { 'name': groups[1].name, 'users': [] },
        { 'name': groups[2].name, 'users': [] },
    ]
