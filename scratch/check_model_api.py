import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

try:
    response = client.chat.completions.create(
        model="glm-4",
        messages=[{"role": "user", "content": "Hola, prueba."}],
        max_tokens=20
    )
    print("SUCCESS:", response.choices[0].message.content)
except Exception as e:
    print("ERROR:", e)
