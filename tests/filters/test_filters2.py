import strawberry_django
from strawberry_django import auto, filter_field
from django.db import models

class BasicFilterModel(models.Model):
    string = models.CharField(max_length=50)
    number = models.IntegerField()

def test_basic():
    @strawberry_django.filter2(BasicFilterModel)
    class Filter:
        string: str
        number: int

    assert dict(Filter.filterset_class.get_fields()) == {
        'string': ['exact'],
        'number': ['exact'],
    }

def test_auto_types():
    @strawberry_django.filter2(BasicFilterModel)
    class Filter:
        string: auto
        number: auto

    assert dict(Filter.filterset_class.get_fields()) == {
        'string': ['exact'],
        'number': ['exact'],
    }

def test_field_without_annotation():
    @strawberry_django.filter2(BasicFilterModel)
    class Filter:
        string = filter_field()

    assert dict(Filter.filterset_class.get_fields()) == {
        'string': ['exact'],
    }

def test_field_lookup():
    @strawberry_django.filter2(BasicFilterModel)
    class Filter:
        string = filter_field(lookups=['exact', 'contains'])

    assert dict(Filter.filterset_class.get_fields()) == {
        'string': ['exact', 'contains'],
    }
