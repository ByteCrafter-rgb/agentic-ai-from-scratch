import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"


# ---------------------------------------------------------
# YOUR REAL FUNCTIONS from Week 2 Day 1 (unchanged)
# ---------------------------------------------------------
def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    response = requests.get(url, params={"name": city_name, "count": 1})
    response.raise_for_status()
    data = response.json()
    if "results" not in data or len(data["results"]) == 0:
        raise ValueError(f"No location found for '{city_name}'")
    r = data["results"][0]
    return r["latitude"], r["longitude"]


WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    80: "Rain showers", 95: "Thunderstorm",
}


def get_weather(city: str) -> dict:
    """This is the function the MODEL will trigger -- but never runs itself."""
    print(f"    [REAL function executing for: {city}]")
    lat, lon = get_coordinates(city)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": lat, "longitude": lon,
              "current": "temperature_2m,weather_code,wind_speed_10m", "timezone": "auto"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    current = response.json()["current"]
    return {
        "city": city,
        "temperature_c": current["temperature_2m"],
        "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
        "wind_speed_kmh": current["wind_speed_10m"],
    }


# ---------------------------------------------------------
# STEP A: Describe get_weather to the model. This description
# is ALL the model ever sees of your function -- not the code,
# not the API calls inside it, just this name/description/schema.
# ---------------------------------------------------------
weather_tool = types.FunctionDeclaration(
    name="get_weather",
    description="Get the current real-time weather for a given city.",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name, e.g. 'Pune'"}
        },
        "required": ["city"]
    }
)
tools = types.Tool(function_declarations=[weather_tool])


# ---------------------------------------------------------
# STEP B: Ask a question. The model decides FOR ITSELF whether
# it needs to call the tool to answer.
# ---------------------------------------------------------
user_message = input("Ask me about the weather somewhere: ").strip()

response = client.models.generate_content(
    model=MODEL,
    contents=user_message,
    config=types.GenerateContentConfig(
        tools=[tools],
        # DAY 3: no tool_config here -- default mode is "AUTO",
        # meaning the model decides FOR ITSELF whether this
        # question needs the tool or can be answered directly.
        # This is the real test: yesterday we proved the wiring
        # works, today we test its judgment.
    )
)

# ---------------------------------------------------------
# STEP C: Check if the model requested the tool.
# ---------------------------------------------------------
function_call = None
for part in response.candidates[0].content.parts:
    if part.function_call:
        function_call = part.function_call
        break

if function_call:
    print(f"\nModel requested: {function_call.name}({dict(function_call.args)})")

    # STEP D: YOUR code runs the REAL function -- the actual
    # network calls to Open-Meteo happen right here, not inside the AI.
    result = get_weather(**function_call.args)
    print(f"Real result: {result}")

    # STEP E: Send the real result back so the model can phrase
    # a natural-language answer. Reuse the original Part (with its
    # thought_signature) rather than rebuilding it -- see Week 1 Day 3.
    original_part = next(p for p in response.candidates[0].content.parts if p.function_call)

    follow_up = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(role="user", parts=[types.Part(text=user_message)]),
            types.Content(role="model", parts=[original_part]),
            types.Content(role="user", parts=[
                types.Part(function_response=types.FunctionResponse(
                    name="get_weather", response=result
                ))
            ])
        ],
        config=types.GenerateContentConfig(tools=[tools])
    )
    print(f"\nBot: {follow_up.text}")
else:
    print(f"\nBot (no tool needed): {response.text}")