import pytest
import strawberry
import strawberry_django
from strawberry_django import auto
from tests import models, utils
from tests.types import Fruit
from typing import List

@strawberry_django.ordering.order_by(models.Color)
class ColorOrderBy:
    name: auto

@strawberry_django.ordering.order_by(models.Fruit)
class FruitOrderBy:
    name: auto
    color: ColorOrderBy

@strawberry.type
class Query:
    fruits: List[Fruit] = strawberry_django.field(order_by=FruitOrderBy)

@pytest.fixture
def query():
    return utils.generate_query(Query)


def test_asc(query, fruits):
    result = query('{ fruits(orderBy: { name: asc }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '3', 'name': 'banana'},
        {'id': '2', 'name': 'raspberry'},
        {'id': '1', 'name': 'strawberry'},
    ]


def test_desc(query, fruits):
    result = query('{ fruits(orderBy: { name: desc }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
        {'id': '3', 'name': 'banana'},
    ]


def test_relationship(query, fruits):
    def add_color(fruit, color_name):
        fruit.color = models.Color.objects.create(name=color_name)
        fruit.save()
    color_names = ['red', 'dark red', 'yellow']
    [ add_color(fruit, color_name) for fruit, color_name in zip(fruits, color_names) ]
    result = query('{ fruits(orderBy: { color: { name: desc } }) { id name color { name } } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '3', 'name': 'banana', 'color': { 'name': 'yellow' } },
        {'id': '1', 'name': 'strawberry', 'color': { 'name': 'red' } },
        {'id': '2', 'name': 'raspberry', 'color': { 'name': 'dark red' } },
    ]
