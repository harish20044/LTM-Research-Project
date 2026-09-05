from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

client = Groq(api_key=os.environ["GROQ_API_KEY"])

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Reply with exactly: pipeline check ok"}],
)

print(response.choices[0].message.content)
