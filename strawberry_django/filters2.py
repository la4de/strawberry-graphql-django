import dataclasses
import django_filters
import strawberry_django
from typing import List, Optional
from .type import auto

type_map = {
    bool: django_filters.BooleanFilter,
    str: django_filters.CharFilter,
    int: django_filters.NumberFilter,
}

def get_filterset_filter_type(field_type):
    return type_map[field_type]

@dataclasses.dataclass
class FilterField:
    lookups: Optional[List[str]] = None

def filter_field(lookups=None):
    return FilterField(lookups=lookups)

def iter_fields(filter_cls):
    annotations = getattr(filter_cls, '__annotations__', {})
    for field_name, field_type in annotations.items():
        yield (field_name, field_type, getattr(filter_cls, field_name, None))
    for field_name in dir(filter_cls):
        if field_name.startswith('__'):
            continue
        if field_name in annotations:
            continue
        yield (field_name, auto, getattr(filter_cls, field_name))

def convert_to_filterset(model_, filter_cls):
    meta_fields = {}
    attrs = {}
    for field_name, field_type, field in iter_fields(filter_cls):
        if field_type is not auto:
            filter_type = get_filterset_filter_type(field_type)
        lookups = None
        field = getattr(filter_cls, field_name, None)
        if field is not None:
            if field.lookups:
                lookups = field.lookups
        meta_fields[field_name] = lookups or ['exact']

    class Meta:
        model = model_
        fields = meta_fields
    attrs['Meta'] = Meta

    filterset_cls = type(filter_cls.__name__, (django_filters.FilterSet,), attrs)

    return strawberry_django.filter(filterset_cls)

def filter(model):
    def wrapper(filter_cls):
        return convert_to_filterset(model, filter_cls)
    return wrapper
