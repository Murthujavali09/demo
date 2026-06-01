# Weather App

A weather application with three interfaces—**desktop GUI**, **command-line (CLI)**, and **web**—all powered by the same shared API in `gui/api.py`. Data comes from [Open-Meteo](https://open-meteo.com/) (no API key required).

## Features

- Search weather by city name
- Auto-detect location from your IP address
- Current conditions: temperature, wind, humidity, visibility, sunrise/sunset
- 7-day daily forecast
- Hourly forecast
- Metric and imperial units (GUI and web; CLI via `--imperial`)

## Project structure

```
p5/
├── gui/
│   ├── api.py          # Shared weather API (geocoding + forecasts)
│   ├── app.py          # Tkinter app entry point
│   ├── dashboard.py    # Home / search screen
│   ├── weather.py      # Weather details screen
│   └── UI/             # Icons and assets (optional)
├── cli/
│   └── main.py         # Command-line interface
├── web/
│   ├── app.py          # Flask web server
│   ├── templates/      # HTML pages
│   └── static/         # CSS
├── requirements.txt
└── README.md
```

All three apps import logic from `gui/api.py`, so API changes only need to be made in one place.

## Requirements

- Python 3.8+
- Internet connection

### Install dependencies

From the project root:

```bash
pip install -r requirements.txt
```

| Package   | Used by        |
|-----------|----------------|
| `requests`| API (all apps) |
| `flask`   | Web app        |
| `Pillow`  | GUI (icons)    |

## Running the app

### Desktop GUI

```bash
cd gui
python app.py
```

1. Enter a city and click **Get Weather**, or use **Auto Locate**.
2. View current weather and switch between **Weekly** and **Hourly** forecasts.
3. Change units with the **Metric / Imperial** dropdown.

### Command-line (CLI)

From the project root:

```bash
# Current weather + 7-day forecast
python cli/main.py London

# Hourly forecast instead of weekly
python cli/main.py London --hourly

# Current + daily + hourly
python cli/main.py London --all

# Fahrenheit, mph, miles
python cli/main.py London --imperial

# Detect city from your IP
python cli/main.py --locate
```

**CLI options**

| Option       | Description                          |
|-------------|--------------------------------------|
| `city`      | City name (positional)               |
| `--locate`  | Use IP-based geolocation             |
| `--hourly`  | Show hourly forecast (default: daily)|
| `--all`     | Show current, daily, and hourly      |
| `--imperial`| Use imperial units                   |

### Web

```bash
cd web
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

- Search by city on the home page
- **Auto Locate** uses your IP to find a city
- Switch **Weekly** / **Hourly** on the weather page
- Change **Metric** / **Imperial** from the units dropdown

**JSON API** (optional):

```http
GET /api/weather/London
```

Returns current weather, hourly, and daily forecast as JSON.

## Shared API (`gui/api.py`)

Main functions used by all interfaces:

| Function              | Description                                      |
|-----------------------|--------------------------------------------------|
| `get_weather_data(city)` | Fetch and cache weather for a city            |
| `is_valid(city)`      | Check if a city exists (or network error)        |
| `get_data()`          | Return cached current, hourly, and daily data    |
| `get_icon(code)`      | Path to weather icon for a WMO weather code      |

Weather codes and conditions are mapped in `api.py` (`weather_codes`, `weather_icons`).

## Data sources

- **Geocoding:** [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api)
- **Forecast:** [Open-Meteo Forecast API](https://open-meteo.com/en/docs)
- **Auto-locate:** [ipinfo.io](https://ipinfo.io) and [ipapi.co](https://ipapi.co) (fallback)

## Notes

- Icons are loaded from `gui/UI/icons/` when present; the web app serves them via `/icons/<code>`.
- If a city is not found, you will see an error in the GUI (dialog), CLI (stderr), or web (redirect with message).
- The GUI requires Tkinter (included with most Python installs on Windows/macOS; on Linux you may need `python3-tk`).

## License

This project is for educational use. Weather data is provided by Open-Meteo under their [terms of use](https://open-meteo.com/en/terms).
