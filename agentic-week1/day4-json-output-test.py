import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"


# ---------------------------------------------------------
# Define the exact SHAPE of JSON you want back.
# This is a schema, not a suggestion -- the API enforces it,
# so you don't need to hope the model "remembers" to use JSON.
# ---------------------------------------------------------
recipe_schema = {
    "type": "object",
    "properties": {
        "recipe_name": {"type": "string"},
        "prep_time_minutes": {"type": "integer"},
        "difficulty": {
            "type": "string",
            "enum": ["easy", "medium", "hard"]
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["recipe_name", "prep_time_minutes", "difficulty", "ingredients"]
}

response = client.models.generate_content(
    model=MODEL,
    contents="Give me a simple recipe for scrambled eggs.",
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=recipe_schema
    )
)

print("=== RAW TEXT (should be valid JSON) ===")
print(response.text)

# ---------------------------------------------------------
# Because it's guaranteed valid JSON matching your schema,
# you can parse it straight into a Python dict -- no
# regex-hacking a plain-text response, no "please respond
# only in JSON" prompt begging.
# ---------------------------------------------------------
data = json.loads(response.text)

print("\n=== PARSED PYTHON DICT ===")
print(f"Recipe: {data['recipe_name']}")
print(f"Prep time: {data['prep_time_minutes']} minutes")
print(f"Difficulty: {data['difficulty']}")
print("Ingredients:")
for ing in data["ingredients"]:
    print(f"  - {ing}")