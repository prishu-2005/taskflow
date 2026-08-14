import re
import os
from dotenv import load_dotenv

load_dotenv()
USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "true"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")



def parse_task_description(description: str):
    working = description.lower()

    # Priority
    if "urgent" in working or "asap" in working:
        priority = "high"
    elif "whenever" in working or "low priority" in working:
        priority = "low"
    else:
        priority = "medium"

    # Due-date hint
    date_phrases = [
        "today",
        "tomorrow",
        "next week",
        "next monday",
        "next tuesday",
        "next wednesday",
        "next thursday",
        "next friday",
        "next saturday",
        "next sunday",
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
        if phrase in working:
            due_date_hint = phrase
            break

    # Remove every priority keyword from the original-cased description
    title = description

    priority_keywords = [
        "urgent",
        "asap",
        "whenever",
        "low priority",
    ]

    for keyword in priority_keywords:
        title = re.sub(
            re.escape(keyword),
            "",
            title,
            flags=re.IGNORECASE,
        )

    # Remove every occurrence of the matched date phrase
    if due_date_hint:
        title = re.sub(
            re.escape(due_date_hint),
            "",
            title,
            flags=re.IGNORECASE,
        )

    title = re.sub(r"\s+", " ", title).strip()

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
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": description,
            },
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("Groq returned an empty response")

    result = json.loads(content)

    return result