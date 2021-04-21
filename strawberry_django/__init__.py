from . import filters
from .fields import auto, field
from .fields.types import (
    DjangoFileType, DjangoImageType,
    OneToOneInput, OneToManyInput, ManyToOneInput, ManyToManyInput,
)
from .filters import filter
from .filters2 import filter_field, filter as filter2
from .mutations.mutations import mutations
from .resolvers import django_resolver
from .type import type, input

# deprecated functions
#from .legacy.fields import field, mutation
from .legacy.mutations.auth import AuthMutation
from .legacy.queries.fields import queries
from .legacy.registers import TypeRegister
