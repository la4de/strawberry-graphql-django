import pytest
import strawberry
import strawberry_django
from .. import models, types, utils


def generate_query(*args, **kwargs):
    query = strawberry_django.queries(*args, **kwargs)
    return utils.generate_query(query)


def test_field_name(user):
    @strawberry_django.type(models.User, fields=[])
    class User:
        my_name: str = strawberry_django.field(field_name='name')
    query = generate_query(User)

    result = query('{ users { myName } }')
    assert not result.errors
    assert result.data['users'] == [{ 'myName': 'user' }]


def test_relational_field_name(user, group):
    @strawberry_django.type(models.User, fields=[])
    class User:
        my_group: types.Group = strawberry_django.field(field_name='group')
    query = generate_query(User)

    result = query('{ users { myGroup { name } } }')
    assert not result.errors
    assert result.data['users'] == [ { 'myGroup': { 'name': 'group' } } ]


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_sync_resolver(user, group):
    @strawberry_django.type(models.User, fields=[])
    class User:
        @strawberry_django.field
        def my_group(self, info) -> types.Group:
            return models.Group.objects.get()
    query = generate_query(User)

    result = await query('{ users { myGroup { name } } }')
    assert not result.errors
    assert result.data['users'] == [ { 'myGroup': { 'name': 'group' } } ]


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_async_resolver(user, group):
    @strawberry_django.type(models.User, fields=[])
    class User:
        @strawberry_django.field
        async def my_group(self, info) -> types.Group:
            from asgiref.sync import sync_to_async
            return await sync_to_async(models.Group.objects.get)()
    query = generate_query(User)

    result = await query('{ users { myGroup { name } } }')
    assert not result.errors
    assert result.data['users'] == [ { 'myGroup': { 'name': 'group' } } ]
