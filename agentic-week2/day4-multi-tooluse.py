import os
import logging
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"

# ===========================================================
# Logging setup -- writes to both a file (agent.log) and the
# terminal, with timestamps and severity levels. This replaces
# the scattered print() statements with something you could
# actually leave running in production and review later.
# ===========================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("agent")


# ===========================================================
# TOOL 1: Weather (from Week 2 Day 1-3, unchanged)
# ===========================================================
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    80: "Rain showers", 95: "Thunderstorm",
}

def get_weather(city: str) -> dict:
    print(f"    [TOOL CALLED: get_weather(city={city!r})]")
    try:
        geo = requests.get("https://geocoding-api.open-meteo.com/v1/search",
                            params={"name": city, "count": 1}, timeout=10)
        geo.raise_for_status()
        results = geo.json().get("results")
        if not results:
            return {"error": f"No location found for '{city}'. Check the spelling or try a nearby major city."}
        lat, lon = results[0]["latitude"], results[0]["longitude"]

        weather = requests.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto"
        }, timeout=10)
        weather.raise_for_status()
        current = weather.json()["current"]
        return {
            "city": city,
            "temperature_c": current["temperature_2m"],
            "condition": WEATHER_CODES.get(current["weather_code"], "Unknown"),
            "wind_speed_kmh": current["wind_speed_10m"],
        }
    except requests.exceptions.Timeout:
        return {"error": "Weather service took too long to respond. Try again shortly."}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not reach the weather service. It may be down."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Weather service returned an error: {e}"}
    except (KeyError, ValueError) as e:
        return {"error": f"Weather service returned unexpected data: {e}"}


# ===========================================================
# TOOL 2: Currency conversion (Frankfurter API -- no key needed)
# ===========================================================
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    print(f"    [TOOL CALLED: convert_currency({amount}, {from_currency!r} -> {to_currency!r})]")
    try:
        response = requests.get("https://api.frankfurter.app/latest", params={
            "amount": amount,
            "from": from_currency.upper(),
            "to": to_currency.upper(),
        }, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "rates" not in data or to_currency.upper() not in data["rates"]:
            return {"error": f"'{from_currency}' or '{to_currency}' isn't a supported currency code."}
        return {
            "amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "converted_amount": data["rates"][to_currency.upper()],
        }
    except requests.exceptions.Timeout:
        return {"error": "Currency service took too long to respond. Try again shortly."}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not reach the currency service. It may be down."}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Currency service returned an error: {e}"}
    except (KeyError, ValueError) as e:
        return {"error": f"Currency service returned unexpected data: {e}"}


# ===========================================================
# Describe BOTH tools to the model
# ===========================================================
weather_tool = types.FunctionDeclaration(
    name="get_weather",
    description="Get the current real-time weather for a given city.",
    parameters={
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name, e.g. 'Pune'"}},
        "required": ["city"]
    }
)

currency_tool = types.FunctionDeclaration(
    name="convert_currency",
    description="Convert an amount of money from one currency to another using current exchange rates.",
    parameters={
        "type": "object",
        "properties": {
            "amount": {"type": "number", "description": "The amount to convert"},
            "from_currency": {"type": "string", "description": "3-letter currency code, e.g. 'USD'"},
            "to_currency": {"type": "string", "description": "3-letter currency code, e.g. 'INR'"},
        },
        "required": ["amount", "from_currency", "to_currency"]
    }
)

tools = types.Tool(function_declarations=[weather_tool, currency_tool])

AVAILABLE_FUNCTIONS = {
    "get_weather": get_weather,
    "convert_currency": convert_currency,
}


# ===========================================================
# Main loop: ask, let model choose (or not choose) a tool
# ===========================================================
def run_agent(user_message, max_steps=5):
    # This list IS the conversation. Every tool call and every tool
    # result gets appended here, so the model always has full context
    # of what's already been done -- this is what lets it chain a
    # SECOND tool call after seeing the first tool's result.
    contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]

    for step in range(max_steps):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=types.GenerateContentConfig(tools=[tools])
            )
        except Exception as e:
            print(f"Bot: Sorry, I couldn't process that right now ({type(e).__name__}). Try again in a moment.")
            return

        parts = response.candidates[0].content.parts
        function_call = next((p.function_call for p in parts if p.function_call), None)

        if not function_call:
            # No more tool calls requested -- this IS the final answer.
            logger.info("Final answer after %d tool step(s) for input: %r", step, user_message)
            print(f"Bot: {response.text}")
            return

        logger.info("Tool chosen: %s | args: %s | step: %d",
                    function_call.name, dict(function_call.args), step)
        print(f"Model chose: {function_call.name}({dict(function_call.args)})")

        func = AVAILABLE_FUNCTIONS.get(function_call.name)
        if func is None:
            logger.warning("Model requested unknown tool: %s", function_call.name)
            print(f"Bot: The model tried to call an unknown tool '{function_call.name}'. Skipping.")
            return

        result = func(**function_call.args)
        if "error" in result:
            logger.warning("Tool %s failed: %s", function_call.name, result["error"])
        else:
            logger.info("Tool %s succeeded: %s", function_call.name, result)

        # Append BOTH the model's tool request and the tool's result
        # to the running conversation, then loop back around -- the
        # model now sees this result and decides what to do NEXT:
        # call another tool, or write the final answer.
        model_part = next(p for p in parts if p.function_call)
        contents.append(types.Content(role="model", parts=[model_part]))
        contents.append(types.Content(role="user", parts=[
            types.Part(function_response=types.FunctionResponse(
                name=function_call.name, response=result
            ))
        ]))

    print("Bot: I wasn't able to finish that request in a reasonable number of steps.")


if __name__ == "__main__":
    print("=== Multi-tool agent (weather + currency). Type 'quit' to exit. ===\n")
    while True:
        msg = input("\nYou: ").strip()
        if msg.lower() in ("quit", "exit"):
            break
        run_agent(msg)