import strawberry_django
from strawberry_django import auto
from .. import utils
from ..types import Fruit
from django.db import models

class DjangoFilterModel(models.Model):
    boolean = models.BooleanField()
    char = models.CharField(max_length=50)
    foreign_key = models.ForeignKey('DjangoFilterModel', on_delete=models.CASCADE)

@strawberry_django.type(DjangoFilterModel)
class Type:
    boolean: auto
    char: auto
    foreign_key: 'Type'

def test_filter_from_type():
    @strawberry_django.filter3
    class Filter(Type):
        pass

    assert [(f.name, f.type) for f in utils.type_fields(Filter)] == [
        ('boolean', bool),
        ('char', str),
        ('foreign_key', Type),
    ]

"""
def test_filter_from_model():
    @strawberry_django.filter3
    class Filter(Type):
        pass

    assert [(f.name, f.type) for f in utils.type_fields(Filter)] == [
        ('boolean', bool),
        ('char', str),
        ('foreign_key', Type),
    ]
"""
