# Why_YAML — Input Format Decision

##  Decision

NetAutoGen uses **YAML** (`.yaml`) as the input format for both global and device-specific configurations.

This format was chosen for its **human readability**, ease of writing, and compatibility with structured configuration use cases.

---

##  Why YAML?

### 1.  Human-Friendly
- Simple, clean syntax — ideal for network engineers
- No extra characters, brackets, or quotes needed for most fields
- Easier to hand-write and edit compared to JSON or XML

### 2.  Structured & Hierarchical
- Naturally represents nested structures like:
  - Interfaces
  - SSH blocks
  - VLAN lists
  - Per-device dictionaries

### 3.  Compatible with Jinja2 + Python
- Cleanly loads into Python dictionaries with `PyYAML`
- Works directly with Jinja2 templating without transformation

### 4.  Diff-Friendly for Git
- Smaller diffs for changes (e.g., 1-line edit vs JSON reformatting)
- Easier to track and version control

---

##  Alternatives Considered

| Format | Why Not |
|--------|---------|
| **JSON** | More verbose, harder to hand-edit, trailing comma issues |
| **XML** | Overkill, noisy, not modern in DevOps workflows |
| **Form-based UI** | Adds complexity, not CLI-friendly, requires web stack |
| **CSV/INI** | Not hierarchical enough — can’t express interfaces or VLAN blocks cleanly |

---

##  Example YAML Snippet

```yaml
vendor: cisco
routing: static

ssh:
  enable: true
  username: admin
  password: net123
  domain_name: lab.local

vlans:
  - id: 10
    name: Users

devices:
  - hostname: SW1
    device_type: l2_switch
    interfaces:
      - name: Gi0/1
        mode: access
        vlan: 10
```

##  Design Notes

- One YAML file can represent an entire lab (multiple devices + global settings)
    
- Default location: `/inputs/`
    
- File extensions: `.yaml` preferred over `.yml` for consistency
    

---

##  Future Considerations

- Support for JSON if needed (`.json` → parsed the same in Python)
    
- YAML form builder (web GUI) that exports a ready-to-run `.yaml`
    
- Linting rules to validate input before config generation
    

---

##  Related Notes

- [[General_vs_Device_Fields]]
    
- [[Input_Loader]]
    
- [[Field_Mapping_Reference]]
