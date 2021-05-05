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

    # annotated fields
    field_names = list(annotations.keys())
    for field_name in field_names:
        field_type = None
        field_value = getattr(cls, field_name, UNSET)
        if isinstance(field_value, StrawberryField):
            field_type = field_value.type
        if field_type is None:
            field_type = annotations[field_name]
        yield field_name, field_type, field_value

    # strawberry fields
    for field_name in dir(cls):
        if field_name in field_names:
            continue
        field_value = getattr(cls, field_name)
        if not isinstance(field_value, StrawberryField):
            continue
        field_type = field_value.type or auto
        yield field_name, field_type, field_value


def fields(cls):
    return cls._type_definition.fields
