from django.db import models
from strawberry.arguments import StrawberryArgument, UNSET, convert_arguments, is_unset
from strawberry.field import StrawberryField
import strawberry
from .. import utils
from ..resolvers import django_resolver
from ..filters import StrawberryDjangoFieldFilters
from ..ordering import StrawberryDjangoFieldOrdering

from typing import List, Optional



class StrawberryDjangoFieldBase:
    def get_queryset(self, queryset, info, **kwargs):
        return queryset

class StrawberryDjangoField(
        StrawberryDjangoFieldOrdering,
        StrawberryDjangoFieldFilters,
        StrawberryDjangoFieldBase,
        StrawberryField):

    def __init__(self, django_name=None, graphql_name=None, python_name=None, **kwargs):
        self.django_name = django_name
        super().__init__(graphql_name=graphql_name, python_name=python_name, **kwargs)

    @property
    def django_model(self):
        type_ = self.type or self.child.type
        return getattr(type_, '_django_model', None)

    def get_result(self, kwargs, info, source):
        if self.base_resolver:
            args, kwargs = self._get_arguments(kwargs, source=source, info=info)
            return self.base_resolver(*args, **kwargs)
        return self.get_django_result(kwargs, info, source)

    @django_resolver
    def get_django_result(self, kwargs, info, source):
        kwargs = convert_arguments(kwargs, self.arguments)
        return self.resolver(info=info, source=source, **kwargs)

    def resolver(self, info, source, **kwargs):
        if source is None:
            #TODO: would there be better and safer way to detect root?
            # root query object
            result = self.django_model.objects.all()

        else:
            # relation model field
            result = getattr(source, self.django_name or self.python_name)
            if isinstance(result, models.manager.Manager):
                result = result.all()

        if isinstance(result, models.QuerySet):
            result = self.get_queryset(queryset=result, info=info, **kwargs)

            if not self.is_list:
                result = result.get()

        return result


def field(resolver=None, *, name=None, filters=None, field_name=None, default=UNSET, **kwargs):
    field_ = StrawberryDjangoField(
        python_name=None,
        graphql_name=name,
        type_=None,
        filters=filters,
        django_name=field_name,
        default_value=default,
        **kwargs
    )
    if resolver:
        resolver = django_resolver(resolver)
        return field_(resolver)
    return field_
