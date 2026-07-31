import json
from groq import Groq, APIConnectionError, RateLimitError, APIStatusError
from pydantic import ValidationError
from .config import GROQ_API_KEY, MODEL_NAME
from .logger import setup_logger
from .chunking import chunk_text
from .prompts import build_chunk_summary_prompt, build_final_summary_prompt
from .models import DocumentSummary

CHUNK_THRESHOLD = 8000

client = Groq(api_key=GROQ_API_KEY)
logger = setup_logger()


def call_llm_for_text(system_prompt: str, user_prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise Exception("Rate limit exceeded. Please try again shortly.") from e
    except APIConnectionError as e:
        logger.error(f"API connection error: {e}")
        raise Exception("Could not connect to the AI service. Check your internet connection.") from e
    except APIStatusError as e:
        logger.error(f"API status error: {e}")
        raise Exception("An error occurred while generating the summary.") from e

    return response.choices[0].message.content


def call_llm_for_json(system_prompt: str, user_prompt: str) -> dict:
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        result = json.loads(response.choices[0].message.content)
        validated = DocumentSummary(**result)
    except RateLimitError as e:
        logger.error(f"Rate limit error: {e}")
        raise Exception("Rate limit exceeded. Please try again shortly.") from e
    except APIConnectionError as e:
        logger.error(f"API connection error: {e}")
        raise Exception("Could not connect to the AI service. Check your internet connection.") from e
    except APIStatusError as e:
        logger.error(f"API status error: {e}")
        raise Exception("An error occurred while generating the summary.") from e
    except json.JSONDecodeError as e:
        logger.error(f"AI response could not be parsed as JSON: {e}")
        raise Exception("The AI response could not be parsed. Please try again.") from e
    except ValidationError as e:
        logger.error(f"AI response missing required fields: {e}")
        raise Exception("The AI response was incomplete. Please try again.") from e

    return validated.model_dump()

def summarize_document(text: str) -> dict:
    if len(text) <= CHUNK_THRESHOLD:
        system_prompt, user_prompt = build_final_summary_prompt(text)
        return call_llm_for_json(system_prompt, user_prompt)
    else:
        chunks = chunk_text(text, max_chars=CHUNK_THRESHOLD)
        chunk_summaries = []

        for chunk in chunks:
            system_prompt, user_prompt = build_chunk_summary_prompt(chunk)
            summary = call_llm_for_text(system_prompt, user_prompt)
            chunk_summaries.append(summary)

        combined = "\n\n".join(chunk_summaries)
        system_prompt, user_prompt = build_final_summary_prompt(combined)
        return call_llm_for_json(system_prompt, user_prompt)


def generate_stream(system_prompt: str, user_prompt: str):
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            yield content


def build_markdown_summary(document_summary: dict) -> str:
    md = f"# Document Summary\n\n"
    md += f"## Executive Summary\n\n{document_summary['executive_summary']}\n\n"

    md += "## Key Points\n\n"
    for point in document_summary["bullet_points"]:
        md += f"- {point}\n"
    md += "\n"

    md += "## Key Takeaways\n\n"
    for takeaway in document_summary["key_takeaways"]:
        md += f"- {takeaway}\n"
    md += "\n"

    md += "## Action Items\n\n"
    for item in document_summary["action_items"]:
        md += f"- {item}\n"

    return md