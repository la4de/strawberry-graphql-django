import strawberry_django
from strawberry_django import auto
from typing import List
from . import models

@strawberry_django.type(models.Fruit)
class Fruit:
    id: auto
    name: auto
    color: 'Color'
    types: List['FruitType']

@strawberry_django.type(models.Color)
class Color:
    id: auto
    name: auto
    fruits: List[Fruit]

@strawberry_django.type(models.FruitType)
class FruitType:
    id: auto
    name: auto
    fruits: List[Fruit]

@strawberry_django.input(models.Fruit)
class FruitInput:
    id: auto
    name: auto
    color: auto

@strawberry_django.input(models.Color)
class ColorInput:
    id: auto
    name: auto
    fruits: auto

@strawberry_django.input(models.FruitType)
class FruitTypeInput:
    id: auto
    name: auto
    fruits: auto

@strawberry_django.input(models.Fruit, partial=True)
class FruitPartialInput(FruitInput):
    name: auto
    color: auto

@strawberry_django.input(models.Color, partial=True)
class ColorPartialInput(Color):
    name: auto
    fruits: auto

@strawberry_django.input(models.FruitType, partial=True)
class FruitTypePartialInput(FruitTypeInput):
    pass

# TODO: remove later
from .legacy.types import *
