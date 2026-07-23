from dotenv import load_dotenv
from openai import OpenAI

from config import CHAT_MODEL

load_dotenv()

client = OpenAI()


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

    content = response.choices[0].message.content
    if content is None:
        raise ValueError("Model returned no content (possibly refused or filtered).")

    return content
