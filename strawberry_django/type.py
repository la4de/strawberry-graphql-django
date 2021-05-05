import dataclasses
import django
import strawberry
from django.db import models
from strawberry.arguments import UNSET, is_unset
from typing import Optional

from .fields.field import StrawberryField, StrawberryDjangoField
from .fields.types import (
    auto, is_auto, is_optional,
    get_model_field, resolve_model_field_type, resolve_model_field_name,
)
from .fields.utils import iter_class_fields
from . import utils

_type = type


def resolve_django_name(model, field_name, field_value, is_input, is_filter):
    django_name = getattr(field_value, 'django_name', field_name)
    try:
        model_field = get_model_field(model, django_name)
        django_name = resolve_model_field_name(model_field, is_input, is_filter)
    except django.core.exceptions.FieldDoesNotExist:
        pass
    return django_name


def is_field_type_inherited_from_different_object_type(cls, field_name, is_input, is_filter):
    if field_name in cls.__dict__.get('__annotations__', {}):
        return False
    # TODO: optimize and simplify
    for c in reversed(cls.__mro__):
        if field_name not in c.__dict__.get('__annotations__', {}):
            continue
        if not utils.is_strawberry_type(c):
            return False
        if c._type_definition.is_input != is_input:
            return True
        if c._is_filter != is_filter:
            return True
        return False
    return False


def resolve_field_type(cls, model, field_name, django_name, field_type, is_input, partial, is_filter):
    model_field = None

    try:
        model_field = get_model_field(model, django_name)
    except django.core.exceptions.FieldDoesNotExist:
        if is_auto(field_type):
            raise

    is_relation = getattr(model_field, 'is_relation', False)

    if is_relation:
        if is_field_type_inherited_from_different_object_type(cls, field_name, is_input, is_filter):
            field_type = auto
        if is_filter and is_auto(field_type):
            from . import filters
            field_type = filters.DjangoModelFilterInput

    if is_auto(field_type):
        field_type = resolve_model_field_type(model_field, is_input)

    if is_filter == 'lookups':
        if model_field and not model_field.is_relation:
            from . import filters
            if field_type not in (bool, filters.DjangoModelFilterInput):
                field_type = filters.FilterLookup[field_type]

    if is_optional(model_field, is_input, partial):
        field_type = Optional[field_type]

    return field_type


def get_fields(cls, model, is_input, partial, is_filter):
    fields = []
    for field_name, field_type, field_value in iter_class_fields(cls):
        django_name = resolve_django_name(model, field_name, field_value, is_input, is_filter)
        field_type = resolve_field_type(cls, model, field_name, django_name, field_type, is_input, partial, is_filter)
        if isinstance(field_value, StrawberryField):
            field = field_value
        else:
            field = StrawberryDjangoField(
                default_value=field_value,
                django_name=django_name,
                type_=field_type
            )
        if is_input:
            if field.default is dataclasses.MISSING:
                #TODO: could strawberry support UNSET?
                field.default = UNSET
                field.default_value = UNSET
        field.origin_value = field_value
        fields.append((field_name, field_type, field))
    return fields

def process_type(cls, model, **kwargs):
    is_input = kwargs.get('is_input', False)
    partial = kwargs.pop('partial', False)
    is_filter = kwargs.pop('is_filter', False)

    fields = get_fields(cls, model, is_input, partial, is_filter)

    # store original annotations for further use
    annotations = cls.__dict__.get('__annotations__', {})

    # update annotations and fields
    cls.__annotations__ = {}
    for field_name, field_type, field in fields:
        cls.__annotations__[field_name] = field_type
        setattr(cls, field_name, field)

    strawberry.type(cls, **kwargs)

    cls.__annotations__ = annotations
    cls._django_model = model
    cls._partial = partial
    cls._is_filter = bool(is_filter)

    return cls
    

def type(model, **kwargs):
    if 'fields' in kwargs or 'types' in kwargs:
        from .legacy.type import type as type_legacy
        return type_legacy(model, **kwargs)

    def wrapper(cls):
        return process_type(cls, model, **kwargs)
    return wrapper


def input(model, *, partial=False, **kwargs):
    return type(model, partial=partial, is_input=True, **kwargs)
