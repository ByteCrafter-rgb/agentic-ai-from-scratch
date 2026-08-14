import os
import time
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"


# ---------------------------------------------------------
# A robust wrapper: this is the pattern you'd actually use
# in a real app. It distinguishes between error TYPES and
# handles each differently, instead of one blanket try/except.
# ---------------------------------------------------------
def safe_call(contents, config, retries=3, base_delay=5):
    for attempt in range(1, retries + 1):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=config,
            )
            return response

        except errors.ServerError as e:
            # 503 etc -- Google's servers are temporarily overloaded.
            # This is NOT your fault. Safe to retry after a short wait.
            wait = base_delay * attempt  # simple backoff: 5s, 10s, 15s...
            print(f"  [ServerError] Model busy. Retrying in {wait}s "
                  f"(attempt {attempt}/{retries})...")
            time.sleep(wait)

        except errors.ClientError as e:
            msg = str(e)
            if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                # Rate limit or quota. Check WHICH one (per-minute vs
                # per-day) from the error text before deciding to retry --
                # a per-day quota won't be fixed by waiting 10 seconds.
                if "PerDay" in msg or "PerProjectPerModel-FreeTier" in msg and "Day" in msg:
                    print("  [QuotaError] Daily quota likely exhausted. "
                          "Retrying won't help today.")
                    raise
                wait = base_delay * attempt
                print(f"  [RateLimit] Too many requests. Retrying in {wait}s...")
                time.sleep(wait)
            else:
                # 400 (bad request), 404 (model not found), etc --
                # retrying won't fix these, something is actually wrong
                # with the request itself. Fail fast and loud instead
                # of silently retrying a request that can never succeed.
                print(f"  [ClientError] Not retryable: {msg[:200]}")
                raise

        except TimeoutError as e:
            wait = base_delay * attempt
            print(f"  [TimeoutError] Request took too long. "
                  f"Retrying in {wait}s...")
            time.sleep(wait)

    raise RuntimeError(f"Failed after {retries} attempts. Giving up.")


# ---------------------------------------------------------
# DEMO 1: Malformed response handling
# Even with a schema, always validate before trusting the
# output -- never assume json.loads() will succeed blindly.
# ---------------------------------------------------------
def get_structured_recipe(dish):
    schema = {
        "type": "object",
        "properties": {
            "recipe_name": {"type": "string"},
            "prep_time_minutes": {"type": "integer"},
            "ingredients": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["recipe_name", "prep_time_minutes", "ingredients"],
    }

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=schema,
        max_output_tokens=500,
    )

    response = safe_call(f"Give me a simple recipe for {dish}.", config)

    if not response.text:
        print("  [Malformed] Empty response text -- cannot parse.")
        return None

    try:
        data = json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"  [Malformed] Response was not valid JSON: {e}")
        print(f"  Raw text was: {response.text[:200]}")
        return None

    # Even valid JSON might be missing fields your code depends on --
    # defensive checking beyond just "did it parse."
    required_fields = ["recipe_name", "prep_time_minutes", "ingredients"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        print(f"  [Malformed] JSON parsed but missing fields: {missing}")
        return None

    return data


# ---------------------------------------------------------
# RUN THE DEMOS
# ---------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("DEMO: robust call with retry logic")
    print("=" * 50)
    recipe = get_structured_recipe("garlic bread")
    if recipe:
        print(f"\nSuccess: {recipe['recipe_name']} "
              f"({recipe['prep_time_minutes']} min)")
        for ing in recipe["ingredients"]:
            print(f"  - {ing}")
    else:
        print("\nCould not get a usable recipe after validation.")