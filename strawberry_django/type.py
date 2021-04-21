import strawberry
from strawberry.arguments import UNSET, is_unset
from .fields.utils import iter_class_fields
from .fields.types import is_auto, is_optional, resolve_model_field_type, resolve_model_field_name
from django.db import models
from typing import Optional
import django

from .fields.field import DjangoField
from . import utils

def is_field_optional(model, django_name, is_input, partial):
    if not model:
        return False
    try:
        model_field = model._meta.get_field(django_name)
    except django.core.exceptions.FieldDoesNotExist:
        return False
    return is_optional(model_field, is_input, partial)

def process_type(cls, model, kwargs):
    is_input = kwargs.get('is_input', False)
    partial = kwargs.pop('partial', False)

    annotations = {}
    for python_name, field_type, field_value in iter_class_fields(cls):
        django_name = python_name
        if utils.is_django_field(field_value):
            if field_value.django_name:
                django_name = field_value.django_name

        if model:
            try:
                model_field = model._meta.get_field(django_name)
                django_name = resolve_model_field_name(model_field, is_input)
            except django.core.exceptions.FieldDoesNotExist:
                if is_auto(field_type):
                    raise

        if is_auto(field_type):
            if not model:
                raise TypeError("'auto' type cannot be used without 'model' attribute")

            #TODO: non editable fields
            #if is_input:
            #    if not field.editable:
            #        raise Exception()

            field_type = resolve_model_field_type(model_field, is_input)

        if is_field_optional(model, django_name, is_input, partial):
            field_type = Optional[field_type]

        if is_unset(field_value):
            field_value = DjangoField(
                django_name=django_name,
                python_name=None,
                graphql_name=None,
                type_=field_type
            )

            if is_input:
                #TODO: could strawberry support UNSET?
                field_value.default = UNSET
                field_value.default_value = UNSET

        annotations[python_name] = field_type
        setattr(cls, python_name, field_value)

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
