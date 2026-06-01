#!/usr/bin/env python3
"""CLI weather app — uses gui/api.py for data."""

import argparse
import sys
from datetime import datetime
from pathlib import Path

GUI_DIR = Path(__file__).resolve().parent.parent / "gui"
sys.path.insert(0, str(GUI_DIR))

import api  # noqa: E402
import requests  # noqa: E402


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


def format_temp(c, imperial):
    if imperial:
        return f"{c_to_f(c)}°F"
    return f"{c}°C"


def format_wind(kmh, imperial):
    if imperial:
        return f"{kmh_to_mph(kmh)} mph"
    return f"{kmh} km/h"


def format_vis(km, imperial):
    if imperial:
        return f"{km * 0.621371:.1f} mi"
    return f"{km:.1f} km"


def print_header(text):
    width = 60
    print()
    print("=" * width)
    print(f"  {text}")
    print("=" * width)


def print_current(current, imperial):
    print_header(current["location"])
    print(f"  Condition:   {current['condition']}")
    print(f"  Temperature: {format_temp(current['temperature_c'], imperial)}")
    print(f"  Wind:        {format_wind(current['windspeed_kph'], imperial)}")
    print(f"  Humidity:    {current['humidity_percent']}%")
    print(f"  Visibility:  {format_vis(current['visibility_km'], imperial)}")
    print(f"  Sunrise:     {current['sunrise']}")
    print(f"  Sunset:      {current['sunset']}")


def print_daily(daily, imperial):
    print_header("7-Day Forecast")
    today = datetime.today().strftime("%Y-%m-%d")
    print(f"  {'Day':<12} {'Condition':<18} {'Min':>8} {'Max':>8}")
    print("  " + "-" * 50)
    for day in daily:
        label = "Today" if day["date"] == today else day["day_name"]
        lo = format_temp(day["min_temp_c"], imperial)
        hi = format_temp(day["max_temp_c"], imperial)
        print(f"  {label:<12} {day['condition']:<18} {lo:>8} {hi:>8}")


def print_hourly(hourly, imperial):
    print_header("Hourly Forecast")
    print(f"  {'Time':<10} {'Temp':>8} {'Condition':<18} {'Wind':>10} {'Hum':>6}")
    print("  " + "-" * 56)
    for hour in hourly:
        temp = format_temp(hour["temp_c"], imperial)
        wind = format_wind(hour["windspeed_kph"], imperial)
        print(
            f"  {hour['time']:<10} {temp:>8} {hour['condition']:<18} "
            f"{wind:>10} {hour['humidity_percent']:>5}%"
        )


def fetch_weather(city):
    validity = api.is_valid(city)
    if validity == "network_error":
        print("Error: Network error. Check your internet connection.", file=sys.stderr)
        sys.exit(1)
    if not validity:
        print(f"Error: Invalid location '{city}'.", file=sys.stderr)
        sys.exit(1)

    result = api.get_weather_data(city)
    current, hourly, daily = result

    if isinstance(current, dict) and current.get("error"):
        print(f"Error: {current['error']}", file=sys.stderr)
        sys.exit(1)

    if not current or "location" not in current:
        print("Error: Failed to fetch weather data.", file=sys.stderr)
        sys.exit(1)

    return current, hourly, daily


def build_parser():
    parser = argparse.ArgumentParser(
        description="Weather CLI — powered by Open-Meteo (shared gui/api)."
    )
    parser.add_argument(
        "city",
        nargs="?",
        help="City name (e.g. London, Tokyo)",
    )
    parser.add_argument(
        "--locate",
        action="store_true",
        help="Detect city from your IP address",
    )
    parser.add_argument(
        "--hourly",
        action="store_true",
        help="Show hourly forecast instead of 7-day",
    )
    parser.add_argument(
        "--imperial",
        action="store_true",
        help="Use Fahrenheit, mph, and miles",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show current, daily, and hourly forecasts",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.locate:
        city = detect_city_from_ip()
        if not city:
            print("Error: Could not detect location automatically.", file=sys.stderr)
            sys.exit(1)
        print(f"Detected location: {city}")
    elif args.city:
        city = args.city.strip()
    else:
        parser.print_help()
        sys.exit(1)

    current, hourly, daily = fetch_weather(city)
    print_current(current, args.imperial)

    if args.all:
        print_daily(daily, args.imperial)
        print_hourly(hourly, args.imperial)
    elif args.hourly:
        print_hourly(hourly, args.imperial)
    else:
        print_daily(daily, args.imperial)

    print()


if __name__ == "__main__":
    main()
