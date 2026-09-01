# Autofig

Network configuration generator for learning labs. Takes network topologies (YAML or interactive form) and generates Cisco IOS configurations.

## Quick Start

```bash
git clone https://github.com/Dologara/Autofig.git
cd Autofig
pip install -e .

# Interactive form
autofig build

# Generate from YAML
autofig generate --input topology.yaml --output ./configs
```

## What It Does

Define a network topology and automatically generate Cisco IOS configurations for routers, switches, and multilayer switches. Supports both YAML input and interactive form-based topology building.

## Project Status

**Phase 1: Complete**
- Interactive topology builder with validation
- YAML generation and parsing
- Cisco configuration rendering
- CLI interface

**Phase 2: Complete**
- SQLite database persistence
- CLI commands for stored topologies

82/82 tests passing.

**Phase 3: Planned**
- FastAPI wrapper
- Web UI
- Form-based YAML builder

**Phase 4: Roadmap**
- Multi-vendor support (Juniper, Arista)
- NetBox integration

## Requirements

- Python 3.10+
- pyyaml
- jinja2
- click

## Docs

Architecture and design notes are in `/docs/`.

## License

MIT
