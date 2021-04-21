from django.db.models import fields
from typing import get_origin, List, Optional
import strawberry
from strawberry.arguments import UNSET
import datetime, decimal, uuid

class auto:
    pass

@strawberry.type
class DjangoFileType:
    name: str
    path: str
    size: int
    url: str

@strawberry.type
class DjangoImageType(DjangoFileType):
    width: int
    height: int

@strawberry.input
class OneToOneInput:
    set: Optional[strawberry.ID]

@strawberry.input
class OneToManyInput:
    set: Optional[strawberry.ID]

@strawberry.input
class ManyToOneInput:
    add: Optional[List[strawberry.ID]] = UNSET
    remove: Optional[List[strawberry.ID]] = UNSET
    set: Optional[List[strawberry.ID]] = UNSET

@strawberry.input
class ManyToManyInput:
    add: Optional[List[strawberry.ID]] = UNSET
    remove: Optional[List[strawberry.ID]] = UNSET
    set: Optional[List[strawberry.ID]] = UNSET

@strawberry.input
class ManyToManyInput:
    add: Optional[List[strawberry.ID]] = UNSET
    remove: Optional[List[strawberry.ID]] = UNSET
    set: Optional[List[strawberry.ID]] = UNSET

field_type_map = {
    fields.AutoField: strawberry.ID,
    fields.BigAutoField: strawberry.ID,
    fields.BigIntegerField: int,
    fields.BooleanField: bool,
    fields.CharField: str,
    fields.DateField: datetime.date,
    fields.DateTimeField: datetime.datetime,
    fields.DecimalField: decimal.Decimal,
    fields.EmailField: str,
    fields.files.FileField: DjangoFileType,
    fields.FilePathField: str,
    fields.FloatField: float,
    fields.files.ImageField: DjangoImageType,
    fields.GenericIPAddressField: str,
    fields.IntegerField: int,
    fields.json.JSONField: NotImplemented,
    fields.NullBooleanField: Optional[bool],
    fields.PositiveBigIntegerField: int,
    fields.PositiveIntegerField: int,
    fields.PositiveSmallIntegerField: int,
    fields.SlugField: str,
    fields.SmallAutoField: strawberry.ID,
    fields.SmallIntegerField: int,
    fields.TextField: str,
    fields.TimeField: datetime.time,
    fields.URLField: str,
    fields.UUIDField: uuid.UUID,
}

input_field_type_map = {
    fields.files.FileField: NotImplemented,
    fields.files.ImageField: NotImplemented,
    fields.related.ForeignKey: OneToManyInput,
    fields.reverse_related.ManyToOneRel: ManyToOneInput,
    fields.related.OneToOneField: OneToOneInput,
    fields.reverse_related.OneToOneRel: OneToOneInput,
    fields.related.ManyToManyField: ManyToManyInput,
    fields.reverse_related.ManyToManyRel: ManyToManyInput,
}

def resolve_model_field_type(model_field, is_input):
    model_field_type = type(model_field)
    field_type = None
    if is_input:
        field_type = input_field_type_map.get(model_field_type, None)
    if field_type is None:
        field_type = field_type_map[model_field_type]
    if field_type is NotImplemented:
        raise NotImplementedError("GraphQL type for model field '{model_field}' has not been implemented yet")
    return field_type

from django.db.models.fields.reverse_related import ForeignObjectRel, ManyToOneRel

def resolve_model_field_name(model_field, is_input):
    if isinstance(model_field, (ForeignObjectRel, ManyToOneRel)):
        return model_field.get_accessor_name()
    if is_input:
        return model_field.attname
    else:
        return model_field.name


def is_auto(type_):
    return type_ is auto

def is_optional(field, is_input, partial):
    if is_input:
        if isinstance(field, fields.AutoField):
            return True
        if isinstance(field, fields.reverse_related.OneToOneRel):
            return field.null
        if field.many_to_many or field.one_to_many:
            return True
        has_default = field.default != fields.NOT_PROVIDED
        if field.blank or partial or has_default:
            return True
    if field.null:
        return True
    return False
