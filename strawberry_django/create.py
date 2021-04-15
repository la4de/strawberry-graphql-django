from strawberry.field import StrawberryField
from strawberry.arguments import StrawberryArgument, UNSET
from typing import List
from asgiref.sync import sync_to_async

from django.db import transaction

class DjangoMutation(StrawberryField):
    def __init__(self, input_type, many):
        self.django_model = input_type._django_model
        self.input_type = input_type
        self.many = many
        super().__init__(
            python_name=None,
            graphql_name=None,
            type_=None,
        )

    @property
    def arguments(self):
        if not self.many:
            arg = StrawberryArgument(
                python_name = 'data',
                graphql_name = 'data',
                type_ = self.input_type,
            )
        else:
            arg = StrawberryArgument(
                python_name = 'data',
                graphql_name = 'data',
                type_ = None,
                child = StrawberryArgument(graphql_name=None, python_name=None, type_=self.input_type),
                is_list = True,
            )
        return [
            arg
        ]

#from tests.types import FruitInput

class DjangoCreateMutation(DjangoMutation):
    def __init__(self, input_type, many):
        super().__init__(input_type, many)

    def create(self, data):
        instance = self.django_model(**data)
        instance.save()
        return instance

    @sync_to_async
    @transaction.atomic
    def get_result(self, kwargs, info, source):
        data = kwargs['data']
        if self.many:
            return [self.create(d) for d in data]
        else:
            return self.create(data)

class DjangoUpdateMutation(DjangoMutation):
    def __init__(self, input_type, many):
        super().__init__(input_type, many)

    @sync_to_async
    @transaction.atomic
    def get_result(self, kwargs, info, source):
        data = kwargs['data']
        if self.many:
            return [self.create(d) for d in data]
        else:
            return self.create(data)
