import strawberry
from strawberry.arguments import UNSET, is_unset
from .fields.utils import iter_class_fields
from .fields.types import auto, is_auto, is_optional, resolve_model_field_type, resolve_model_field_name
from django.db import models
from typing import Optional
import django

from .fields.field import StrawberryField, StrawberryDjangoField
from . import utils

_type = type


def resolve_django_name(model, field_name, field_value, is_input):
    django_name = getattr(field_value, 'django_name', field_name)
    try:
        model_field = model._meta.get_field(django_name)
        django_name = resolve_model_field_name(model_field, is_input)
    except django.core.exceptions.FieldDoesNotExist:
        pass
    return django_name


def resolve_field_type(model, django_name, field_type, is_input, partial):
    model_field = None

    try:
        model_field = model._meta.get_field(django_name)
    except django.core.exceptions.FieldDoesNotExist:
        if is_auto(field_type):
            raise

    if is_input:
        if model_field and model_field.is_relation:
            # TODO: we should overwrite only inherited type from output type
            field_type = auto

    if is_auto(field_type):
        field_type = resolve_model_field_type(model_field, is_input)

    if is_optional(model_field, is_input, partial):
        field_type = Optional[field_type]

    return field_type


def get_fields(cls, model, is_input, partial):
    fields = []
    for field_name, field_type, field_value in iter_class_fields(cls):
        django_name = resolve_django_name(model, field_name, field_value, is_input)
        field_type = resolve_field_type(model, django_name, field_type, is_input, partial)
        if isinstance(field_value, StrawberryField):
            field = field_value
        else:
            field = StrawberryDjangoField(
                default_value=field_value,
                django_name=django_name,
                graphql_name=field_name,
                python_name=field_name,
                type_=field_type
            )
            if is_input:
                #TODO: could strawberry support UNSET?
                field.default = UNSET
                field.default_value = UNSET
        fields.append((field_name, field_type, field))
    return fields

def process_type(cls, model, kwargs):
    is_input = kwargs.get('is_input', False)
    partial = kwargs.pop('partial', False)

    fields = get_fields(cls, model, is_input, partial)

    # store original annotations for further use
    if '__annotations__' in cls.__dict__:
        cls._orig_annotations = cls.__annotations__

    # update annotations and fields
    cls.__annotations__ = {}
    for field_name, field_type, field in fields:
        cls.__annotations__[field_name] = field_type
        setattr(cls, field_name, field)

    #cls._django_type_definition(model)
    cls._django_model = model
    cls._partial = partial

    return strawberry.type(cls, **kwargs)
    

def type(model, **kwargs):
    if 'fields' in kwargs or 'types' in kwargs:
        from .legacy.type import type as type_legacy
        return type_legacy(model, **kwargs)

    def wrapper(cls):
        return process_type(cls, model, kwargs)
    return wrapper


def input(model, *, partial=False, **kwargs):
    return type(model, partial=partial, is_input=True, **kwargs)
