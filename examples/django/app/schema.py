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

"""
Code above generates following schema

type Color {
  id: ID!
  name: String!
  fruits: [Fruit!]
}

input ColorInput {
  id: ID
  name: String!
  fruits: ManyToOneInput
}

input ColorPartialInput {
  id: ID
  name: String
  fruits: ManyToOneInput
}

type Fruit {
  id: ID!
  name: String!
  color: Color
}

input FruitInput {
  id: ID
  name: String!
  color: OneToManyInput
}

input FruitPartialInput {
  id: ID
  name: String
  color: OneToManyInput
}

input ManyToOneInput {
  add: [ID!]
  remove: [ID!]
  set: [ID!]
}

type Mutation {
  createFruit(data: FruitInput!): Fruit!
  createFruits(data: [FruitInput!]!): [Fruit!]!
  updateFruits(data: FruitPartialInput!): [Fruit!]!
  deleteFruits: [Fruit!]!
  createColor(data: ColorInput!): Color!
  createColors(data: [ColorInput!]!): [Color!]!
  updateColors(data: ColorPartialInput!): [Color!]!
  deleteColors: [Color!]!
}

input OneToManyInput {
  set: ID
}

type Query {
  fruit: Fruit!
  fruits: [Fruit!]!
  color: Color!
  colors: [Color!]!
}
"""
