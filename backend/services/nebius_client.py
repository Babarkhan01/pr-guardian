import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(base_url=os.getenv("NEBIUS_BASE_URL"),
                api_key=os.getenv("NEBIUS_API_KEY"))

if __name__ == "__main__":
    models = [m.id for m in client.models.list().data if "nemotron" in m.id.lower()]
    print("Nemotron models on your account:")
    for m in models:
        print(" ", m)
