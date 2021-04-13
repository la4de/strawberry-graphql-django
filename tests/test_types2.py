import strawberry_django
from strawberry_django import auto, field
from typing import List
import strawberry
from . import models
import django
import pytest


def test_field_type_auto_resolution():
    @strawberry_django.type(models.User)
    class User:
        id: auto
        name = field()

    assert [(f.name, f.type) for f in User._type_definition.fields] == [
        ('id', strawberry.ID),
        ('name', str),
    ]


def test_field_does_not_exist():
    with pytest.raises(django.core.exceptions.FieldDoesNotExist):
        @strawberry_django.type(models.User)
        class User:
            unknown_field: auto

    with pytest.raises(django.core.exceptions.FieldDoesNotExist):
        @strawberry_django.type(models.User)
        class User:
            unknown_field = field()


def test_field_type_from_resolver():
    global User

    def resolver() ->' User':
        pass

    @strawberry_django.type(models.User)
    class User:
        friend1 = strawberry_django.field(resolver)
        @strawberry_django.field
        def friend2() -> 'User':
            pass

    assert [(f.name, f.type) for f in User._type_definition.fields] == [
        ('friend1', User),
        ('friend2', User),
    ]

    del User


def test_field_type_from_field():
    global User

    def resolver():
        pass

    @strawberry_django.type(models.User)
    class User:
        friend: 'User' = strawberry_django.field(resolver)

    assert [(f.name, f.type) for f in User._type_definition.fields] == [
        ('friend', User),
    ]
