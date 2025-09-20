import os
from openai import OpenAI

def openai_summarize(text: str, model: str = "gpt-5-nano") -> str:
    client = OpenAI(api_key=os.environ.get("API_KEY"))
    response = client.responses.create(
        model=model,
        input=(
            "You are a concise scientific summarizer. "
            "Write 3 sentences, neutral tone, no hype, no emojis. "
            "If input is only a title, rephrase it clearly without inventing details.\n\n"
            f"Input: {text}"
        ),
    )

    return response.output_text.strip()
