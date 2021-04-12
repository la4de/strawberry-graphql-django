import strawberry_django
from django.db import models
from strawberry.field import StrawberryField
from strawberry.arguments import StrawberryArgument, UNSET
from asgiref.sync import sync_to_async
from . import utils

import dataclasses
from typing import Any, List, Optional

@dataclasses.dataclass
class Result:
    value: Any = None

class DjangoFilters:
    def __init__(self, filters=None, django_name=None, *args, **kwargs):
        self.filters = filters
        self.django_name = django_name
        super().__init__(*args, **kwargs)

    @property
    def arguments(self) -> List[StrawberryArgument]:
        arguments = super().arguments
        if self.filters:
            arg = StrawberryArgument(
                type_=self.filters,
                python_name="filters",
                graphql_name="filters",
                default_value=UNSET,
                description=None,
                origin=None,
            )
            arguments += [arg]
        return arguments

    def apply_filter(self, kwargs, source, info, queryset):
        if self.filters:
            filters = self.filters(**kwargs.get('filters'))
            queryset = strawberry_django.filters.apply(filters, queryset)
        return queryset


class DjangoField(DjangoFilters, StrawberryField):
    def __init__(self, *args, **kwargs):
        self.hooks = kwargs.pop('hooks', [])
        if isinstance(self.hooks, tuple):
            self.hooks = list(self.hooks)
        elif not isinstance(self.hooks, list):
            self.hooks = [self.hooks]
        super().__init__(*args, **kwargs)

    def get_result(self, kwargs, source, info):
        result = Result()
        sync_resolver = None

        if self.base_resolver:
            if not self.base_resolver.is_async:
                sync_resolver = super().get_result

        else:
            if self.is_django_type:
                sync_resolver = self.django_resolver

        if sync_resolver:
            if utils.is_async():
                @sync_to_async(thread_sensitive=True)
                def resolve():
                    result.value = sync_resolver(kwargs, source, info)
                    self.call_hooks(root=source, info=info, result=result)
                    if isinstance(result.value, models.QuerySet):
                        # force query execution
                        result.value = list(result.value)
                    return result.value
                return resolve()
            else:
                result.value = sync_resolver(kwargs, source, info)
                self.call_hooks(root=source, info=info, result=result)
                return result.value

        if self.django_name:
            result.value = getattr(source, self.django_name)
        else:
            result.value = super().get_result(kwargs, source, info)
        self.call_hooks(root=source, info=info, result=result)
        return result.value


    def django_resolver(self, kwargs, source, info):

        if source is None:
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


    @property
    def django_model(self):
        return self.django_type._django_model

    @property
    def django_type(self):
        return self.type or self.child.type

    @property
    def is_django_type(self):
        return is_django_type(self.django_type)

    def hook(self, hook):
        self.hooks.append(hook)

    def call_hooks(self, *args, **kwargs):
        for hook in self.hooks:
            hook(*args, **kwargs)

def field(resolver=None, *, name=None, filters=None, field_name=None, **kwargs):
    field_ = DjangoField(
        python_name=None,
        graphql_name=name,
        type_=None,
        filters=filters,
        django_name=field_name,
        **kwargs
    )
    if resolver:
        return field_(resolver)
    return field_



#TODO: move to common place
def is_django_type(obj):
    return hasattr(obj, '_django_model')
