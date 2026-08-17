import requests

# ---------------------------------------------------------
# STEP 1: Geocoding -- turn a city name into lat/lon.
# Open-Meteo's weather endpoint needs coordinates, not names,
# so most real integrations need a two-step lookup like this.
# ---------------------------------------------------------
def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1}

    response = requests.get(url, params=params)
    response.raise_for_status()  # raises an error if status code is 4xx/5xx

    data = response.json()

    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"No location found for '{city_name}'")

    result = data["results"][0]
    return {
        "name": result["name"],
        "country": result.get("country", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }


# ---------------------------------------------------------
# STEP 2: Actual weather call using those coordinates.
# ---------------------------------------------------------
def get_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code,wind_speed_10m",
        "timezone": "auto",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


# Rough mapping of Open-Meteo's numeric weather codes to plain text.
# (Full table: https://open-meteo.com/en/docs -- WMO weather codes)
WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm",
}


if __name__ == "__main__":
    city = input("Enter a city name: ").strip()

    try:
        location = get_coordinates(city)
        print(f"\nFound: {location['name']}, {location['country']} "
              f"(lat={location['latitude']}, lon={location['longitude']})")

        weather = get_weather(location["latitude"], location["longitude"])

        # Print the FULL raw JSON first, so you can see the actual shape
        # of a real API response before we start picking fields out of it.
        print("\n=== RAW JSON RESPONSE ===")
        print(weather)

        current = weather["current"]
        code = current["weather_code"]
        condition = WEATHER_CODES.get(code, f"Unknown (code {code})")

        print(f"\n=== READABLE SUMMARY ===")
        print(f"{location['name']}: {current['temperature_2m']}°C, {condition}")
        print(f"Wind speed: {current['wind_speed_10m']} km/h")

    except requests.exceptions.RequestException as e:
        print(f"Network/API error: {e}")
    except ValueError as e:
        print(f"Error: {e}")