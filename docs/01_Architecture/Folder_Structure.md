# Folder Structure

---

## 📂 Folder Breakdown

### `core/`
Main business logic.
- `input_loader.py`: Parses input YAML
- `config_merger.py`: Merges global + device configs
- `generator.py`: Renders config with Jinja2

### `cli/`
Entry-point scripts and CLI handler.
- `main.py`: CLI interface
- `cli_utils.py`: Optional helpers

### `web/` *(planned)*
Future FastAPI or Flask-based interface.
- `app.py`, `routes.py`, etc.

### `inputs/`
YAML input files from users.
- Test inputs or real device data

### `outputs/`
Generated configuration files.
- `.txt` files output per device

### `templates/`
Jinja2 templates per vendor/device.
- `cisco_router.j2`, `cisco_l2_switch.j2`, etc.

### `tests/`
Unit tests for logic modules.
- `test_input_loader.py`, `test_merger.py`, etc.

### `config/` *(optional but recommended)*
Defaults or validation files.
- `default_vlans.yaml`, `schema.yaml`

### `scripts/` *(optional)*
Dev/test utilities.
- `validate_inputs.py`, `batch_generate.py`

### `assets/`
Non-code assets.
- Diagrams, flowcharts, UI mockups

### `docs/` *(optional)*
Exported docs or vault material.

---

## 🔁 Mermaid Diagram (Optional)

```mermaid
graph TD
  A[NetAutoGen/] --> A1[core/]
  A --> A2[cli/]
  A --> A3[web/]
  A --> A4[inputs/]
  A --> A5[outputs/]
  A --> A6[templates/]
  A --> A7[tests/]
  A --> A8[config/]
  A --> A9[scripts/]
  A --> A10[assets/]
  A --> A11[docs/]
  ```
