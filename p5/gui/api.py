import os
import requests
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
ICON_DIR = os.path.abspath(os.path.join(BASE_DIR, "UI/icons"))
# --- Weather code mapping ---
weather_codes = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain",
    82: "Heavy rain",
    95: "Thunderstorm",
    96: "Hail",
    99: "Heavy hail",
}

weather_icons = {
    0: os.path.join(ICON_DIR, "sun.gif"),
    1: os.path.join(ICON_DIR, "sun.gif"),
    2: os.path.join(ICON_DIR, "partial_clouds.gif"),
    3: os.path.join(ICON_DIR, "clouds.gif"),
    45: os.path.join(ICON_DIR, "foggy.gif"),
    48: os.path.join(ICON_DIR, "foggy.gif"),
    51: os.path.join(ICON_DIR, "rain.gif"),
    53: os.path.join(ICON_DIR, "rain.gif"),
    55: os.path.join(ICON_DIR, "rain.gif"),
    61: os.path.join(ICON_DIR, "drizzle.gif"),
    63: os.path.join(ICON_DIR, "drizzle.gif"),
    65: os.path.join(ICON_DIR, "rainy.gif"),
    71: os.path.join(ICON_DIR, "snow.gif"),
    73: os.path.join(ICON_DIR, "snow.gif"),
    75: os.path.join(ICON_DIR, "snow.gif"),
    80: os.path.join(ICON_DIR, "drizzle.gif"),
    81: os.path.join(ICON_DIR, "drizzle.gif"),
    82: os.path.join(ICON_DIR, "drizzle.gif"),
    95: os.path.join(ICON_DIR, "storm.gif"),
    96: os.path.join(ICON_DIR, "hail.gif"),
    99: os.path.join(ICON_DIR, "hail.gif"),
}


current_weather = {}
daily_forecast = []
hourly_forecast = []


def get_weather_data(city):
    global current_weather, daily_forecast, hourly_forecast
    daily_forecast.clear()
    hourly_forecast.clear()

    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()

        if not geo_res.get("results"):
            return {"error": f"Location '{city}' not found"}, [], []

        lat = geo_res["results"][0]["latitude"]
        lon = geo_res["results"][0]["longitude"]
        location_name = (
            f"{geo_res['results'][0]['name']}, {geo_res['results'][0]['country']}"
        )

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            "&current_weather=true"
            "&hourly=temperature_2m,relativehumidity_2m,visibility,weathercode,windspeed_10m"
            "&daily=temperature_2m_max,temperature_2m_min,weathercode,sunrise,sunset"
            "&forecast_days=7&timezone=auto"
        )
        data = requests.get(weather_url).json()
        cw = data.get("current_weather", {})
        current_time = cw.get("time")
        # Convert to hourly format (e.g., "2025-08-15T03:15" -> "2025-08-15T03:00")
        current_hour = current_time[:13] + ":00"

        try:
            current_time_index = data["hourly"]["time"].index(current_hour)
        except ValueError:
            # If still not found, use the first available index
            current_time_index = 0
            print(
                f"Warning: Could not find exact time match for {current_hour}, using index 0"
            )
        current_weather = {
            "location": location_name,
            "temperature_c": cw.get("temperature"),
            "windspeed_kph": cw.get("windspeed"),
            "weather_code": cw.get("weathercode"),
            "condition": weather_codes.get(cw.get("weathercode"), "Unknown"),
            "humidity_percent": data["hourly"]["relativehumidity_2m"][
                current_time_index
            ],
            "visibility_km": data["hourly"]["visibility"][current_time_index] / 1000,
            "sunrise": datetime.fromisoformat(data["daily"]["sunrise"][0]).strftime(
                "%I:%M %p"
            ),
            "sunset": datetime.fromisoformat(data["daily"]["sunset"][0]).strftime(
                "%I:%M %p"
            ),
        }

        for i, date_str in enumerate(data["daily"]["time"]):
            day_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
            daily_forecast.append(
                {
                    "date": date_str,
                    "day_name": day_name,
                    "min_temp_c": data["daily"]["temperature_2m_min"][i],
                    "max_temp_c": data["daily"]["temperature_2m_max"][i],
                    "weather_code": data["daily"]["weathercode"][i],
                    "condition": weather_codes.get(
                        data["daily"]["weathercode"][i], "Unknown"
                    ),
                    "sunrise": datetime.fromisoformat(
                        data["daily"]["sunrise"][i]
                    ).strftime("%I:%M %p"),
                    "sunset": datetime.fromisoformat(
                        data["daily"]["sunset"][i]
                    ).strftime("%I:%M %p"),
                }
            )

        for i in range(6, 17):
            hourly_forecast.append(
                {
                    "time": datetime.fromisoformat(data["hourly"]["time"][i]).strftime(
                        "%I:%M %p"
                    ),
                    "temp_c": data["hourly"]["temperature_2m"][i],
                    "condition": weather_codes.get(
                        data["hourly"]["weathercode"][i], "Unknown"
                    ),
                    "windspeed_kph": data["hourly"]["windspeed_10m"][i],
                    "humidity_percent": data["hourly"]["relativehumidity_2m"][i],
                    "visibility_km": data["hourly"]["visibility"][i] / 1000,
                }
            )

        return current_weather, hourly_forecast, daily_forecast

    except Exception as e:
        print(f"error: {str(e)}")
        return {}, [], []


def is_valid(city):
    try:
        if not city.strip():
            return False

        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()

        return bool(geo_res.get("results"))
    except requests.exceptions.RequestException:
        # Network or timeout issue
        return "network_error"
    except Exception:
        return False


def get_data():
    return current_weather, hourly_forecast, daily_forecast


def get_icon(code):
    return weather_icons.get(code, weather_icons[0])
