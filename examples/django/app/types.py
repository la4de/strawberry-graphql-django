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
class FruitInput:
    id: auto
    name: auto
    color: auto

@strawberry_django.input(models.Fruit, partial=True)
class FruitPartialInput(FruitInput):
    pass

@strawberry_django.input(models.Color)
class ColorInput:
    id: auto
    name: auto
    fruits: auto

@strawberry_django.input(models.Color, partial=True)
class ColorPartialInput(ColorInput):
    pass
