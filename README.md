# TaskFlow — AI-Assisted Task Management Platform

A full-stack task and project management application built with **Python, FastAPI, SQLite, SQLAlchemy, HTML, CSS, and JavaScript**. TaskFlow helps users organize projects, manage tasks, track priorities, and create tasks quickly using natural-language descriptions.

[![Automated Tests](https://img.shields.io/badge/Tests-10%20passing-brightgreen)](../../actions)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Testing](https://img.shields.io/badge/Testing-pytest-orange)](https://docs.pytest.org/)

---

## Overview

TaskFlow combines a lightweight web interface with a Python backend and a relational database to provide task management functionality.

The project also explores algorithm implementation, natural-language task parsing, API validation, automated testing, and continuous integration.

## Features

* **Task Management:** Create, view, update, and delete tasks.
* **Project Management:** Organize tasks into projects.
* **AI Quick Add:** Convert natural-language descriptions into structured tasks using a rule-based parser, with optional Groq integration.
* **Task Priorities:** Organize tasks by low, medium, and high priority.
* **Task Search:** Search tasks using implemented search algorithms.
* **Task Sorting:** Organize tasks using custom sorting logic.
* **Dashboard Statistics:** Display task and project information.
* **Input Validation:** Validate incoming data using Pydantic.
* **REST API:** Handle application operations through FastAPI endpoints.
* **Automated Testing:** Test validation and API behavior using pytest.
* **Continuous Integration:** Run automated tests through GitHub Actions.

## Technology Stack

| Category                | Technologies                              |
| ----------------------- | ----------------------------------------- |
| Frontend                | HTML5, CSS3, JavaScript                   |
| Backend                 | Python, FastAPI                           |
| Database                | SQLite                                    |
| ORM                     | SQLAlchemy                                |
| Validation              | Pydantic                                  |
| Algorithms              | Custom search and sorting implementations |
| Testing                 | pytest, FastAPI TestClient                |
| CI                      | GitHub Actions                            |
| Optional AI Integration | Groq                                      |

## Project Structure

```text
TaskFlow/
├── .github/
│   └── workflows/
│       └── tests.yml
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
├── tests/
│   ├── conftest.py
│   └── test_taskflow.py
├── .gitignore
├── check_algorithms.py
└── README.md
```

## Getting Started

Follow these steps to run TaskFlow locally.

### Prerequisites

* Python 3.12 or newer
* Git
* A modern web browser

### 1. Clone the repository

```bash
git clone https://github.com/prishu-2005/taskflow.git
cd taskflow
```

### 2. Create a virtual environment

On Windows PowerShell:

```powershell
python -m venv taskflow-venv
.\taskflow-venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install fastapi "uvicorn[standard]" sqlalchemy pydantic pytest httpx
```

If you want to use the optional Groq integration, install its package:

```bash
python -m pip install groq
```

### 4. Start the backend

Open a terminal in the project root and run:

```powershell
cd backend
python -m uvicorn main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

Keep the backend terminal open while using the application.

### 5. Start the frontend

Open a **second terminal** in the project root.

If your virtual environment is active, you can use the same Python installation.

```powershell
python -m http.server 5500 --directory frontend
```

Open the application at:

`http://127.0.0.1:5500`

Keep both terminals running while using TaskFlow.

## AI Quick Add

TaskFlow includes a quick task creation feature that interprets natural-language descriptions.

For example:

**Input:**

```text
Finish resume tomorrow, urgent
```

**Parsed result:**

* Title: Finish resume
* Priority: High
* Due date: tomorrow

The rule-based parser identifies supported priority and date phrases. Optional Groq integration can provide an additional language-model-based parsing path when configured.

Date phrases such as `tomorrow` are currently represented as text by the rule-based parser; they should not be assumed to be normalized calendar dates.

## Algorithms

TaskFlow includes custom algorithm implementations for task searching and sorting.

The algorithm module is intended to demonstrate fundamental programming and problem-solving skills.

Relevant source files:

* `backend/algorithms.py` — algorithm implementations
* `check_algorithms.py` — algorithm checks and benchmarks

Algorithm performance depends on the implementation, input size, and data distribution. Consult the benchmark script and its actual output when reporting specific performance measurements.

## API Overview

The FastAPI backend exposes endpoints for managing users, projects, and tasks.

| Functionality                 | Endpoint                |
| ----------------------------- | ----------------------- |
| Create a user                 | `POST /users`           |
| Create a project              | `POST /projects`        |
| Retrieve projects             | `GET /projects`         |
| Create a task                 | `POST /tasks`           |
| Create a task using Quick Add | `POST /tasks/quick-add` |
| Search tasks                  | `GET /tasks/search`     |
| Retrieve sorted tasks         | `GET /tasks/sorted`     |

The API also includes additional task and project operations.

For the complete, interactive endpoint list, request schemas, and response examples, start the backend and visit:

`http://127.0.0.1:8000/docs`

## Automated Testing

TaskFlow includes automated tests for request validation and API functionality.

The current test suite contains **10 tests**, covering:

* Valid task input
* Task title whitespace trimming
* Rejection of blank task titles
* Rejection of invalid priorities
* Quick Add request validation
* Rejection of blank Quick Add descriptions
* Project creation
* Task creation
* Quick Add API behavior
* Invalid Quick Add requests

### Run the tests

From the project root, activate the virtual environment and run:

```bash
python -m pytest -v
```

The current local test result is **10 passed**.

### Test database isolation

The API tests use an isolated in-memory SQLite database through a test fixture. This keeps test operations separate from the application's normal database.

## Continuous Integration

TaskFlow uses GitHub Actions to execute automated tests on pushes to the `main` branch and pull requests targeting `main`.

Workflow configuration:

`.github/workflows/tests.yml`

The workflow:

1. Checks out the repository.
2. Sets up Python.
3. Installs dependencies.
4. Runs the pytest suite.
5. Reports the workflow result on GitHub.

View workflow runs in the repository's **Actions** tab.

## Future Improvements

Potential improvements include:

* Expand automated test coverage for search, sorting, deletion, and error handling.
* Add user authentication and authorization.
* Improve task filtering and dashboard analytics.
* Add more robust date parsing.
* Introduce a dependency lockfile or maintained dependency requirements.
* Improve deployment configuration and production error handling.
* Add additional integration tests.

## Author

**Priyanshi Suthar**

* GitHub: [@prishu-2005](https://github.com/prishu-2005)
* LinkedIn: [Priyanshi Suthar](https://www.linkedin.com/in/priyanshi-suthar-1115b2445/)

---

*TaskFlow is a portfolio project developed to practice full-stack development, API design, database integration, algorithms, automated testing, and continuous integration.*
