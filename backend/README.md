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

Run migrations

```
python manage.py migrate
```

In order to execute the search first needs to load the fixtures data

```
python manage.py loaddata fixtures.json
```

Once the data is loaded, next step is to execute the `search_products` management command
for CLI app

```
python manage.py search_products
```

Another choice to check the search is to start the django server and go to following url to view
the results.

URL pattern: `http://127.0.0.1:8000/search/<str:query>/`

```
python manage.py runserver
```