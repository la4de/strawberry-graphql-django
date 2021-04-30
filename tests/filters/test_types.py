from django.db import models
from strawberry_django import auto, fields
from typing import List
import pytest
import strawberry
import strawberry_django
from .. import models, utils

from strawberry_django.filters3 import DjangoModelFilterInput

def test_filter():
    @strawberry_django.filter3(models.Fruit)
    class Filter:
        id: auto
        name: auto
        color: auto
        types: auto

    assert [(f.name, f.type) for f in fields(Filter)] == [
        ('id', strawberry.ID),
        ('name', str),
        ('color', DjangoModelFilterInput),
        ('types', DjangoModelFilterInput),
    ]

def test_lookups():
    @strawberry_django.filter3(models.Fruit, lookups=True)
    class Filter:
        id: auto
        name: auto
        color: auto
        types: auto

    assert [(f.name, f.type.__name__) for f in fields(Filter)] == [
        ('id', 'IDFilterLookup'),
        ('name', 'StrFilterLookup'),
        ('color', 'DjangoModelFilterInput'),
        ('types', 'DjangoModelFilterInput'),
    ]

def test_inherit(testtype):
    @testtype(models.Fruit)
    class Base:
        id: auto
        name: auto
        color: auto
        types: auto

    @strawberry_django.filter3(models.Fruit)
    class Filter(Base):
        pass

    assert [(f.name, f.type) for f in fields(Filter)] == [
        ('id', strawberry.ID),
        ('name', str),
        ('color', DjangoModelFilterInput),
        ('types', DjangoModelFilterInput),
    ]
