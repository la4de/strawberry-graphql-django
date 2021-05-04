import enum
import strawberry
import strawberry_django
from . import utils
from typing import Optional


@strawberry.enum
class Ordering(enum.Enum):
    asc = 'asc'
    desc = 'desc'


def generate_order_by_args(order_by, prefix=''):
    args = []
    for field in strawberry_django.fields(order_by):
        ordering = getattr(order_by, field.name, utils.UNSET)
        if utils.is_unset(ordering):
            continue
        if ordering == Ordering.asc:
            args.append(f'{prefix}{field.name}')
        elif ordering == Ordering.desc:
            args.append(f'-{prefix}{field.name}')
        else:
            prefix = f'{prefix}{field.name}__'
            subargs = generate_order_by_args(ordering, prefix=prefix)
            args.extend(subargs)
    return args

def order_by(model):
    def wrapper(cls):
        for name, type_ in cls.__annotations__.items():
            if strawberry_django.is_auto(type_):
                type_ = Ordering
            cls.__annotations__[name] = Optional[type_]
            setattr(cls, name, utils.UNSET)
        return strawberry.input(cls)
    return wrapper


def apply(order_by, queryset):
    args = generate_order_by_args(order_by)
    if not args:
        return queryset
    return queryset.order_by(*args)
