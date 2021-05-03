from . import filters
from .fields import auto, field
from .fields.types import (
    DjangoFileType, DjangoImageType, DjangoModelType,
    OneToOneInput, OneToManyInput, ManyToOneInput, ManyToManyInput,
)
from .fields.utils import fields
from .filters import filter, FilterLookup
from .mutations.mutations import mutations
from .resolvers import django_resolver
from .type import type, input

# deprecated functions
#from .legacy.fields import field, mutation
from .legacy.mutations.auth import AuthMutation
from .legacy.queries.fields import queries
from .legacy.registers import TypeRegister
