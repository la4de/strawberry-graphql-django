# Mutations

```python
from strawberry_django import mutations

@strawberry.type
class Mutation:
    createFruit: Fruit = mutations.create(FruitInput)
    createFruits: List[Fruit] = mutations.create(FruitInput, many=True)
    updateFruits: List[Fruit] = mutations.update(FruitPartialInput, many=True)
    deleteFruits: List[Fruit] = mutations.delete(many=True)
```
