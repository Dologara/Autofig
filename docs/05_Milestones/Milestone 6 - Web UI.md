# Milestone 6 – Web UI

## Goal

Build a simple browser-based frontend to:
- Upload or paste YAML input
- Trigger config generation via the API
- View or download the generated device configs

The UI will make the tool accessible to non-CLI users and allow quick testing or small-team usage.

---

## Output

- Frontend folder (e.g., `/web_ui/`)
- `index.html` or frontend framework (React/Vue/etc.)
- Upload + Submit YAML form
- Config download or preview area
- Connected to API from `Milestone 2`

---

## Tasks

- [x] Decide stack: simple HTML/JS, or React (preferred long-term)
- [x] Create UI layout: YAML input box, Submit button, Output area
- [ ] Connect UI to `/api/generate` via fetch or axios
- [ ] Add error handling for invalid YAML/API failure
- [ ] Add download button for `.txt` config output
- [ ] Optional: YAML validation before sending
- [ ] Optional: config preview in-browser

---

## Sample UI Flow

```text
[YAML Input Box] → [Submit] → [API POST] → [Show Config / Download]
```

## Suggested Tech Stack

|Component|Option|
|---|---|
|Framework|React (w/ Vite or Create React App)|
|HTTP client|Fetch or Axios|
|Deployment|Serve via FastAPI static files or standalone|
|Styling|Tailwind CSS or basic HTML/CSS|

---

## Testing

|Test Case|Outcome|
|---|---|
|Valid YAML → Submit → Output shows|✅|
|Malformed YAML → Submit → Error shown|✅|
|Backend unreachable → UI handles error|✅|
|Download click → File saves correctly|✅|

---

## Related Notes

- `[[Milestone 2 - API Server]]`
    
- `[[Output_Format]]`
    
- `[[YAML_Examples]]`
    
- `[[Frontend_Todo_List]]` (optional)
    

---

## Status

🛠 In Progress → Complete when:

- A working UI allows upload or paste → generate → download
    
- API is correctly triggered and handles input/output
    
- Local deployment on localhost:port is successful
    

---

## Future Features

- Login/auth integration
    
- Input field validation
    
- Predefined device templates
    
- Web-based YAML editor or wizard