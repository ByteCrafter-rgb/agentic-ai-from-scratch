import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3.1-flash-lite"


def ask(system, user, temperature=1.0, max_tokens=500, retries=3):
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user,
                config=types.GenerateContentConfig(
                    system_instruction=system,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    thinking_config=types.ThinkingConfig(thinking_level="minimal"),
                )
            )
            time.sleep(2)  # small buffer for rate limits
            return response
        except errors.ServerError as e:
            print(f"    [server busy, retry {attempt+1}/{retries} in 10s...]")
            time.sleep(10)
    raise RuntimeError("Server still unavailable after retries -- try again in a few minutes.")


# PART 1: System prompt vs user prompt
print("=" * 50)
print("PART 1: SYSTEM PROMPT CHANGES BEHAVIOR")
print("=" * 50)

r1 = ask("You are a pirate. Stay in character.", "What's the capital of France?")
print("\n[Pirate system prompt]")
print(r1.text)

r2 = ask("You are a terse fact-checker. One sentence answers only.", "What's the capital of France?")
print("\n[Terse fact-checker system prompt]")
print(r2.text)


# PART 2: Temperature comparison
print("\n" + "=" * 50)
print("PART 2: TEMPERATURE AFFECTS RANDOMNESS")
print("=" * 50)

for temp in [0, 0.5, 1.0]:
    print(f"\n--- temperature={temp} ---")
    for i in range(2):
        r = ask("You are a creative writer.", "Give me one tagline for a coffee shop.", temperature=temp)
        if r.text is None:
            print(f"  {i+1}. [EMPTY RESPONSE] finish_reason={r.candidates[0].finish_reason}")
            print(f"     full candidate: {r.candidates[0]}")
        else:
            print(f"  {i+1}. {r.text.strip()}")


# PART 3: Max tokens / truncation
print("\n" + "=" * 50)
print("PART 3: MAX TOKENS CAN TRUNCATE OUTPUT")
print("=" * 50)

r3 = ask("You are a helpful teacher.", "Explain photosynthesis in detail.", max_tokens=25)
print("\nText:", r3.text)
print("Finish reason:", r3.candidates[0].finish_reason)
print("Output tokens used:", r3.usage_metadata.candidates_token_count)