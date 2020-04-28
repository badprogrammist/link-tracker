# API

## `POST /api/v1/linktracker/visited_links`

Add visited links

### Payload
```
{
"links": [
	"https://ya.ru",
	"https://ya.ru?q=123",
	"funbox.ru",
	"https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
	]
}
```

### Response

```
{
    "status": "ok"
}
```

### Errors

- `400 Bad Request`
    - data structure is invalid
    - invalid url


## `GET /api/v1/linktracker/visited_domains?from=0&to=1588088486.324779`

Get visited urls set

### Args

- `from` - timestamp of begin time
- `to` - timestamp of end time

### Response

```
{
    "domains": [
        "funbox.ru",
        "ya.ru",
        "stackoverflow.com"
    ],
    "status": "ok"
}
```

### Errors

- `400 Bad Request`
    - `from` is null
    - `to` is null


# Tests

# Run tests

```
$python -m pytest tests/
```

## Run tests in container

```
$docker build -t linktracker .
$docker run linktracker python -m pytest tests/
```

## Run tests with redis

```
$docker-compose -f docker-compose-test.yaml up
```

# Running

```
$docker-compose up

curl --location --request POST 'localhost:8000/api/v1/linktracker/visited_links' \
--header 'Content-Type: application/json' \
--data-raw '{
"links": [
	"https://ya.ru",
	"https://ya.ru?q=123",
	"funbox.ru",
	"https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor"
	]
}'

curl --location --request GET 'localhost:8000/api/v1/linktracker/visited_domains?from=0&to=1588088486.324779'
```