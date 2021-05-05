import enum
import strawberry
import strawberry_django
from strawberry.arguments import UNSET, is_unset, StrawberryArgument
from typing import Optional, List

from .arguments import argument
from . import utils


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
    if utils.is_unset(order_by) or order_by is None:
        return queryset
    args = generate_order_by_args(order_by)
    if not args:
        return queryset
    return queryset.order_by(*args)


class StrawberryDjangoFieldOrdering:
    def __init__(self, order_by=None, **kwargs):
        self.order_by = order_by
        super().__init__(**kwargs)

    @property
    def arguments(self) -> List[StrawberryArgument]:
        arguments = []
        if not self.base_resolver:
            if self.order_by:
                arguments.append(
                    argument('order_by', self.order_by)
                )
        return super().arguments + arguments

    def get_queryset(self, queryset, info, order_by=UNSET, **kwargs):
        queryset = apply(order_by, queryset)
        return super().get_queryset(queryset, info, **kwargs)
