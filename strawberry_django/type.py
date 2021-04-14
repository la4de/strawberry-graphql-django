import strawberry
from strawberry.arguments import UNSET, is_unset
from .fields.utils import iter_class_fields
from .fields.types import field_type_map, is_auto, is_optional
from django.db import models
from typing import Optional
import django

from .fields.field import DjangoField
from . import utils

_type = type

def resolve_model_field_type(model, field_name):
    model_field = model._meta.get_field(field_name)
    model_field_type = _type(model_field)
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
    for field_name, field_type, field_value in iter_class_fields(cls):
        if is_auto(field_type):
            field_type = resolve_model_field_type(model, field_name)

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

    if '__annotations__' not in cls.__dict__:
        # strawberry reads annotations from __dict__
        cls.__annotations__ = annotations
    else:
        cls.__annotations__.update(annotations)

    cls._django_model = model
    cls._partial = partial

    return strawberry.type(cls, **kwargs)

def type(cls_or_model, **kwargs):
    if 'fields' in kwargs or 'types' in kwargs:
        from .legacy.type import type as type_legacy
        return type_legacy(model=cls_or_model, **kwargs)

    if not utils.is_django_model(cls_or_model):
        cls = cls_or_model
        return process_type(cls, None, kwargs)

    def wrapper(cls):
        model = cls_or_model
        return process_type(cls, model, kwargs)

    return wrapper

def input(cls_or_model, *, partial=False, **kwargs):
    return type(cls_or_model, partial=partial, is_input=True, **kwargs)
