import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"


# ---------------------------------------------------------
# STEP 1: Define the DUMMY function that actually "runs"
# In real life this might call a weather API. Here it's fake.
# ---------------------------------------------------------
def get_weather(location: str) -> dict:
    print(f"    [dummy function actually executing for: {location}]")
    return {"location": location, "temperature_c": 24, "condition": "Sunny"}


# ---------------------------------------------------------
# STEP 2: Describe that function to the model so it KNOWS
# it exists and when it might be useful to call it.
# This description is what the model reasons over -- it
# never sees your Python code.
# ---------------------------------------------------------
weather_function = types.FunctionDeclaration(
    name="get_weather",
    description="Get the current weather for a specific city or location.",
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. 'Bangalore' or 'Paris'"
            }
        },
        "required": ["location"]
    }
)

tools = types.Tool(function_declarations=[weather_function])


# ---------------------------------------------------------
# STEP 3: Send a user message. The model decides on its own
# whether it needs to call the function to answer.
# ---------------------------------------------------------
user_message = "What's the weather like in Tokyo right now?"

response = client.models.generate_content(
    model=MODEL,
    contents=user_message,
    config=types.GenerateContentConfig(tools=[tools])
)

print("=== RAW RESPONSE (first pass) ===")
print(response)

# ---------------------------------------------------------
# STEP 4: Check whether the model actually asked to call
# the function, and pull out what arguments it chose.
# ---------------------------------------------------------
function_call = None
for part in response.candidates[0].content.parts:
    if part.function_call:
        function_call = part.function_call
        break

if function_call:
    print(f"\nModel wants to call: {function_call.name}")
    print(f"With arguments: {dict(function_call.args)}")

    # STEP 5: YOU run the real function -- the model can't.
    result = get_weather(**function_call.args)
    print(f"Function result: {result}")

    # STEP 6: Send the function's result BACK to the model,
    # so it can turn raw data into a natural language answer.
    # IMPORTANT: reuse the ORIGINAL Part object from the model's
    # response (it carries a thought_signature the model needs) --
    # don't rebuild a fresh Part from just the function_call, or
    # Gemini 3.x will reject the request as missing that signature.
    original_model_part = None
    for part in response.candidates[0].content.parts:
        if part.function_call:
            original_model_part = part
            break

    follow_up = client.models.generate_content(
        model=MODEL,
        contents=[
            types.Content(role="user", parts=[types.Part(text=user_message)]),
            types.Content(role="model", parts=[original_model_part]),
            types.Content(role="user", parts=[
                types.Part(function_response=types.FunctionResponse(
                    name="get_weather",
                    response=result
                ))
            ])
        ],
        config=types.GenerateContentConfig(tools=[tools])
    )

    print("\n=== FINAL NATURAL LANGUAGE ANSWER ===")
    print(follow_up.text)
else:
    print("\nModel answered directly without calling the function:")
    print(response.text)