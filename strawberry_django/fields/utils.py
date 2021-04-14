from strawberry.arguments import UNSET, is_unset
from strawberry.field import StrawberryField
from .types import auto

def iter_class_fields(cls):
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
