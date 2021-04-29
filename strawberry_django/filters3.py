from strawberry.arguments import UNSET, is_unset
from typing import Generic, List, Optional, TypeVar, Union
import dataclasses
import strawberry

from .utils import is_strawberry_type, type_fields, is_django_field

T= TypeVar("T")

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
    startswith: Optional[T] = UNSET
    i_startswith: Optional[T] = UNSET
    endswith: Optional[T] = UNSET
    i_endswith: Optional[T] = UNSET
    range: Optional[List[T]] = UNSET
    is_null: Optional[bool] = UNSET
    regex: Optional[str] = UNSET
    i_regex: Optional[str] = UNSET

lookup_name_conversion_map = {
    'i_exact': 'iexact',
    'i_contains': 'icontains',
    'in_list': 'in',
    'i_startswith': 'istartswith',
    'i_endswith': 'iendswith',
    'is_null': 'isnull',
    'i_regex': 'iregex',
}

def from_type(type_, _depth=3):
    if _depth == 0:
        return

    fields = []
    for field in type_fields(type_):
        if not is_django_field(field):
            continue

        field_name = field.django_name
        if not field_name:
            continue

        field_type = field.type or field.child.type
        if field_type is bool:
            pass

        elif is_strawberry_type(field_type):
            field_type = from_type(field_type, _depth - 1)
            if field_type is None:
                continue

        else:
            field_type = FilterLookup[field_type]

        fields.append((field_name, field_type))

    if not fields:
        return

    filter_name = f'{type_.__name__}FilterType'
    cls = dataclasses.make_dataclass(filter_name, fields)
    return filter(cls)

from .fields.utils import iter_class_fields

def _process_filter(cls, lookups):
    for key, value in cls.__annotations__.items():
        cls.__annotations__[key] = Optional[value]
        setattr(cls, key, getattr(cls, key, UNSET))
    return strawberry.input(cls)

def filter(cls, *, lookups=False):
    return _process_filter(cls, lookups)

def build_filter_kwargs(filters):
    kwargs = {}
    for key, value in vars(filters).items():
        if is_unset(value):
            continue
        if key in lookup_name_conversion_map:
            key = lookup_name_conversion_map[key]
        if hasattr(value, '_type_definition'):
            for key2, value2 in build_filter_kwargs(value).items():
                kwargs[f'{key}__{key2}'] = value2
        else:
            kwargs[key] = value
    return kwargs

def filters_apply(filters, queryset):
    kwargs = build_filter_kwargs(filters)
    queryset = queryset.filter(**kwargs)
    return queryset
