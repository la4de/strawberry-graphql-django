from inspect import iscoroutine
from django.db import models
from strawberry.field import StrawberryField
from asgiref.sync import sync_to_async
from . import utils

import dataclasses
from typing import Any

@dataclasses.dataclass
class Result:
    value: Any = None

class DjangoField(StrawberryField):
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
            if not iscoroutine(self.base_resolver):
                sync_resolver = self.base_resolver

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

        result.value = super().get_result(kwargs, source, info)
        self.call_hooks(root=source, info=info, result=result)
        return result.value


    def django_resolver(self, kwargs, source, info):

        if source is None:
            # root query object
            result = self.django_model.objects.all()

        else:
            # relation model field
            result = getattr(source, self.python_name)
            if isinstance(result, models.manager.Manager):
                result = result.all()

        if isinstance(result, models.QuerySet):
            # TODO: add filtering here!
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



#TODO: move to common place
def is_django_type(obj):
    return hasattr(obj, '_django_model')
