import strawberry
from .utils import generate_query
from typing import List

"""
def resolver():
    return Type('hello')

def resolver2():
    return [Type2('hello')]

@strawberry.type(default_resolver=resolver)
class Type:
    string: str

@strawberry.type(default_resolver=resolver)
class Type2:
    string: str

@strawberry.type
class Query:
    type: Type
    types: List[Type2]

def test_default_resolver():
    query = generate_query(Query)

    result = query('{ type { string } }')

    assert not result.errors
    assert result.data == { 'type': { 'string': 'hello' } }


def test_default_resolver_from_list():
    query = generate_query(Query)

    result = query('{ types { string } }')

    assert not result.errors
    assert result.data == { 'type': { 'string': 'hello' } }

"""
