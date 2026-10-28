
import re
import os
from dotenv import load_dotenv

load_dotenv()

USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def parse_task_description(description: str):
    working = description.lower()

    # Priority detection
    if re.search(r"\b(?:urgent|urgently|asap)\b", working):
        priority = "high"
    elif re.search(r"\bwhenever\b|\blow\s+priority\b", working):
        priority = "low"
    else:
        priority = "medium"

    # Due-date hints: check longer phrases before shorter ones
    date_phrases = [
        "next monday",
        "next tuesday",
        "next wednesday",
        "next thursday",
        "next friday",
        "next saturday",
        "next sunday",
        "next week",
        "tomorrow",
        "today",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]

    due_date_hint = None

    for phrase in date_phrases:
        pattern = r"\b" + re.escape(phrase) + r"\b"
        if re.search(pattern, working):
            due_date_hint = phrase
            break

    # Remove priority phrases as complete words, case-insensitively
    title = description

    priority_patterns = [
        r"\blow\s+priority\b",
        r"\bwhenever\b",
        r"\burgently\b",
        r"\burgent\b",
        r"\basap\b",
    ]

    for pattern in priority_patterns:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)

    # Remove the detected date phrase as a complete phrase
    if due_date_hint:
        date_pattern = r"\b" + re.escape(due_date_hint) + r"\b"
        title = re.sub(date_pattern, "", title, flags=re.IGNORECASE)

    # Clean up leftover punctuation and whitespace
    title = re.sub(r"\s+", " ", title)
    title = re.sub(r"\s*[,.;!?]+\s*$", "", title)
    title = re.sub(r"^[,.;!?]+\s*", "", title)
    title = title.strip()
    if not title:
        title = "Untitled task"

    return {
        "title": title,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }


def parse_with_groq(description: str):
    if not USE_REAL_LLM or not GROQ_API_KEY:
        return None

    from groq import Groq
    import json

    client = Groq(api_key=GROQ_API_KEY)

    system_prompt = """
You parse a task description into JSON.

Return exactly these fields:
- title: a short task title
- priority: exactly one of low, medium, high
- due_date_hint: a date phrase or null

Do not include any other fields.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("Groq returned an empty response")

    result = json.loads(content)

    return result

