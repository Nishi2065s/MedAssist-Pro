import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

contents = [
    {"role": "user", "parts": [{"text": "Hello"}]},
    {"role": "model", "parts": [{"text": "Hi!"}]},
    {"role": "user", "parts": [{"text": "What's up?"}]}
]

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.5,
        )
    )
    print("SUCCESS:", response.text)
except Exception as e:
    import traceback
    print("ERROR:")
    traceback.print_exc()
