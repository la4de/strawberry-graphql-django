from django.db.models import fields
from typing import get_origin, List, Optional
import strawberry
import datetime, decimal, uuid

class auto:
    pass

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
    #TODO: fields.FieldFile
    fields.FilePathField: str,
    fields.FloatField: float,
    #TODO: fields.ImageField
    fields.GenericIPAddressField: str,
    fields.IntegerField: int,
    #TODO: fields.JSONField
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

def is_auto(type_):
    return type_ is auto

def is_optional(field, is_input, partial):
    if is_input:
        if isinstance(field, fields.AutoField):
            return True
        if field.many_to_many or field.one_to_many:
            return True
        has_default = field.default != fields.NOT_PROVIDED
        if field.blank or partial or has_default:
            return True
    if field.null:
        return True
    return False

