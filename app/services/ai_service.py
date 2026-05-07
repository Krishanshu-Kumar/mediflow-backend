import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("AI_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",
)

MODELS = {
    "general": os.getenv("AI_MODEL_GENERAL", "llama3.2:3b"),
    "coder": os.getenv("AI_MODEL_CODER", "qwen2.5-coder:3b"),
}

def chat(
    prompt: str,
    system_prompt: str = "You are a precise, helpful assistant.",
    model: str = "general",
    temperature: float = 0.7,
) -> str:
    response = client.chat.completions.create(
        model=MODELS[model],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content