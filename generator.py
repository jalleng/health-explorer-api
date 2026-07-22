import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHAT_MODEL = "gpt-4o-mini"


def build_prompt(question: str, chunks: list[str]) -> str:
    context = "\n".join(chunks)
    return (
        "You are a helpful assistant analyzing public health data. "
        "Use only the following context to answer the question. "
        "If the answer is not in the context, say so.\n\n"
        "Context:\n"
        f"{context}\n\n"
        f"Question: {question}"
    )


def generate(question: str, chunks: list[str]) -> str:
    prompt = build_prompt(question, chunks)

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content
