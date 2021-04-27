from strawberry.arguments import UNSET
from ..legacy.mutations.fields import mutations as mutations_legacy
from .fields import DjangoCreateMutation, DjangoUpdateMutation, DjangoDeleteMutation

def mutations(*args, **kwargs):
    return mutations_legacy(*args, **kwargs)

def create(input_type=UNSET, *args, many=False, types=None, pre_save=None, post_save=None):
    if args or types:
        args = (input_type,) + args
        if many:
            #TODO: check error
            raise Exception("'many' parameter cannot be used together with 'types'")
        return mutations_legacy.create(*args, types=types, pre_save=pre_save, post_save=post_save)
    return DjangoCreateMutation(input_type, many=many)

def update(input_type=UNSET, *args, many=False, types=None):
    if args or types:
        args = (input_type,) + args
        return mutations_legacy.update(*args, types=types)
    if many is False:
        raise NotImplementedError('many=False not implemented yet')
    return DjangoUpdateMutation(input_type)

def delete(*args, types=None, many=False):
    if args or types:
        return mutations_legacy.delete(*args, types=types)
    if many is False:
        raise NotImplementedError('many=False not implemented yet')
    return DjangoDeleteMutation()

mutations.create = create
mutations.update = update
mutations.delete = delete
