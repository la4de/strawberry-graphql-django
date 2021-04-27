import strawberry_django
import strawberry
from strawberry_django import FilterLookup
from ..types import Fruit
from .. import utils, models
from typing import List

@strawberry_django.filter3
class ColorFilter:
    id: FilterLookup[strawberry.ID]
    name: FilterLookup[str]

@strawberry_django.filter3
class FruitFilter:
    id: FilterLookup[strawberry.ID]
    name: FilterLookup[str]
    color: ColorFilter

@strawberry.type
class Query:
    fruits: List[Fruit] = strawberry_django.field(filters=FruitFilter)

def test_empty(fruits):
    query = utils.generate_query(Query)
    result = query('{ fruits { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
        {'id': '3', 'name': 'banana'},
    ]

def test_exact(fruits):
    query = utils.generate_query(Query)
    result = query('{ fruits(filters: { name: { exact: "strawberry" } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
    ]

def test_lt_gt(fruits):
    query = utils.generate_query(Query)
    result = query('{ fruits(filters: { id: { gt: 1, lt: 3 } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '2', 'name': 'raspberry'},
    ]

def test_in_list(fruits):
    query = utils.generate_query(Query)
    result = query('{ fruits(filters: { id: { inList: [ 1, 3 ] } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '3', 'name': 'banana'},
    ]

def test_relationship(fruits):
    color = models.Color.objects.create(name='red')
    color.fruits.set([fruits[0], fruits[1]])

    query = utils.generate_query(Query)
    result = query('{ fruits(filters: { color: { name: { iExact: "RED" } } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
    ]
