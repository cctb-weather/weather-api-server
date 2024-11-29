# weather-api-server

API SERVER: [https://weather-api-server-fy1z.onrender.com](https://weather-api-server-fy1z.onrender.com)

## Installation
```sh
$ git clone https://github.com/cctb-weather/weather-api-server
$ cd weather-api-server
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

## Environment
create `.env` and fill the values.

```sh
$ cp .env.example .env
```

### Weather API key
set your weather api key to `WEATHER_API_KEY`

```sh
# .env
WEATHER_API_KEY=xxxxxxxxxxxx
```

## Start server on Local
```sh
$ flask --app app run
```

## Start server on Production
```sh
$ gunicorn app:app
```

