"""Web weather app — uses gui/api.py for data."""

import os
import sys
from pathlib import Path

from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, url_for
import requests

GUI_DIR = Path(__file__).resolve().parent.parent / "gui"
sys.path.insert(0, str(GUI_DIR))

import api  # noqa: E402

BASE_DIR = Path(__file__).resolve().parent
ICON_DIR = GUI_DIR / "UI" / "icons"

app = Flask(__name__, template_folder="templates", static_folder="static")


def c_to_f(c):
    return round((c * 9 / 5) + 32, 1)


def kmh_to_mph(kmh):
    return round(kmh * 0.621371, 1)


def detect_city_from_ip():
    for url in ("https://ipinfo.io/json", "https://ipapi.co/json/"):
        try:
            r = requests.get(url, timeout=5)
            if r.ok:
                j = r.json()
                city = (j.get("city") or "").strip()
                if city:
                    return city
                region = (j.get("region") or "").strip()
                if region:
                    return region
        except Exception:
            pass
    return ""


def unit_context(imperial):
    return {
        "imperial": imperial,
        "temp_unit": "°F" if imperial else "°C",
        "speed_unit": "mph" if imperial else "km/h",
        "vis_unit": "mi" if imperial else "km",
    }


def format_weather(current, hourly, daily, imperial):
    """Add display-friendly fields for templates."""
    if imperial:
        current = {
            **current,
            "temp_display": c_to_f(current["temperature_c"]),
            "wind_display": kmh_to_mph(current["windspeed_kph"]),
            "vis_display": round(current["visibility_km"] * 0.621371, 1),
        }
    else:
        current = {
            **current,
            "temp_display": current["temperature_c"],
            "wind_display": current["windspeed_kph"],
            "vis_display": round(current["visibility_km"], 1),
        }

    for day in daily:
        if imperial:
            day["min_display"] = c_to_f(day["min_temp_c"])
            day["max_display"] = c_to_f(day["max_temp_c"])
        else:
            day["min_display"] = day["min_temp_c"]
            day["max_display"] = day["max_temp_c"]
        day["icon_url"] = url_for(
            "weather_icon", code=day.get("weather_code", 0)
        )

    for hour in hourly:
        if imperial:
            hour["temp_display"] = c_to_f(hour["temp_c"])
            hour["wind_display"] = kmh_to_mph(hour["windspeed_kph"])
        else:
            hour["temp_display"] = hour["temp_c"]
            hour["wind_display"] = hour["windspeed_kph"]

    current["icon_url"] = url_for(
        "weather_icon", code=current.get("weather_code", 0)
    )
    return current, hourly, daily


def load_weather(city):
    validity = api.is_valid(city)
    if validity == "network_error":
        return None, "Network error. Please check your internet connection."
    if not validity:
        return None, f"Location '{city}' not found. Please try another city."

    result = api.get_weather_data(city)
    current, hourly, daily = result

    if isinstance(current, dict) and current.get("error"):
        return None, current["error"]

    if not current or "location" not in current:
        return None, "Failed to fetch weather data."

    return (current, hourly, daily), None


@app.route("/")
def index():
    error = request.args.get("error")
    return render_template("index.html", error=error)


@app.route("/weather")
def weather_page():
    city = (request.args.get("city") or "").strip()
    view = request.args.get("view", "daily")
    imperial = request.args.get("units", "metric") == "imperial"

    if not city:
        return redirect(url_for("index", error="Please enter a city name."))

    data, err = load_weather(city)
    if err:
        return redirect(url_for("index", error=err))

    current, hourly, daily = data
    current, hourly, daily = format_weather(current, hourly, daily, imperial)
    ctx = unit_context(imperial)

    return render_template(
        "weather.html",
        city=city,
        current=current,
        hourly=hourly,
        daily=daily,
        view=view,
        error=None,
        today=datetime.today().strftime("%Y-%m-%d"),
        **ctx,
    )


@app.route("/locate")
def locate():
    city = detect_city_from_ip()
    if not city:
        return redirect(
            url_for("index", error="Could not detect your location automatically.")
        )
    units = request.args.get("units", "metric")
    return redirect(
        url_for("weather_page", city=city, view="daily", units=units)
    )


@app.route("/icons/<int:code>")
def weather_icon(code):
    path = api.get_icon(code)
    if os.path.isfile(path):
        directory, filename = os.path.split(path)
        return send_from_directory(directory, filename)
    return ("", 404)


@app.route("/api/weather/<city>")
def api_weather(city):
    data, err = load_weather(city)
    if err:
        return jsonify({"error": err}), 400
    current, hourly, daily = data
    return jsonify(
        {"current": current, "hourly": hourly, "daily": daily}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
