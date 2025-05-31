# 05_Output_Format — Output Strategy

## Decision

NetAutoGen outputs **plain-text CLI configuration files** for each device.  
These are generated from Jinja2 templates and stored in the `/outputs/` directory, named per device.

---

## File Naming Convention

Each output file is named using:

Examples:
R1.txt  
SW1.txt  
cisco_l3_core.txt


Simple and readable  
Ideal for labs and manual paste  
Optional: Future support for custom prefixes or extensions (`.cfg`, `.conf`)

---

## Output Directory Structure

```bash
outputs/
├── R1.txt
├── SW1.txt
├── SW2.txt
```

One file per device. All outputs from a single input YAML file are written here by default.

Optional future layout:
outputs/
└── cisco/
    ├── router_R1.txt
    ├── l2_SW1.txt

## Output Style & Formatting

Each file contains:

- A full CLI configuration block
    
- Generated from one Jinja2 template
    
- Flat, vendor-native CLI syntax (e.g., Cisco IOS)
    

Possible sections:

- Hostname at the top
    
- Interface blocks
    
- VLAN definitions
    
- Routing (static or OSPF)
    
- SSH config
    
- Comments or dividers (optional via templates)
    

---

## Example Output Snippet

`hostname R1 interface GigabitEthernet0/0  ip address 192.168.1.1 255.255.255.0  description LAN Connection  no shutdown !  ip route 0.0.0.0 0.0.0.0 192.168.1.254  username admin secret net123 ip domain-name lab.local crypto key generate rsa general-keys modulus 1024`

---

## Testing Plan

- Generated `.txt` should match expected CLI configs
    
- One file per device block
    
- Invalid YAML should not produce output
    
- Configs should render correctly with or without optional fields

- Test both with and without global field overrides
    

---

## Future Enhancements

- Optional `.zip` export of all generated configs
    
- Timestamped output (`R1_2025-06-01.txt`)
    
- `--stdout` CLI flag to print config to console
    
- `--output-dir` override
    
- Merge all into a single master `.txt` (optional)
    

---

## Related Notes

- `[[Template_Design_Principles]]`
    
- `[[Milestone 1 - Core CLI]]`
    
- `[[Global_vs_Device_Inputs]]`
    
- `[[Field_Mapping_Reference]]`
    

