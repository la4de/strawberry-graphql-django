import strawberry
from typing import List
from .types import Fruit

@strawberry.type
class Query:
    fruits: List[Fruit]

schema = strawberry.Schema(query=Query)
