from flask import Flask, request, jsonify
import requests  # For making requests to an external weather API
import os
from datetime import datetime
from flask_cors import CORS
import pytz  # For timezone conversion
from timezonefinder import TimezoneFinder  # To find timezone based on lat/lon

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Replace with your actual API key
API_Key = "1c2ae1f094d24861963235832242111"  # WeatherAPI.com


@app.route("/debug")
def debug_paths():
    paths_info = {
        "Current Working Directory": os.getcwd(),
        "Script Directory": os.path.dirname(os.path.abspath(__file__)),
        "Parent Directory": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        ),
        "Attempted Frontend Path": os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "frontend")
        ),
        "Files in Current Directory": os.listdir(os.getcwd()),
        "Files in Parent Directory": os.listdir(
            os.path.abspath(os.path.join(os.getcwd(), ".."))
        ),
    }
    return jsonify(paths_info)


def get_timezone(lat, lon):
    tf = TimezoneFinder()
    timzone = tf.timezone_at(lng=float(lon), lat=float(lat))
    return pytz.timezone(timzone) if timzone else None


@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if city:  # if city is provided use this api call.
        url = f"http://api.weatherapi.com/v1/current.json?key={API_Key}&q={city}&days=1&aqi=no"
    elif lat or lon:  # if lat and lon provided then use this api call
        url = f"http://api.weatherapi.com/v1/current.json?key={API_Key}&q={lat},{lon}"
    else:
        return jsonify({"error": "Either city or lat/lon parameters are required"}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        location = weather_data["location"]
        current = weather_data["current"]

        result = {
            "city": location["name"],
            "temp_c": current["temp_c"],
            "weather": {
                "code": current["condition"]["code"],
                "text": current["condition"]["text"],
            },
            "wind_kph": current["wind_kph"],
            "humidity": current["humidity"],
        }

        return jsonify(result)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Error fetching weather data: {e}"}), 500

    except KeyError as e:
        return jsonify({"error": f"Error parsing weather data: {e}"}), 500


@app.route("/day_forecast", methods=["GET"])
def get_day_forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    try:
        # WeatherAPI.com endpoint for forecast
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_Key}&q={lat},{lon}&days=2"

        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Parse the response
        data = response.json()

        # Extract hourly forecast for the next 24 hours
        location = data["location"]

        forecast_hours = []
        for forecast_day in data["forecast"]["forecastday"]:
            for forecast_hour in forecast_day["hour"]:
                forecast_hours.append(forecast_hour)

        timezone = get_timezone(lat, lon)
        if timezone is None:
            raise Exception("Timezone not found for the given coordinates")

        current_hour = int(datetime.now(timezone).strftime("%H"))
        start_hour = current_hour + 1
        end_hour = current_hour + 8
        forecast_hours = forecast_hours[start_hour:end_hour]

        # Process and format the forecast data
        forecast = []
        for hour in forecast_hours:
            # Parse the datetime string and extract just the time
            hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M").strftime(
                "%H:%M"
            )

            forecast.append(
                {
                    "time": hour_time,
                    "temp_c": hour["temp_c"],
                    "weather": {
                        "text": hour["condition"]["text"],
                        "code": hour["condition"]["code"],
                    },
                }
            )

        return jsonify(
            {"status": "success", "forecast": forecast, "city": location["name"]}
        )

    except requests.RequestException as e:
        return jsonify(
            {"status": "error", "message": f"API request failed: {str(e)}"}
        ), 500

    except KeyError as e:
        return jsonify(
            {"status": "error", "message": f"Error parsing API response: {str(e)}"}
        ), 500

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"Unexpected error: {str(e)}"}
        ), 500


@app.route("/week_forecast", methods=["GET"])
def get_week_forecast():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    try:
        # WeatherAPI.com endpoint for weekly forecast (7 days)
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_Key}&q={lat},{lon}&days=7"

        # Make the API request
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response
        data = response.json()

        # Extract daily forecast data
        daily_forecast = data["forecast"]["forecastday"]

        # Process and format the forecast data
        forecast = []
        for day in daily_forecast:
            day_of_week = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%a")
            forecast.append(
                {
                    "day_of_week": day_of_week,
                    "max_temp_c": float(round(day["day"]["maxtemp_c"], 1)),
                    "min_temp_c": float(round(day["day"]["mintemp_c"], 1)),
                    "weather": {
                        "text": day["day"]["condition"]["text"],
                        "code": day["day"]["condition"]["code"],
                    },
                }
            )

        return jsonify(
            {
                "status": "success",
                "forecast": forecast,
            }
        )

    except requests.RequestException as e:
        return jsonify(
            {"status": "error", "message": f"API request failed: {str(e)}"}
        ), 500

    except KeyError as e:
        return jsonify(
            {"status": "error", "message": f"Error parsing API response: {str(e)}"}
        ), 500

    except Exception as e:
        return jsonify(
            {"status": "error", "message": f"Unexpected error: {str(e)}"}
        ), 500


if __name__ == "__main__":
    app.run(debug=True, port=8878)
