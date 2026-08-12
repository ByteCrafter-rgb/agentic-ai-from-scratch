import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.1-flash-lite"

# Conversation history
history = []

while True:

    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    # Add user's message to history
    history.append(
        types.Content(
            role="user",
            parts=[types.Part(text=user_input)]
        )
    )

    # Send the ENTIRE conversation history
    response = client.models.generate_content(
        model=MODEL,
        contents=history
    )

    assistant_response = response.text

    # Print response
    print("Bot:", assistant_response)

    # Add model's response to history
    history.append(
        types.Content(
            role="model",
            parts=[types.Part(text=assistant_response)]
        )
    )