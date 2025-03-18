# url-shortener-drf

## Run locally

```
docker compose build
docker compose up -d
```

## once updating models, apply changes to database

```
docker-compose -f .\docker-compose.yml run --rm app sh -c "python manage.py makemigrations"
docker-compose -f .\docker-compose.yml run --rm app sh -c "python manage.py migrate"
```