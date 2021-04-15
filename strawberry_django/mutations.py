from .legacy.mutations.fields import mutations as mutations_legacy
from .create import DjangoCreateMutation

def mutations(*args, **kwargs):
    return mutations_legacy(*args, **kwargs)

def create(input_type, many=False):
    return DjangoCreateMutation(input_type, many=many)

def update(*args, **kwargs):
    return mutations_legacy.update(*args, **kwargs)

def delete(*args, **kwargs):
    return mutations_legacy.delete(*args, **kwargs)

def create_wrapper(input_type, *args, many=False, types=None, pre_save=None, post_save=None):
    if args or types:
        args = (input_type,) + args
        if many:
            #TODO: check error
            raise Exception("'many' parameter cannot be used together with 'types'")
        return mutations_legacy.create(*args, types=types, pre_save=pre_save, post_save=post_save)
    return create(input_type, many=many)

mutations.create = create_wrapper
mutations.update = update
mutations.delete = delete

#def create(*args, types=None):
