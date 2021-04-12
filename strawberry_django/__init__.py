from .fields import field, mutation
from .mutations.fields import mutations
from .mutations.auth import AuthMutation
from .queries.fields import queries
from .registers import TypeRegister
from . import filters
from .filters import filter
from .filters2 import filter_field, filter as filter2
from .resolvers import django_resolver
from .type import input, type
from .type2 import auto

from .type2 import type, input
from .fields2 import field
