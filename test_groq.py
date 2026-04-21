import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.5,
        max_tokens=800,
    )
    print("GROQ SUCCESS:", response.choices[0].message.content)
except Exception as e:
    import traceback
    print("GROQ ERROR:")
    traceback.print_exc()
