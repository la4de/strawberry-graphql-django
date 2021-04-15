import strawberry_django
from strawberry_django import auto
from typing import List
from . import models

@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    color: 'Color'

@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: List[Fruit]


@strawberry_django.input(models.Fruit)
class FruitInput(Fruit):
    color: 'ColorInput'

@strawberry_django.input(models.Color)
class ColorInput(Color):
    fruits: List[FruitInput]


from .legacy.types import *
