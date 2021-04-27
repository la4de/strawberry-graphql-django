import strawberry
from strawberry.arguments import is_unset, UNSET
from django.db import models
import asyncio
import warnings


def is_async():
    # django uses the same method to detect async operation
    # https://github.com/django/django/blob/76c0b32f826469320c59709d31e2f2126dd7c505/django/utils/asyncio.py
    try:
        event_loop = asyncio.get_event_loop()
    except RuntimeError:
        pass
    else:
        if event_loop.is_running():
            return True
    return False


def deprecated(msg, stacklevel=1):
    warnings.warn(msg, DeprecationWarning, stacklevel=stacklevel + 1)

def is_strawberry_type(obj):
    return hasattr(obj, '_type_definition')

def is_django_type(obj):
    return hasattr(obj, '_django_model')

def is_django_model(obj):
    return isinstance(obj, models.base.ModelBase)

def is_django_field(obj):
    from .fields.field import DjangoField
    return isinstance(obj, DjangoField)

def type_fields(type_):
    return type_._type_definition.fields

def type_django_model(type_):
    return getattr(type_, '_django_model', None)
