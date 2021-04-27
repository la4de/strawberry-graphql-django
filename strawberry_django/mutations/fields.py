from strawberry.field import StrawberryField
from strawberry.arguments import StrawberryArgument, UNSET, convert_arguments, is_unset
from typing import List
from asgiref.sync import sync_to_async
from ..resolvers import django_resolver
from .. import utils, types
from ..fields.types import OneToOneInput, OneToManyInput, ManyToOneInput, ManyToManyInput

from django.db import transaction

class DjangoMutation(StrawberryField):
    def __init__(self, input_type=None, many=False):
        self.input_type = input_type
        self.many = many
        super().__init__(
            python_name=None,
            graphql_name=None,
            type_=None,
        )

    def post_init(self):
        type_ = self.type or self.child.type
        if is_unset(self.input_type):
            type_ = self.type or self.child.type
            self.input_type = types.from_type(type_, is_input=True)
        elif self.input_type:
            assert type_._django_model == self.input_type._django_model, ('Input'
                ' and output types should be generated from the same Django model')
        self.django_model = type_._django_model

    @property
    def arguments(self):
        args = []
        if self.input_type:
            args.append(get_argument('data', self.input_type, self.many))
        return args

    @django_resolver
    def get_result(self, kwargs, info, source):
        kwargs = convert_arguments(kwargs, self.arguments)
        return self.resolver(info=info, source=source, **kwargs)

    def get_wrapped_resolver(self):
        self.post_init()
        return super().get_wrapped_resolver()


class DjangoCreateMutation(DjangoMutation):
    def __init__(self, input_type, many):
        super().__init__(input_type, many)

    def create(self, data):
        input_data = get_input_data(self.django_model, data)
        instance = self.django_model.objects.create(**input_data)
        update_m2m([instance], data)
        return instance

    @transaction.atomic
    def resolver(self, info, source, data):
        if self.many:
            return [self.create(d) for d in data]
        else:
            return self.create(data)


class DjangoUpdateMutation(DjangoMutation):
    def __init__(self, input_type):
        super().__init__(input_type)

    @transaction.atomic
    def resolver(self, info, source, data):
        queryset = self.django_model.objects.all()
        #TODO: filter here
        input_data = get_input_data(self.django_model, data)
        queryset.update(**input_data)
        update_m2m(queryset, data)
        return queryset


class DjangoDeleteMutation(DjangoMutation):
    def __init__(self):
        super().__init__()

    @transaction.atomic
    def resolver(self, info, source):
        queryset = self.django_model.objects.all()
        #TODO: filter here
        instances = list(queryset)
        queryset.delete()
        return instances


def get_argument(name, type_, is_list=False):
    if is_list:
        return StrawberryArgument(
            python_name = name,
            graphql_name = name,
            type_ = None,
            child = StrawberryArgument(graphql_name=None, python_name=None, type_=type_),
            is_list = True,
        )
    else:
        return StrawberryArgument(
            python_name = name,
            graphql_name = name,
            type_ = type_,
        )


def get_input_data(model, data):
    input_type = type(data)
    input_data = {}
    m2m_data = {}
    for field in input_type._type_definition.fields:
        value = getattr(data, field.name)
        if isinstance(value, (ManyToOneInput, ManyToManyInput)):
            continue
        if is_unset(value):
            continue
        if isinstance(value, OneToManyInput):
            value = value.set
        input_data[field.django_name] = value
    return input_data


def update_m2m(queryset, data):
    #TODO: optimize
    for field_name, field_value in vars(data).items():
        if not isinstance(field_value, (ManyToOneInput, ManyToManyInput)):
            continue

        for instance in queryset:
            f = getattr(instance, field_name)
            if not is_unset(field_value.set):
                if field_value.add:
                    raise ValueError("'add' cannot be used together with 'set'")
                if field_value.remove:
                    raise ValueError("'remove' cannot be used together with 'set'")

                values = field_value.set
                if isinstance(field_value, ManyToOneInput):
                    values = [f.model.objects.get(pk=pk) for pk in values]
                if values:
                    f.set(values)
                else:
                    f.clear()
            else:
                if field_value.add:
                    values = field_value.add
                    if isinstance(field_value, ManyToOneInput):
                        values = [f.model.objects.get(pk=pk) for pk in values]
                    f.add(*values)
                if field_value.remove:
                    values = field_value.remove
                    if isinstance(field_value, ManyToOneInput):
                        values = [f.model.objects.get(pk=pk) for pk in values]
                    f.remove(*values)
