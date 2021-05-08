import pytest
import strawberry
import strawberry_django
from strawberry_django import auto
from typing import Any, List

from tests.types import Fruit
from tests import utils, models

@strawberry_django.filters.filter(models.Color, lookups=True)
class ColorFilter:
    id: auto
    name: auto

@strawberry_django.filters.filter(models.Fruit, lookups=True)
class FruitFilter:
    id: auto
    name: auto
    color: ColorFilter
    search: str

    def filter_search(self, queryset):
        return queryset.filter(name__icontains=self.search)

@strawberry_django.filters.filter(models.Fruit)
class FruitSearchFilter:
    name: auto

    def filter(self, queryset):
        if self.name:
            queryset = queryset.filter(name__icontains=self.name)
        return queryset

@strawberry.type
class Query:
    fruits: List[Fruit] = strawberry_django.field(filters=FruitFilter)
    fruit_search: List[Fruit] = strawberry_django.field(filters=FruitSearchFilter)

@pytest.fixture
def query():
    return utils.generate_query(Query)


def test_without_filtering(query, fruits):
    result = query('{ fruits { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
        {'id': '3', 'name': 'banana'},
    ]


def test_exact(query, fruits):
    result = query('{ fruits(filters: { name: { exact: "strawberry" } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
    ]


def test_lt_gt(query, fruits):
    result = query('{ fruits(filters: { id: { gt: 1, lt: 3 } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '2', 'name': 'raspberry'},
    ]


def test_in_list(query, fruits):
    result = query('{ fruits(filters: { id: { inList: [ 1, 3 ] } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '3', 'name': 'banana'},
    ]


def test_relationship(query, fruits):
    color = models.Color.objects.create(name='red')
    color.fruits.set([fruits[0], fruits[1]])

    result = query('{ fruits(filters: { color: { name: { iExact: "RED" } } }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
    ]


def test_field_filter_method(query, fruits):
    result = query('{ fruits(filters: { search: "berry" }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
    ]


def test_type_filter_method(query, fruits):
    result = query('{ fruits: fruitSearch(filters: { name: "berry" }) { id name } }')
    assert not result.errors
    assert result.data['fruits'] == [
        {'id': '1', 'name': 'strawberry'},
        {'id': '2', 'name': 'raspberry'},
    ]
