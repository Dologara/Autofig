# Autofig (NetAutoGen Planning Stage)

Autofig is a vendor-agnostic network configuration generator. It takes structured YAML inputs and uses Jinja2 templates to generate CLI configurations for various network devices.

---

## Project Status

- In early development
- Vault planning complete
- Folder structure initialized
- CLI and core logic in progress

---

## Directory Structure (Planned)

Autofig/
├── core/ # Core Python logic (input loading, rendering, etc.)
├── templates/ # Jinja2 templates for routers, switches, etc.
├── inputs/ # YAML input files
├── outputs/ # Generated device configs
├── cli/ # CLI entry point scripts
├── scratch/ # Local testing and prototypes
├── docs/ # Obsidian vault documentation
├── tests/ # Unit and integration tests


---

## Requirements

- Python 3.10+
- Dependencies in `requirements.txt`:
  - `pyyaml`
  - `jinja2`
  - `click`
  - `rich`

---

## Docs

All design notes and plans are maintained in an [Obsidian vault](docs/) (markdown-based).

---

## Roadmap

Planned milestones can be found in:  
`docs/05_Milestones/`
