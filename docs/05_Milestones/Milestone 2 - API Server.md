# Milestone 2 – API Server

## Goal

Wrap the existing CLI logic into a minimal **FastAPI server** to expose NetAutoGen's core features through a RESTful API.

This enables external tools (or a future Web UI) to:
- Upload YAML input
- Trigger config generation
- Download or view generated configs

---

## Output

- `app.py` FastAPI server entry point
- `/api/generate` POST endpoint
- Support for:
  - File upload OR raw JSON/YAML input
  - Return rendered config in response
  - Optional write-to-file toggle

---

## Core API Features

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/generate` | POST | Accepts input YAML, returns rendered config |
| `/api/devices` | GET (optional) | List supported device types |
| `/api/templates/{device}` | GET (optional) | Return raw Jinja2 template |

---

## Tasks

- [ ] Set up FastAPI project structure
- [ ] Move core CLI logic into reusable Python functions
- [ ] Create `POST /api/generate` endpoint
- [ ] Accept YAML via file upload and `application/json`
- [ ] Add basic error handling (e.g., invalid YAML)
- [ ] Return rendered config as raw text or downloadable file
- [ ] Write example cURL/Postman test
- [ ] Document API usage

---

## Suggested Folder Structure

/web/  
├── app.py  
├── routes/  
│ └── generate.py  
├── utils/  
│ └── file_handler.py


---

## Security Notes

- No auth in MVP — secure in Milestone 4
- Limit file size / input length
- Sanitize filenames or in-memory only

---

## Testing Scenarios

- Valid YAML input via JSON body
- Upload `.yaml` file
- Malformed input returns error
- Output returned inline or as `.txt` attachment
- Response includes CLI config and metadata (e.g., device hostname)

---

## Related Notes

- `[[CLI_First_Design]]`
- `[[Output_Format]]`
- `[[Extensibility_Plan]]`
- `[[Milestone 7 - Web UI]]`

---

## Status

In Progress → Ready when server can accept YAML input and return working config for at least one device.

Blocks:
- Needs Milestone 1 logic to be modularized
- Should be in place before Milestone 7 (Web UI)
