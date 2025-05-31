#  Templating Strategy

##  Decision

NetAutoGen uses **Jinja2 templates** to generate device configurations from YAML input. Each device type (e.g., router, L2 switch) has its own dedicated template file.

This approach prioritizes **readability**, **modularity**, and **vendor-specific logic separation**.

---

##  Why Jinja2?

- Mature, stable, widely supported templating engine
-  Clean syntax for loops, conditionals, and defaults
-  Used in many network automation tools (e.g., Ansible)
-  Python-native — no external runtime or toolchain

---

##  Template Layout

Directory structure:

templates/  
├── cisco_router.j2  
├── cisco_l2_switch.j2  
├── cisco_l3_switch.j2


Template file is selected at runtime based on:

```python
template = f"{vendor}_{device_type}.j2"
```

This makes the system plug-and-play for adding new vendors or device types.

##  Design Principles

### 1.  One Template per Device Type

- Keep templates isolated — no combined logic for routers and switches.
    
- Easier to test, debug, and evolve separately.
    

### 2.  One Device per Render

- Templates receive a fully merged device config (global + device).
    
- Keeps template logic flat — no deep merging logic inside the template.
    

### 3.  Flat, Minimal Logic

- Prefer loops over nested `if` blocks.
    
- Use `{% if field is defined %}` to handle optional input.
    
- Keep templates readable for network engineers.
    

### 4.  Field Naming Consistency

- Template uses fields exactly as defined in YAML.
    
- No renaming or aliasing inside the template.
    
- Enables 1:1 mapping for traceability.
    

### 5.  Safe Defaults

- Use filters like `| default(...)` to handle missing input gracefully.
    
- Avoid hard fails in output — fallback values improve UX.

## Typical Template Structure

hostname {{ hostname }}

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

{% for route in static_routes %}
ip route {{ route.destination }} {{ route.mask }} {{ route.next_hop }}
{% endfor %}

{% if ssh.enable %}
ip domain-name {{ ssh.domain_name }}
username {{ ssh.username }} secret {{ ssh.password }}
crypto key generate rsa general-keys modulus {{ ssh.generate_rsa_bits | default(1024) }}
{% endif %}

##  Extensibility Plan

|Scenario|Solution|
|---|---|
|Add new vendor|Create `vendor_device_type.j2`|
|Add reusable blocks|Use `{% include 'partials/ssh_block.j2' %}`|
|Advanced logic (reused across templates)|Use Jinja2 macros or filters|

Planned support for:

- `templates/common/` for shared components
    
- Nested includes or macros for DRY logic
    

---

##  Template Testing Strategy

- Each template tested with:
    
    -  Full YAML (standard case)
        
    -  Minimal YAML (tests fallback logic)
        
    -  Invalid YAML (tests handling/missing fields)
        
- Inputs go under `/inputs/`
    
- Rendered configs under `/outputs/`
    
- Template changes should be tracked with versioned test files
    

---

##  Alternatives Considered

|Option|Reason for Rejection|
|---|---|
|Single giant template with `if device_type ==`|Becomes unmaintainable|
|Pure Python string rendering|Too manual, no templating benefits|
|External tools (e.g., Ansible J2 roles)|Adds complexity, not portable or standalone|

---

##  Related Notes

- [[Jinja2_Syntax]]
    
- [[Template_Design_Principles]]
    
- [[Generator]]
