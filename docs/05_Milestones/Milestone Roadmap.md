# Milestone Roadmap

This file tracks all major phases in the evolution of NetAutoGen — from its CLI-based origin to a fully API-backed, Web UI-integrated configuration automation system.

---

## Project Flow Summary

Each milestone builds upon the last in terms of complexity, usability, and extensibility.

---

## Roadmap Table

| ID | Milestone | Description | Status |
|----|-----------|-------------|--------|
| 1. | [[Milestone 1 - Core CLI]] | Core engine: YAML input → CLI config | In Progress |
| 2. | [[Milestone 2 - Linux Deployment]] | Install/run project in Linux environment | In Progress |
| 3. | [[Milestone 3 - API Server]] | Wrap CLI logic with FastAPI | Planned |
| 4. | [[Milestone 4 - Docs & Collaboration]] | Project docs, contributor structure | In Progress |
| 5. | [[Milestone 5 - Template Expansion]] | Add vendors, features, devices | Planned |
| 6. | [[Milestone 6 - Web UI]] | Browser interface for input + output | Planned |
| 7. | [[Milestone 7 - Security]] | Add token auth, safe input handling | Planned |
| 0. | [[Optional Features]] | Bonus tools and advanced use cases | Future |

---

## Supporting Design Decisions

- `[[CLI_First_Design]]` — Why CLI matters early
- `[[Templating_Strategy]]` — How templates scale
- `[[Global_vs_Device_Inputs]]` — Input separation model
- `[[Output_Format]]` — Why we generate plain-text
- `[[Extensibility_Plan]]` — Future vendors and web expansion

---


## Tip

Each milestone file includes:
- Goals
- Tasks
- Output targets
- Dependencies
- Links to design notes

Use this roadmap to check what’s done, what’s next, and how each part of the system evolves.
