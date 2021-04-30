from strawberry.arguments import UNSET, is_unset
from typing import Generic, List, Optional, TypeVar, Union
import dataclasses
import strawberry

from . import utils
from .fields import is_auto
from .type import process_type

T= TypeVar("T")

@strawberry.input
class DjangoModelFilterInput:
    pk: strawberry.ID

@strawberry.input
class FilterLookup(Generic[T]):
    exact: Optional[T] = UNSET
    i_exact: Optional[T] = UNSET
    contains: Optional[T] = UNSET
    i_contains: Optional[T] = UNSET
    in_list: Optional[List[T]] = UNSET
    gt: Optional[T] = UNSET
    gte: Optional[T] = UNSET
    lt: Optional[T] = UNSET
    lte: Optional[T] = UNSET
    starts_with: Optional[T] = UNSET
    i_starts_with: Optional[T] = UNSET
    ends_with: Optional[T] = UNSET
    i_ends_with: Optional[T] = UNSET
    range: Optional[List[T]] = UNSET
    is_null: Optional[bool] = UNSET
    regex: Optional[str] = UNSET
    i_regex: Optional[str] = UNSET

lookup_name_conversion_map = {
    'i_exact': 'iexact',
    'i_contains': 'icontains',
    'in_list': 'in',
    'starts_with': 'startswith',
    'i_starts_with': 'istartswith',
    'ends_with': 'endswith',
    'i_ends_with': 'iendswith',
    'is_null': 'isnull',
    'i_regex': 'iregex',
}

def filter(model, *, lookups=False):
    def wrapper(cls):
        is_filter = lookups and 'lookups' or True
        type_ = process_type(cls, model, is_input=True, partial=True, is_filter=is_filter)
        return type_
    return wrapper

def build_filter_kwargs(filters):
    kwargs = {}
    django_model = getattr(filters, '_django_model', None)
    for field_name, field_value in vars(filters).items():
        if is_unset(field_value):
            continue

        if django_model:
            if field_name not in django_model._meta._forward_fields_map:
                continue

        if field_name in lookup_name_conversion_map:
            field_name = lookup_name_conversion_map[field_name]
        if utils.is_strawberry_type(field_value):
            for subfield_name, subfield_value in build_filter_kwargs(field_value).items():
                kwargs[f'{field_name}__{subfield_name}'] = subfield_value
        else:
            kwargs[field_name] = field_value
    return kwargs

def filters_apply(filters, queryset):
    kwargs = build_filter_kwargs(filters)
    queryset = queryset.filter(**kwargs)
    filter_method = getattr(filters, 'filter', None)
    if filter_method:
        queryset = filter_method(queryset)
    return queryset
