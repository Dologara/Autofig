
# Data Model

This document outlines how NetAutoGen structures, manages, and processes input data across the system.

The project accepts high-level network intent in a structured format (YAML), separates it into base (global) and device-specific inputs, and merges them into clean, unified objects for configuration generation.

---

##  Input Structure

The input to the system is divided into two logical layers:

1. **Global Configuration**
   - Applies to the entire network or all devices by default
   - Example: vendor, routing type, default gateway, VLANs, SSH

2. **Device Configuration**
   - Unique settings per device (e.g., hostname, interface configs)
   - Can override global values as needed

 See: [[02_Input_Spec/Global_Fields]] and [[02_Input_Spec/Device_Specific_Fields]] for detailed input field definitions.

---

##  Merge Strategy

The system uses a 2-phase merge process:

1. **Parse Input**
   - Read and validate the YAML input
   - Load global settings and the list of devices

2. **Merge Configs**
   - For each device:
     - Start with the device's own config
     - Inherit missing values from the global config
   - Output a "merged config object" to be passed into the template engine

This approach ensures minimal duplication and consistent behavior across devices.

---

##  Example Merge Flow

1. `routing: static` is defined globally
2. `Router1` does not override it
3. The final object passed to the router template includes `"routing": "static"`

---

##  Purpose of This Architecture

- Centralizes shared logic
- Reduces duplication in YAML files
- Supports scalable features like:
  - Network-wide defaults
  - Per-device overrides
  - Future multi-vendor branching

---

##  Where It's Used

- Merge logic lives in `core/config_merger.py`
- Used by both CLI and future Web/API flows
- Output fed into Jinja2 templates (see `03_Template_System/`)

---

##  Related Notes
- [[02_Input_Spec/YAML_Examples]] — example inputs
- [[04_Code_Modules/config_merger]] — code that handles merging
- [[03_Template_System/Template_Design_Principles]] — how merged data maps to templates
