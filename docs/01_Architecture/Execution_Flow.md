
# Execution Flow

This note describes the lifecycle of the config generation process — from parsing the input to rendering and outputting final configuration files.

---

##  Overview

1. **User provides input file**
   - A YAML file containing global settings and device configurations

2. **System loads input**
   - Parsed by `input_loader.py`
   - Split into `global_config` and `devices[]`

3. **Device loop begins**
   - For each device in the list:
     - Run merge logic via `config_merger.py`
     - Inherit global fields where applicable

4. **Template selection**
   - Based on `device_type` (router, l2_switch, etc.)
   - Select matching Jinja2 template

5. **Template rendering**
   - Render the config using `generator.py`
   - Output as plain text file to `/outputs/`

---
##  Flow Diagram (Conceptual)


```mermaid
flowchart TD
  A[Step 1: Enter Global Network Info ] --> B[Step 2: Add Device-Specific Info ]
  B --> C[Merge Device with Global Settings ]
  C --> D[Determine Device Type ]

  D --> R[Router Template ]
  D --> L2[L2 Switch Template ]
  D --> L3[L3 Switch Template ]

  R --> FR[Render Router Config ]
  L2 --> FL2[Render L2 Config ]
  L3 --> FL3[Render L3 Config ]

  FR --> O1[Write Router Output ]
  FL2 --> O2[Write L2 Output ]
  FL3 --> O3[Write L3 Output ]

```

---

###  Key Points Reflected:
- Shows user **filling out input in 2 stages**
- Emphasizes **merging** as a separate, essential step
- Cleanly branches based on device type
- Unified output generation per device

---

