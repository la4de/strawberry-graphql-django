# Typed filtering with Django Filter

Install django-filters `pip install django-filter`

Then add `django_filters` to your INSTALLED_APPS.

```python
INSTALLED_APPS = [
    ...
    'django_filters',
]
```

Write a `FilterSet` and decorate it with `strawberry_django.filter`:

```python
import strawberry_django
import django_filters


@strawberry_django.filter
class UserFilter(django_filters.FilterSet):
    # These fields definitions are optional, 
    # they can be automatically generated.

    name = django_filters.CharFilter(lookup_expr="icontains")
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(group__name__icontains=value) |
            Q(tag__name__icontains=value)
        )

    class Meta:
        model = models.User
        fields = ["name", "search"]
```

Create the input type with `UserFilter`, and filter a queryset with `strawberry_django.filters.apply`

```python
@strawberry.type
class Query:
    @strawberry.field
    def user_ids(self, filters: Optional[UserFilter] = UNSET) -> List[int]:
        queryset = models.User.objects.all()
        queryset = strawberry_django.filters.apply(filters, queryset)
        return queryset.order_by("pk").values_list("pk", flat=True)
```

The schema will be:
```
type Query {
  userIds(filters: UserFilter): [Int!]!
}

input UserFilter {
  name: String
  search: String
}
```

And can be queried with:
```
query getUserIds {
    userIds (filters: {"name": "user1", "search": "tag2"})
}
```

See django-filter docs for details on writing FilterSets: https://django-filter.readthedocs.io
