import json
import os
from openai import OpenAI

try:
    with open('/Users/bradyespey/Projects/Files/Reminders/openai_api_key.json') as f:
        data = json.load(f)
        api_key = data["api_key"]

    with open('/Users/bradyespey/Projects/Files/Reminders/openai_model_id.json') as f:
        model_data = json.load(f)
        model_id = model_data["model_id"]
except FileNotFoundError as e:
    print(f"File not found: {e}")
    exit(1)
except KeyError as e:
    print(f"Missing key in JSON file: {e}")
    exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    exit(1)

# Create the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# Use the correct API method for the chat-based model
try:
    response = client.chat.completions.create(
        model=model_id,  # your fine-tuned model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! How are you?"}
        ]
    )

    # Access and print the response
    print(response.choices[0].message.content)

except Exception as e:
    print(f"An error occurred while making the request: {e}")
