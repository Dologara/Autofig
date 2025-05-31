# 🧭 NetAutoGen Project Overview

This folder contains the major milestones for evolving NetAutoGen from a CLI-based tool into a full server-capable, API-integrated, and UI-driven system.

Each milestone represents a phase of architectural and functional growth, designed to keep the tool scalable, testable, and easy to adopt.

---

## 🎯 Project Vision

> To build a modular, vendor-agnostic, input-driven system that generates valid network configurations, beginning with CLI tools and growing into a complete server-based automation platform.

---

## 🧱 Core Foundations

- Built on **YAML input + Jinja2 templates**
- CLI-first approach for speed and simplicity
- Per-device rendering model
- Structured to allow future expansion (web UI, API, integrations)

---

## 🗂️ Milestone Index

| ID  | Milestone                            | Goal                                   |
| --- | ------------------------------------ | -------------------------------------- |
| 1️⃣ | `Milestone 1 - Core CLI`             | CLI input → config generation engine   |
| 2️⃣ | `Milestone 2 - API Server`           | Wrap logic into FastAPI                |
| 3️⃣ | `Milestone 3 - Linux Deployment`     | Package for local install on Linux     |
| 4️⃣ | `Milestone 4 - Docs & Collaboration` | Internal & contributor-friendly docs   |
| 5️⃣ | `Milestone 5 - Security`             | Basic token-based auth, SSH awareness  |
| 6️⃣ | `Milestone 6 - Template Expansion`   | Add new vendors, advanced features     |
| 7️⃣ | `Milestone 7 - Web UI`               | Build simple, live-config browser UI   |
| 🚧  | `Optional Features`                  | GNS3, NetBox, import/export, analytics |

---

## 🔗 See Also

- [[Milestone Roadmap]] — full status and timeline view
- [[Folder_Structure]] — key architectural decisions
