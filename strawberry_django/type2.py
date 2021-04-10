import strawberry
from strawberry.field import StrawberryField
from strawberry.arguments import UNSET, is_unset
from .types import field_type_map, is_optional
from django.db import models
from typing import Optional
import django

from .fields2 import DjangoField


class auto:
    pass


def field2(resolver=None, *, name=None, **kwargs):
    field_ = DjangoField(
        python_name=None,
        graphql_name=name,
        type_=None,
        **kwargs
    )
    if resolver:
        return field_(resolver)
    return field_

def iter_fields(cls):
    field_names = list(cls.__annotations__.keys())
    field_names += [f for f in dir(cls) if f not in field_names and not f.startswith('_')]
    for field_name in field_names:
        field_value = getattr(cls, field_name, UNSET)
        field_type = None
        if isinstance(field_value, StrawberryField):
            field_type = field_value.type
        if field_type is None:
            field_type = cls.__annotations__.get(field_name, auto)
        yield (field_name, field_type, field_value)

def resolve_model_field_type(model, field_name):
    model_field = model._meta.get_field(field_name)
    model_field_type = type(model_field)
    field_type = field_type_map[model_field_type]
    return field_type

def is_field_optional(model, field_name, is_input, partial):
    if not model:
        return False
    try:
        model_field = model._meta.get_field(field_name)
    except django.core.exceptions.FieldDoesNotExist:
        return False
    return is_optional(model_field, is_input, partial)

def process_type(cls, model, kwargs):
    is_input = kwargs.get('is_input', False)
    partial = kwargs.pop('partial', False)

    if not hasattr(cls, '__annotations__'):
        cls.__annotations__ = {}

    annotations = {}
    for field_name, field_type, field_value in iter_fields(cls):
        if field_type is auto:
            field_type = resolve_model_field_type(model, field_name)
            #annotations[field_name] = field_type

        if is_field_optional(model, field_name, is_input, partial):
            field_type = Optional[field_type]

        if is_unset(field_value):
            field_ = DjangoField(
                python_name=None,
                graphql_name=None,
                type_=field_type
            )
            setattr(cls, field_name, field_)

        annotations[field_name] = field_type

    cls.__annotations__.update(annotations)
    cls._django_model = model

    return strawberry.type(cls, **kwargs)

def type2(cls_or_model, **kwargs):
    if not is_django_model(cls_or_model):
        cls = cls_or_model
        return process_type(cls, None, kwargs)

    def wrapper(cls):
        model = cls_or_model
        return process_type(cls, model, kwargs)

    return wrapper

def is_django_type(obj):
    return hasattr(obj, '_django_model')

def is_django_model(obj):
    return isinstance(obj, models.base.ModelBase)
