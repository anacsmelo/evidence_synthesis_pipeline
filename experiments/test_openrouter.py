import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
print("API KEY definida:", bool(api_key))

client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b:free",
    messages=[
        {"role": "user", "content": "Reply with the single word: OK"}
    ],
    max_tokens=100
)

print("Resposta bruta:", response)
print("Conteúdo:", response.choices[0].message.content)
