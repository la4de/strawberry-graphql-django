# Authentication

Not implemented yet!

```python
from strawberry_django import auth

@strawberry.type
class Query:
    me: User = auth.current_user()

@strawberry.type
class Mutation:
    login: User = auth.login()
    logout: User = auth.logout()
    change_password: User = auth.change_password()
```
