# Optional Features

These are bonus or future enhancements that would improve usability, portability, and professional deployment — but are **not required for MVP** or core milestones.

---

## Simulation & Lab Integration

- [ ] **GNS3 Output Format**
  - Generate configs tailored for import into GNS3 topologies
  - Include sample `.net` or project templates

- [ ] **EVE-NG Ready Output**
  - Script to generate device configs and node metadata

---

## Monitoring & Insights

- [ ] **Analytics Dashboard**
  - Track how many configs were generated
  - Log generation time per device
  - CLI stats (optional metrics flag)

- [ ] **Audit Log**
  - Log who generated configs, when, and from what IP (API only)

---

## Import/Export Extensions

- [ ] **Import Config Snippets**
  - Ability to import partial device configs and re-use fields

- [ ] **Export to NetBox**
  - Push device metadata to NetBox via API
  - Helps with inventory and automation ecosystems

- [ ] **Save Session State**
  - Save/load “project” files with inputs + outputs

---

## Dev Tools

- [ ] **Config Linter**
  - Validate rendered CLI output for vendor syntax

- [ ] **Dry-Run Mode**
  - CLI flag to print to screen but not write to file

- [ ] **ZIP Packager**
  - Bundle all outputs + YAML + timestamp into one archive

---

## UI Features (Post-MVP)

- [ ] **YAML Wizard**
  - Web-based step-by-step form to generate input files

- [ ] **Live Config Preview**
  - As user fills YAML, show config live in browser

---

## Team / Collab Features

- [ ] **Multi-user Mode**
  - Allow shared YAML sessions
  - Track changes or versioning

- [ ] **Git Sync**
  - Push/pull YAML and output files from GitHub

---

## Prioritization Notes

These features can be picked up based on:
- Team size and bandwidth
- Community or user feedback
- Specific partner or internal needs

They’re useful, but **should not block** the main CLI → API → Web UI pipeline.

---

## Related Notes

- `[[API_Server]]`
- `[[Web_UI]]`
- `[[Output_Format]]`
- `[[Field_Mapping_Reference]]`
