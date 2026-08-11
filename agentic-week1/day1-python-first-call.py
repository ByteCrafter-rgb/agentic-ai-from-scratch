import os
from dotenv import load_dotenv
from google import genai

# Load variables from .env into the environment (this loads GEMINI_API_KEY)
load_dotenv()

# Create the client — this is your authenticated connection to Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Send the prompt and get a response back
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="A quick brown fox jumps over a lazy dog. What is so special about this one sentence?"
)

# Full raw response object — messy but shows everything (tokens, finish_reason, etc.)
# print("=== FULL RESPONSE OBJECT ===")
# print(response)

print("\n=== JUST THE TEXT ===")
print(response.text)

# print("\n=== USAGE METADATA ===")
# print(response.usage_metadata)

print("\n=== FINISH REASON ===")
print(response.candidates[0].finish_reason)