from django.db import models
from strawberry.arguments import StrawberryArgument, UNSET, convert_arguments, is_unset
from strawberry.field import StrawberryField
from strawberry.types.types import undefined
import strawberry
from .. import utils
from ..resolvers import django_resolver

from typing import List, Optional

def argument(name, type_, is_optional=False, default_value=undefined):
    return StrawberryArgument(
        default_value=default_value,
        description=None,
        graphql_name=name,
        is_optional=is_optional,
        origin=None,
        python_name=name,
        type_=type_,
    )


class StrawberryDjangoFieldFilters:
    def __init__(self, filters=None, *args, **kwargs):
        self.filters = filters
        super().__init__(*args, **kwargs)

    @property
    def arguments(self) -> List[StrawberryArgument]:
        arguments = super().arguments

        if not self.base_resolver:
            if not self.is_list and self.django_model:
                arguments += [
                    argument('pk', strawberry.ID, is_optional=True)
                ]

            django_filters = self.django_filters
            if django_filters:
                arguments += [
                    argument('filters', django_filters, is_optional=True)
                ]

        return arguments

    @property
    def django_filters(self):
        if self.base_resolver:
            return
        return self.filters

    def apply_filter(self, kwargs, source, info, queryset):
        pk = kwargs.get('pk', UNSET)
        if not is_unset(pk):
            queryset = queryset.filter(pk=pk)

        filters = kwargs.get('filters', UNSET)
        if not is_unset(filters):
            from ..filters3 import filters_apply
            queryset = filters_apply(filters, queryset)

        return queryset


class StrawberryDjangoField(
        StrawberryDjangoFieldFilters,
        StrawberryField):

    def __init__(self, django_name=None, graphql_name=None, python_name=None, **kwargs):
        super().__init__(graphql_name=graphql_name, python_name=python_name, **kwargs)
        self.django_name = django_name

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
            result = self.apply_filter(kwargs, source, info, result)

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
