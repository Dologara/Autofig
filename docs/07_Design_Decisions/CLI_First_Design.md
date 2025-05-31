#  CLI_First — Interface Strategy

##  Decision

The NetAutoGen project is designed as a **CLI-first application**, with web or API interfaces to be layered on top later.

---

##  Why CLI First?

### 1.  Faster Development & Debugging
- Easier to test logic, functions, and config output without UI complexity
- Output is visible and inspectable immediately in terminal

### 2.  Focus on Core Logic First
- Templates, parsing, merging, and rendering can be built independently of UI concerns
- Keeps system modular and scriptable

### 3.  Easier Automation & Testing
- CLI interfaces work well with unit tests, CI/CD pipelines
- Can be run headlessly in labs, batch jobs, scripts

### 4.  Friendlier for Network Engineers
- Familiar to users used to CLI tools like Ansible, Nornir, Python scripts
- No need for browser or API token setup in early usage

---

##  Long-Term Plan

The CLI is the **foundational interface** that all future layers will use internally.

### Future interfaces (built on top):
-  Web UI (FastAPI/Flask frontend)
-  REST API for programmatic access
-  Visual form-based YAML builder (optional)

---

##  CLI Command Design Goals

- Simple, clear arguments:
  ```bash
  python main.py --input inputs/core_lab.yaml --output outputs/
- Support for:
    
    - `--dry-run`
        
    - `--device <hostname>`
        
    - `--template-preview`
        
- Error messages should be readable, not just stack traces
    
- Future: `--web` flag could launch a local dashboard
```

##  Notes

- This decision aligns with the Unix philosophy: **"Do one thing well"**
    
- CLI-first tools are easier to integrate into other systems (e.g., Jenkins, GitHub Actions)
    
- Also allows teammates to work independently — UI team doesn't block logic dev
    

---

##  Related Notes

- [[Template_Design_Principles]]
    
- [[Output_Format]]
    
- [[Extensibility_Plan]]
    

