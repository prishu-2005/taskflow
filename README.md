# TaskFlow

TaskFlow is a full-stack task and project management platform built with FastAPI, SQLAlchemy, SQLite, Pydantic, and a vanilla HTML/CSS/JavaScript frontend.

## Tech Stack

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- HTML
- CSS
- JavaScript
- Optional Groq LLM integration

## Project Structure

```text
taskflow/
├── backend/
│   ├── ai_parser.py
│   ├── algorithms.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── styles.css
├── check_algorithms.py
├── README.md
├── .env
└── taskflow.db
```

## Running the Backend

Activate the virtual environment and run:

```bash
cd backend
uvicorn main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Running the Frontend

Open another terminal:

```bash
cd frontend
python -m http.server 5500
```

The frontend is available at:

```text
http://127.0.0.1:5500
```

The frontend communicates with the real FastAPI backend.

---

# Section 1 — Core Backend

TaskFlow provides CRUD operations for users, projects, and tasks.

## Users

- `GET /users`
- `POST /users`

## Projects

- `GET /projects`
- `POST /projects`

## Tasks

- `GET /tasks`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

## Project Statistics

```text
GET /projects/statistics
```

This endpoint returns task counts for each project.

---

# Section 2 — Algorithms

TaskFlow implements the required sorting and searching algorithms without relying on Python's built-in sorting or searching functions for the algorithmic endpoints.

## Insertion Sort

`insertion_sort(records, key)` sorts records in place using insertion sort.

Time complexity:

- Best case: O(n)
- Average case: O(n²)
- Worst case: O(n²)

## Binary Search

`binary_search(sorted_records, target_value, key)` searches a sorted list using binary search.

Time complexity:

- Best case: O(1)
- Average case: O(log n)
- Worst case: O(log n)

Binary search requires the records to be sorted first.

## Linear Search

`linear_search(records, target_value, key)` searches records sequentially.

Time complexity:

- Best case: O(1)
- Average case: O(n)
- Worst case: O(n)

## Comparison Counting

The implementation also provides:

- `insertion_sort_count`
- `binary_search_count`
- `linear_search_count`

These functions count key comparisons so the algorithms can be compared without relying on machine-dependent wall-clock timing.

## Search Endpoint

```text
GET /tasks/search?title=<title>&algo=binary
GET /tasks/search?title=<title>&algo=linear
```

The `binary` option sorts the searchable records using the custom insertion sort before performing binary search.

The `linear` option performs a sequential search.

An exact title match returns the task. If no matching task exists, the endpoint returns HTTP 404.

## Sorted Tasks Endpoint

```text
GET /tasks/sorted
```

This endpoint sorts tasks alphabetically by title using the custom insertion sort implementation.

## Priority Sorting

The tasks endpoint also supports:

```text
GET /tasks?sort=priority
```

Priority ordering is:

```text
low < medium < high
```

and the ordering is produced using the custom insertion sort implementation.

## Benchmark Results

The benchmark/check script was run for `n = 100`, `500`, and `1000`.

| n | Insertion Sort Comparisons | Binary Search Comparisons | Linear Search Comparisons |
|---:|---:|---:|---:|
| 100 | 4950 | 6 | 51 |
| 500 | 124750 | 8 | 251 |
| 1000 | 499500 | 9 | 501 |

The results show the expected growth patterns:

- Insertion sort grows quadratically for the tested worst-case input.
- Binary search grows logarithmically.
- Linear search grows linearly.

Run the checks with:

```bash
python check_algorithms.py
```

The current checks produce:

```text
PASS: correctness checks

Benchmark comparison counts
n=100: insertion_sort=4950, binary_search=6, linear_search=51
n=500: insertion_sort=124750, binary_search=8, linear_search=251
n=1000: insertion_sort=499500, binary_search=9, linear_search=501

ALL CHECKS PASSED
```

---

# Section 3 — AI Quick-Add

## Prompting Technique

The AI Quick-Add feature is modeled on **zero-shot prompting**. The system message directly describes the expected parsing behavior and output structure, while the user's task description is supplied as the user message. No examples are required in the prompt.

Zero-shot prompting keeps the prompt relatively short, which reduces token usage and makes the system easier and cheaper to run. It is suitable for this task because the expected output is highly structured: a title, one of three priority values, and an optional due-date hint.

The repository also contains a deterministic rule-based mock parser. This guarantees reliable and repeatable results without requiring an API key or paid service. Groq can optionally be enabled through `USE_REAL_LLM=true`, but the mock remains the fallback when Groq is disabled or unavailable.

## Quick-Add Endpoint

```text
POST /tasks/quick-add
```

Request:

```json
{
  "description": "Fix inventory bug next Friday, it's urgent",
  "project_id": 1
}
```

The endpoint parses the description and creates a real task in the existing `tasks` table.

The endpoint uses the same SQLAlchemy database session/dependency as the rest of the backend.

## Mock Parser Rules

The deterministic mock parser:

1. Uses a lower-cased copy of the description for keyword matching.
2. Determines priority in this order:
   - `urgent` or `asap` → `high`
   - `whenever` or `low priority` → `low`
   - otherwise → `medium`
3. Determines the due-date hint in the required order:
   - `today`
   - `tomorrow`
   - `next week`
   - `next monday` through `next sunday`
   - `monday` through `sunday`
4. Removes all matching priority keywords from the original-cased description.
5. Removes every occurrence of the matched date phrase.
6. Uses `Untitled task` when the resulting title is empty.

The mock uses no network calls and requires no API key.

## Mock Parser Examples

### Example 1

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

### Example 2

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

### Example 3

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

### Example 4

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

### Example 5

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

## Optional Groq Integration

Groq integration is optional and disabled by default.

Set:

```text
USE_REAL_LLM=true
```

and provide:

```text
GROQ_API_KEY=<your-key>
```

When Groq is disabled or the API key is unavailable, the deterministic mock parser is used automatically.

Therefore, the Quick-Add feature works without an API key or paid service.

The real-LLM path uses a role-based message structure:

```text
system → parsing instructions
user → task description
```

The mock parser remains the default grading path.

## Validation

Before a Quick-Add task is written to the database, the generated task object is validated using the Pydantic `TaskResponse` model.

A nonexistent project returns HTTP 422 and no task is created.

Malformed Quick-Add input is rejected with HTTP 422 validation details.

---

# Frontend

The frontend is implemented using vanilla HTML, CSS, and JavaScript.

It communicates with the real backend API and provides:

- API connection status
- Task statistics
- Project statistics
- Create Task form
- AI Quick-Add form
- Task search
- Task sorting
- Task deletion
- Task list display
- Project display

No task data is hard-coded into the frontend.

## Frontend URL

```text
http://127.0.0.1:5500
```

## Backend URL

```text
http://127.0.0.1:8000
```

---

# API Endpoint Summary

## Users

- `GET /users`
- `POST /users`

## Projects

- `GET /projects`
- `POST /projects`
- `GET /projects/statistics`

## Tasks

- `GET /tasks`
- `GET /tasks?sort=priority`
- `POST /tasks`
- `POST /tasks/quick-add`
- `GET /tasks/search`
- `GET /tasks/sorted`
- `GET /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

## Documentation

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```