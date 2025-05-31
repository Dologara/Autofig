# Milestone 3 – Linux Deployment

## Goal

Ensure NetAutoGen can be:
- Cloned or downloaded onto any Linux machine
- Run via CLI or API without modification
- Installed and managed as a standalone local tool

This milestone prepares the project for real-world testing, labs, or small-scale use by engineers.

---

## Output

- A Linux-ready install process
- CLI executable via `main.py`
- Virtual environment + requirements.txt
- Optional: shell script (`run.sh`) or entry-point alias

---

## Recommended Directory Layout

```bash
netautogen/
├── cli/
├── core/
├── templates/
├── inputs/
├── outputs/
├── main.py
├── requirements.txt
├── README.md
├── run.sh   # optional helper script
```
## Tasks

-  Clean up folder structure
    
-  Add `requirements.txt` (Jinja2, PyYAML, FastAPI if needed)
    
-  Add basic `README.md` with usage instructions
    
-  Test CLI execution with `python main.py`
    
-  Confirm output saved to `/outputs/`
    
-  Write `run.sh` for simple execution (optional)
    
-  Document Linux setup instructions (venv, pip install)
    

---

## Testing Scenarios

|Scenario|Outcome|
|---|---|
|Clone repo and run CLI|✅ Configs generated successfully|
|Invalid Python version|❌ Warn and exit|
|Missing `requirements.txt`|❌ Pip install fails|
|Run from `/home/username/projects/`|✅ Relative paths still work|

---

## Considerations

- Target OS: Ubuntu/Debian (bash-compatible systems)
    
- Minimum: Python 3.8+
    
- Add `.gitignore` to exclude `__pycache__/`, `.vscode/`, etc.
    
- Check if FastAPI is optional or required for core logic
    

---

## Optional Enhancements

- `Makefile` for easy commands
    
- Systemd service to run API on boot
    
- `.deb` package generator (if project expands in future)
    

---

## Related Notes

- `[[Milestone 1 - Core CLI]]`
    
- `[[CLI_First_Design]]`
    
- `[[Folder_Structure]]`