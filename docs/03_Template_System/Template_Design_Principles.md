#  Template Design Principles

This document defines how the NetAutoGen project uses templating to transform structured input into vendor-specific network configuration files.

---

##  Why Use a Templating System?

- **Separation of concerns**: Keep logic (Python) separate from presentation (config output)
- **Modularity**: Easy to support multiple vendors or device types
- **Maintainability**: Updating CLI syntax doesn't affect logic
- **Reusability**: Common blocks like interface logic can be reused across templates

---

##  Tooling

- **Templating Engine**: [`Jinja2`](https://jinja.palletsprojects.com/)
- **Extension**: `.j2` files stored in `/templates/`
- **Rendered By**: `core/generator.py`
- **Input**: Merged per-device config (from `config_merger.py`)

---

##  Template File Structure

Each file in `/templates/` corresponds to a specific `device_type` + `vendor`.

Example:
##  Template Directory Structure

templates/  
├── cisco_router.j2  
├── cisco_l2_switch.j2  
├── cisco_l3_switch.j2


You select the template using:

```python
template = f"{vendor}_{device_type}.j2"
```
##  Core Design Principles

### 1.  One Template per Device Type

Keep each device type isolated.  
Do **not** combine logic for routers and switches in one template.

---

### 2.  One Device per Render Pass

Templates are rendered **per device**:

- Global config is merged with the device block
    
- All needed fields are available in one object
    
- Keeps logic clean — no deep conditional branching needed
    

---

### 3.  Flat Template Logic

Write clean and readable Jinja2:

- Avoid excessive `if` nesting
    
- Use `for` loops for lists (e.g., `interfaces`, `routes`)
    
- Use `{% if field is defined %}` for optional blocks
### 4.  Field Naming Consistency

Use input field names directly, without renaming inside the template.

`interface {{ interfaces[0].name }}  ip address {{ interfaces[0].ip }} {{ interfaces[0].mask }}`

---

### 5. Safe Defaults

Always check if optional fields exist:

`{% if interface.description %}  description {{ interface.description }} {% endif %}`

##  Example Output Sections

Typical router config template:


hostname {{ hostname }}

! Loop through interfaces
{% for interface in interfaces %}
interface {{ interface.name }}
{% if interface.ip %}
 ip address {{ interface.ip }} {{ interface.mask }}
{% endif %}
{% if interface.description %}
 description {{ interface.description }}
{% endif %}
{% if not interface.shutdown %}
 no shutdown
{% endif %}
!
{% endfor %}

! Static routes
{% for route in static_routes %}
ip route {{ route.destination }} {{ route.mask }} {{ route.next_hop }}
{% endfor %}

! SSH setup
ip domain-name {{ ssh.domain_name }}
username {{ ssh.username }} secret {{ ssh.password }}
crypto key generate rsa general-keys modulus {{ ssh.generate_rsa_bits | default(1024) }}

---

##  Future Template Structure

If templates grow more complex:

- Split into partials (e.g., `_interfaces.j2`, `_ssh_block.j2`)
    
- Use `{% include %}` or `{% macro %}` in Jinja2
    
- Create a `common/` folder for reusable components

---

##  Testing Templates

Each template should be tested with:

-  A complete YAML input file
    
-  A minimal YAML (test default behavior)
    
-  A broken YAML (test error handling)
    

Store these under:

- `/inputs/` — raw test YAMLs
    
- `/outputs/` — expected generated configs
    

---

##  Naming Convention

Use this structure:

`{vendor}_{device_type}.j2`

### Examples:

- `cisco_router.j2`
    
- `cisco_l2_switch.j2`
    
- `juniper_l3_switch.j2`
    

---

## 🔗 Related Notes

- [[Cisco_Router_Template]]
    
- [[Jinja2_Syntax]]
    
- [[generator]]