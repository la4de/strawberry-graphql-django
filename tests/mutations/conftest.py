import pytest
import strawberry
import strawberry_django
from .. import models
from .. import types
from .. import utils
from .. types import (
    Fruit, FruitInput, FruitPartialInput,
    Color, ColorInput, ColorPartialInput,
    FruitType, FruitTypeInput, FruitTypePartialInput,
)
from strawberry_django import mutations
from typing import List

@pytest.fixture
def fruits(db):
    fruits = [ models.Fruit.objects.create(name=f'fruit{i+1}') for i in range(3) ]

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

    createFruitType: FruitType= mutations.create(FruitTypeInput)
    createFruitTypes: List[FruitType] = mutations.create(FruitTypeInput, many=True)
    updateFruitTypes: List[FruitType] = mutations.update(FruitTypePartialInput, many=True)
    deleteFruitTypes: List[FruitType] = mutations.delete(many=True)

@pytest.fixture
def mutation(db):
    return utils.generate_query(mutation=Mutation)
