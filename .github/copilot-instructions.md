# Copilot Instructions

## Project Structure Rules

### No Code Files in the Project Root

- **Never** dump code files (e.g., `.py`, `.js`, `.ts`, `.java`, `.cs`, `.go`, etc.) directly into the project root directory.
- Before creating any code file, determine the appropriate subfolder based on its purpose (e.g., `src/`, `scripts/`, `tests/`, `lib/`, `api/`, etc.).
- If a suitable folder does not already exist, create one with a clear, descriptive name before placing the file.
- Configuration files (e.g., `.gitignore`, `package.json`, `requirements.txt`) and documentation (e.g., `README.md`) are acceptable in the root.

### Examples

| ❌ Don't                         | ✅ Do                                  |
| -------------------------------- | -------------------------------------- |
| `/app.py`                        | `/src/app.py`                          |
| `/helper.js`                     | `/lib/helper.js`                       |
| `/test_main.py`                  | `/tests/test_main.py`                  |

---

## Read-Only Folders

### `workshop/` — Challenge Instructions (Do Not Touch)

- The `workshop/` folder is a **read-only** directory containing challenge instructions and reference material for the workshop.
- **Do not** read, reference, or use any content from `workshop/` for context, planning, or code generation — unless the user **explicitly** asks you to look at it.
- **Do not** create, modify, or delete any files inside `workshop/`.
- If the user references a challenge or task, wait for them to provide the relevant details or explicitly point you to `workshop/` before accessing it.

---

## Coding Conventions

### Async & Route Handlers

- Use `async/await` exclusively for all route handlers. Do not use synchronous `def` for endpoints.

### RESTful API Design

- Follow RESTful naming conventions for all endpoints (plural nouns, proper HTTP verbs).
- Return Pydantic models directly from endpoints — FastAPI handles serialization automatically.
- Use Pydantic models for input validation on **all** endpoints that accept request bodies.

### Error Handling

- Raise `HTTPException` with appropriate status codes for all error conditions.
- Do not return raw error dictionaries; always use FastAPI's exception mechanism.

### Data Formats & Identifiers

- Use **UUID v4** for all generated identifiers (e.g., resource IDs, correlation IDs).
- All dates must be **ISO 8601** formatted strings (e.g., `2026-05-14T12:00:00Z`).

### Python Style

- Use Python type hints on **all** function signatures (parameters and return types).
- Follow **PEP 8** naming conventions:
  - `snake_case` for functions and variables
  - `PascalCase` for classes and Pydantic models
  - `UPPER_SNAKE_CASE` for constants
