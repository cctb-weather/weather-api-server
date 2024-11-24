# HOW TO RUN
# Go to the work directory: C:\Users\nelsi\OneDrive\CCTB\IST107 - Internet Programming and Web Applications\WeatherApp - localhost
# Open Anaconda doveAI CMD
# Run `app.openweather.py`
# This provides the current weather condition

# USING OPENWEATHER API
from flask import Flask, request, jsonify, send_from_directory
import requests  # For making requests to an external weather API
import os
from datetime import datetime

app = Flask(__name__)

# Replace with your actual API key
WEATHER_API_KEY = "8356db19f8ee3e8ef2fe65204f7d2792"  # api.openweathermap.org
API_Key = "fbc6b21a336b46f696502554240911"  # WeatherAPI.com


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
    city = request.args.get("city")
    if city:  # if city is provided use this api call.
        api_url = f"http://api.weatherapi.com/v1/forecast.json?key={API_Key}&q={city}&days=1&aqi=no"

        try:
            # WeatherAPI.com endpoint for forecast
            url = f"http://api.weatherapi.com/v1/forecast.json?key={API_Key}&q={city}&days=1&aqi=no"

            # Make the API request
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the response
            data = response.json()

            # Extract hourly forecast for the next 24 hours
            hourly_forecast = data["forecast"]["forecastday"][0]["hour"]

            # Process and format the forecast data
            formatted_forecast = []
            for hour in hourly_forecast:
                # Parse the datetime string and extract just the time
                hour_time = datetime.strptime(hour["time"], "%Y-%m-%d %H:%M").strftime(
                    "%H:%M"
                )

                formatted_forecast.append(
                    {
                        "time": hour_time,
                        "temp_c": hour["temp_c"],
                        "temp_f": hour["temp_f"],
                        "condition": hour["condition"]["text"],
                        "humidity": hour["humidity"],
                        "wind_kph": hour["wind_kph"],
                        "chance_of_rain": hour["chance_of_rain"],
                    }
                )

            return jsonify({"status": "success", "forecast": formatted_forecast})

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

    else:
        return jsonify({"error": "Either city or lat/lon parameters are required"}), 400


@app.route("/week_forecast", methods=["GET"])
def get_week_forecast():
    city = request.args.get("city")

    if city:  # if city is provided use this api call.
        try:
            # WeatherAPI.com endpoint for weekly forecast (7 days)
            url = f"http://api.weatherapi.com/v1/forecast.json?key={API_Key}&q={city}&days=7&aqi=no"

            # Make the API request
            response = requests.get(url)
            response.raise_for_status()

            # Parse the response
            data = response.json()

            # Extract daily forecast data
            daily_forecast = data["forecast"]["forecastday"]

            # Process and format the forecast data
            formatted_forecast = []
            for day in daily_forecast:
                formatted_forecast.append(
                    {
                        "date": day["date"],
                        "max_temp_c": day["day"]["maxtemp_c"],
                        "min_temp_c": day["day"]["mintemp_c"],
                        "max_temp_f": day["day"]["maxtemp_f"],
                        "min_temp_f": day["day"]["mintemp_f"],
                        "avg_humidity": day["day"]["avghumidity"],
                        "condition": day["day"]["condition"]["text"],
                        "chance_of_rain": day["day"]["daily_chance_of_rain"],
                        "total_precipitation_mm": day["day"]["totalprecip_mm"],
                        "max_wind_kph": day["day"]["maxwind_kph"],
                        "sunrise": day["astro"]["sunrise"],
                        "sunset": day["astro"]["sunset"],
                    }
                )

            return jsonify(
                {
                    "status": "success",
                    "location": data["location"]["name"],
                    "country": data["location"]["country"],
                    "forecast": formatted_forecast,
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

    else:
        return jsonify({"error": "Either city or lat/lon parameters are required"}), 400


if __name__ == "__main__":
    app.run(debug=True, port=8878)
