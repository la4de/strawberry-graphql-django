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


def resolve_django_name(model, field_name, field_value, is_input, is_filter):
    django_name = getattr(field_value, 'django_name', field_name)
    try:
        model_field = model._meta.get_field(django_name)
        django_name = resolve_model_field_name(model_field, is_input, is_filter)
    except django.core.exceptions.FieldDoesNotExist:
        pass
    return django_name


def is_field_type_inherited_from_different_object_type(cls, field_name, is_input, is_filter):
    # TODO: optimize and simplify
    for c in reversed(cls.__mro__):
        annotations = {}
        if '_orig_annotations' in c.__dict__:
            annotations = c._orig_annotations
        if field_name in annotations:
            if c._type_definition.is_input != is_input:
                return True
            if c._is_filter != is_filter:
                return True
            return False
    return False


def resolve_field_type(cls, model, field_name, django_name, field_type, is_input, partial, is_filter):
    model_field = None

    try:
        model_field = model._meta.get_field(django_name)
    except django.core.exceptions.FieldDoesNotExist:
        if is_auto(field_type):
            raise

    if model_field and model_field.is_relation:
        if is_field_type_inherited_from_different_object_type(cls, field_name, is_input, is_filter):
            field_type = auto

    if is_input:
        if model_field and model_field.is_relation:
            if is_filter:
                if is_auto(field_type):
                    from . import filters3 as filters
                    field_type = filters.DjangoModelFilterInput

    if is_auto(field_type):
        field_type = resolve_model_field_type(model_field, is_input)

    if is_filter == 'lookups':
        if model_field and not model_field.is_relation:
            from . import filters3 as filters
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
                #TODO: could strawberry support UNSET?
                field.default = UNSET
                field.default_value = UNSET
        fields.append((field_name, field_type, field))
    return fields

def process_type(cls, model, **kwargs):
    is_input = kwargs.get('is_input', False)
    partial = kwargs.pop('partial', False)
    is_filter = kwargs.pop('is_filter', False)

    fields = get_fields(cls, model, is_input, partial, is_filter)

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
    cls._is_filter = bool(is_filter)

    return strawberry.type(cls, **kwargs)
    

def type(model, **kwargs):
    if 'fields' in kwargs or 'types' in kwargs:
        from .legacy.type import type as type_legacy
        return type_legacy(model, **kwargs)

    def wrapper(cls):
        return process_type(cls, model, **kwargs)
    return wrapper


def input(model, *, partial=False, **kwargs):
    return type(model, partial=partial, is_input=True, **kwargs)
