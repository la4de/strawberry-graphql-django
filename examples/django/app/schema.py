import strawberry
import strawberry_django
from strawberry_django import mutations
from typing import List
from .types import (
    Fruit, FruitInput, FruitPartialInput,
    Color, ColorInput, ColorPartialInput,
)

@strawberry.type
class Query:
    fruit: Fruit = strawberry_django.field()
    fruits: List[Fruit] = strawberry_django.field()

    color: Color = strawberry_django.field()
    colors: List[Color] = strawberry_django.field()

@strawberry.type
class Mutation:
    createFruit: Fruit = mutations.create(FruitInput)
    createFruits: List[Fruit] = mutations.create(FruitInput, many=True)
    updateFruits: List[Fruit] = mutations.update(FruitPartialInput, many=True)
    deleteFruits: List[Fruit] = mutations.delete(many=True)

    createColor: Color = mutations.create(ColorInput)
    createColors: List[Color] = mutations.create(ColorInput, many=True)
    updateColors: List[Color] = mutations.update(ColorPartialInput, many=True)
    deleteColors: List[Color] = mutations.delete(many=True)

schema = strawberry.Schema(query=Query, mutation=Mutation)
