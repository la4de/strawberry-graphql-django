from typing import Generic, List, Optional, TypeVar, Union
import strawberry
from strawberry.arguments import UNSET

T= TypeVar("T")

@strawberry.input
class FilterLookup(Generic[T]):
    exact: Optional[T]
    iexact: Optional[T]
    contains: Optional[T]
    icontains: Optional[T]
    in_list: Optional[List[T]]
    gt: Optional[T]
    gte: Optional[T]
    lt: Optional[T]
    lte: Optional[T]
    startswith: Optional[T]
    istartswith: Optional[T]
    endswith: Optional[T]
    iendswith: Optional[T]
    range: Optional[List[T]]
    isnull: Optional[bool]
    regex: Optional[str]
    iregex: Optional[str]

lookup_name_conversion_map = {
    'inList': 'in',
}

def filter(cls):
    for key, value in cls.__annotations__.items():
        cls.__annotations__[key] = Optional[value]
        setattr(cls, key, getattr(cls, key, UNSET))
    return strawberry.input(cls)

def build_filter_kwargs(filters):
    kwargs = {}
    print(filters)
    for key, value in filters.items():
        if key in lookup_name_conversion_map:
            key = lookup_name_conversion_map[key]
        if isinstance(value, dict):
            for key2, value2 in build_filter_kwargs(value).items():
                kwargs[f'{key}__{key2}'] = value2
        else:
            kwargs[key] = value
    return kwargs

def filters_apply(filters, queryset):
    kwargs = build_filter_kwargs(filters)
    queryset = queryset.filter(**kwargs)
    return queryset
