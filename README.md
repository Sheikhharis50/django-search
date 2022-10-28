# Django Search

## Dependencies

1. PostgreSQL >= 11
2. Django >= 4

## Quickstart

Activate the virtual enviornment

```
python -m venv venv
source venv/bin/activate
```

In order to execute the search first needs to load the fixtures data

```
python manage.py loaddata fixtures.json
```

Once the data is loaded, next step is to execute the `search_products` management command

```
python manage.py search_products
```
