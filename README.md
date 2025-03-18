# url-shortener-drf

## Run locally

```
docker compose build
docker compose up -d
```

## once updating models, apply changes to database

```
docker compose -f .\docker-compose.yml run --rm app sh -c "python manage.py makemigrations"
docker compose -f .\docker-compose.yml run --rm app sh -c "python manage.py migrate"
```

## How to start the container on the local machine
First, install Docker and Docker Compose.</br>
Then execute the following command to pull the image. 
```
docker pull kobukuro/url-shortener-drf_app:latest
```
Then make sure the file docker-compose-test.yml exists locally (this file is in the root directory of this repository)</br>
Then execute the following command, then the containers will successfully start (this command is for Windows):
```
docker compose -f .\docker-compose-test.yml up -d
```
Then you can view the API documentation at http://localhost:8000/swagger/. You can also interact with the APIs directly on the page, or use Postman or a browser (browser for calling the GET API).