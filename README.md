# TaskFlow

TaskFlow is a full-stack task and project management API.

## Backend

The backend is built with:

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Run the backend

Activate the virtual environment and run:

```bash
uvicorn main:app --reload

## Section 3 — AI Quick-Add

### Prompting Technique

The AI Quick-Add feature is modeled on **zero-shot prompting**. The system message directly describes the expected parsing behavior and output structure, while the user's task description is supplied as the user message. No examples are required in the prompt.

Zero-shot prompting keeps the prompt relatively short, which reduces token usage and makes the system easier and cheaper to run. It is suitable for this task because the expected output is highly structured: a title, one of three priority values, and an optional due-date hint.

The repository also contains a deterministic rule-based mock parser. This guarantees reliable and repeatable results without requiring an API key or paid service. Groq can optionally be enabled through `USE_REAL_LLM=true`, but the mock remains the fallback when Groq is disabled or unavailable.

### Quick-Add Endpoint

`POST /tasks/quick-add`

Request:

```json
{
  "description": "Fix inventory bug next Friday, it's urgent",
  "project_id": 1
}
```

The endpoint parses the description and creates a real task in the existing `tasks` table.

### Mock Parser Examples

#### Example 1

Input:

```text
This is urgent, mark it ASAP please
```

Output:

```json
{
  "title": "This is , mark it please",
  "priority": "high",
  "due_date_hint": null
}
```

#### Example 2

Input:

```text
 
```

Output:

```json
{
  "title": "Untitled task",
  "priority": "medium",
  "due_date_hint": null
}
```

#### Example 3

Input:

```text
Finish the report next Friday, it's urgent
```

Output:

```json
{
  "title": "Finish the report , it's",
  "priority": "high",
  "due_date_hint": "next friday"
}
```

#### Example 4

Input:

```text
tomorrow review tomorrow
```

Output:

```json
{
  "title": "review",
  "priority": "medium",
  "due_date_hint": "tomorrow"
}
```

#### Example 5

Input:

```text
Whenever possible update the inventory next Monday
```

Output:

```json
{
  "title": "possible update the inventory",
  "priority": "low",
  "due_date_hint": "next monday"
}
```

### Optional Groq Integration

Groq integration is optional and disabled by default.

Set:

```text
USE_REAL_LLM=true
```

and provide:

```text
GROQ_API_KEY=<your-key>
```

When Groq is disabled or the API key is unavailable, the deterministic mock parser is used automatically. Therefore, the feature works without an API key or paid service.
