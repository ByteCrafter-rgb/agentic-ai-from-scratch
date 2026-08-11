import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def ask(system, user, temperature=1.0, max_tokens=1000):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
    )
    time.sleep(13)  # free tier allows 5 requests/minute -> ~1 every 12s minimum
    return response


# -----------------------------
# PART 1: System prompt vs user prompt
# -----------------------------
print("=" * 50)
print("PART 1: SYSTEM PROMPT CHANGES BEHAVIOR")
print("=" * 50)

r1 = ask("You are a pirate. Stay in character.", "What's the capital of France?")
print("\n[Pirate system prompt]")
print(r1.text)

r2 = ask("You are a terse fact-checker. One sentence answers only.", "What's the capital of France?")
print("\n[Terse fact-checker system prompt]")
print(r2.text)


# -----------------------------
# PART 2: Temperature comparison
# -----------------------------
print("\n" + "=" * 50)
print("PART 2: TEMPERATURE AFFECTS RANDOMNESS")
print("=" * 50)

for temp in [0, 0.5, 1.0]:
    print(f"\n--- temperature={temp} ---")
    for i in range(2):
        r = ask("You are a creative writer.", "Give me one tagline for a coffee shop.", temperature=temp)
        print(f"  {i+1}. {r.text.strip()}")


# -----------------------------
# PART 3: Max tokens / truncation
# -----------------------------
print("\n" + "=" * 50)
print("PART 3: MAX TOKENS CAN TRUNCATE OUTPUT")
print("=" * 50)

r3 = ask("You are a helpful teacher.", "Explain photosynthesis in detail.", max_tokens=60)
print("\nText:", r3.text)
print("Finish reason:", r3.candidates[0].finish_reason)
print("Thoughts tokens used:", r3.usage_metadata.thoughts_token_count)
print("Output tokens used:", r3.usage_metadata.candidates_token_count)

# NOTE: with a very small max_output_tokens, Gemini 3.5 may spend the whole
# budget on internal "thinking" tokens and return EMPTY text, even though
# finish_reason still says MAX_TOKENS. Don't assume your code is broken if
# r3.text looks blank -- check finish_reason and thoughts_token_count to
# understand what actually happened.