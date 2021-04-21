from strawberry.arguments import UNSET, is_unset
from strawberry.field import StrawberryField
from .types import auto

def get_annotations(cls):
    annotations = {}
    for c in reversed(cls.__mro__):
        if '__annotations__' in c.__dict__:
            annotations.update(c.__annotations__)
    return annotations

def iter_class_fields(cls):
    annotations = get_annotations(cls)
    python_names = list(annotations.keys())
    python_names += [f for f in dir(cls) if f not in python_names and not f.startswith('_')]
    for python_name in python_names:
        field_value = getattr(cls, python_name, UNSET)
        field_type = None
        if isinstance(field_value, StrawberryField):
            field_type = field_value.type
        if field_type is None:
            field_type = annotations.get(python_name, auto)
        yield (python_name, field_type, field_value)
