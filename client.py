import os
import openai

openai.api_key = os.getenv("OPENAI_API_KEY", "my-api")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

FALLBACK_TEXT = "I'm sorry but the system is not available right now. Please try again later."

def respond_with_openai(messages):
    """
    messages: list of dicts like {"role": "system"|"user"|"assistant", "content": str}
    Returns assistant text, or a friendly fallback on any error.
    """
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages
        )
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return FALLBACK_TEXT

def respond_about_me(facts_dict, question):
    """
    Answer using ONLY provided user facts. If unknown, say you don't know.
    """
    facts_text = "\n".join(f"- {k}: {v}" for k, v in facts_dict.items()) or "- (no facts stored)"
    system = (
        "You are a personal profile assistant. "
        "Answer questions strictly and only from the provided user facts. "
        "If the answer is not present, reply: \"Good questions! Unfortunately, I don't have an answer right now. I'll get back later!\" "
        "Be concise and accurate."
    )
    content = (
        "User Facts:\n"
        f"{facts_text}\n\n"
        f"Question: {question}"
    )
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": content}
            ]
        )
        return resp["choices"][0]["message"]["content"]
    except Exception:
        return "I'm sorry but the system is not available right now. Please try again later."
