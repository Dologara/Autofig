# ✅ Milestone 1 – Core CLI

## 🧠 Goal

Build the core CLI-based engine that:
- Accepts structured YAML input
- Merges global and device-specific config
- Selects a Jinja2 template per device
- Renders and saves CLI configuration output

---

## 📦 Output

- Fully working CLI prototype
- Input: `.yaml` file
- Output: `.txt` config per device in `/outputs/`
- Command:
  ```bash
  python main.py --input inputs/lab.yaml
```
## 🔧 Key Components

|Module|Description|
|---|---|
|`input_loader.py`|Loads and validates YAML input|
|`config_merger.py`|Combines global + device config|
|`generator.py`|Loads Jinja2 templates, renders config|
|`cli/main.py`|Entry-point, handles CLI args|
|`templates/`|Contains vendor-specific Jinja2 files|
|`outputs/`|Stores rendered `.txt` configs|

---

## 📋 Tasks

-  Design folder structure (`core/`, `cli/`, `inputs/`, `outputs/`)
    
-  Write and test `load_yaml()`
    
-  Write merge logic in `config_merger.py`
    
-  Create `generator.py` with Jinja2 logic
    
-  Build CLI runner in `main.py`
    
-  Create initial templates: `cisco_router.j2`, `cisco_l2_switch.j2`
    
-  Add test input YAMLs under `/inputs/`
    
-  Confirm sample `.txt` outputs match expectations
    

---

## 🧪 Testing

Test scenarios:

- ✅ Valid full input (router + switch)
    
- ⚠️ Missing optional global block (use defaults)
    
- ❌ Invalid YAML (catch syntax or structure errors)
    
- ✅ Device overrides global SSH settings
    

---

## 🔗 Dependencies

- `[[Template_Design_Principles]]`
    
- `[[Jinja2_Syntax]]`
    
- `[[Field_Mapping_Reference]]`
    
- `[[Global_vs_Device_Inputs]]`
    

---

## 🧭 Status

🎯 In Progress → Complete when `main.py` can generate per-device config from any valid YAML in `/inputs/`.

Once this milestone is complete, we move to:

- `Milestone 2 - API Server`
    
- `Milestone 3 - Linux Deployment`
    
