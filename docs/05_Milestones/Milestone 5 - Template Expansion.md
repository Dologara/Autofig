# Milestone 5 – Template Expansion

## Goals

Expand NetAutoGen’s templating support to include:
- Additional Cisco device types (e.g., Layer 3 switches)
- New vendors (Juniper, Arista, MikroTik)
- More features within templates (e.g., routing, HSRP, STP, OSPF)

This milestone scales the system from a prototype to a production-ready tool for more complex topologies.

---

## Output

- New `.j2` templates in `/templates/`
- Updated input YAML examples (`/inputs/`)
- Enhanced field handling in Jinja logic
- Optional: shared partials (`_interfaces.j2`, `_ssh_block.j2`)
- Clear documentation of supported input fields per device

---

## Tasks

- [x] Support Cisco L2 switch (access, trunk, VLANs)
- [x] Support Cisco L3 switch (SVIs, inter-VLAN routing)
- [x] Expand router features (static routes, SSH, hostnames)
- [ ] Add support for 1+ non-Cisco vendor (e.g., Juniper)
- [ ] Add shared logic partials (`common/`) and test includes
- [ ] Document input format requirements for each template
- [ ] Add test input files and outputs for each supported type

---

## Template Naming Convention

templates/  
├── cisco_router.j2  
├── cisco_l2_switch.j2  
├── cisco_l3_switch.j2  
├── juniper_router.j2  
├── arista_l2_switch.j2


Each template matches:  
`{vendor}_{device_type}.j2`

---

## Example Features to Add

| Feature | Template Target |
|--------|-----------------|
| VLAN setup | Cisco switches |
| Static + OSPF routing | Routers (Cisco + Juniper) |
| STP config | L2/L3 switches |
| HSRP config | L3 switches |
| SSH access block | All devices |
| Loopback interface | Routers |
| Interface descriptions | All |

---

## Testing Plan

- Valid YAML → Valid CLI output
- Missing fields → Templates use `| default(...)`
- Unsupported combo (e.g., OSPF on L2) → warn or skip
- YAML test + generated `.txt` in `/outputs/`

---

## Optional Enhancements

- `templates/common/` folder for shared logic (Jinja includes)
- Field validation per template using schemas
- Output linting (e.g., interface blocks correctly formatted)

---

## Related Notes

- `[[Template_Design_Principles]]`
- `[[Field_Mapping_Reference]]`
- `[[YAML_Examples]]`
- `[[Jinja2_Syntax]]`

---

## Status

In Progress → Complete when:
- 3+ device types are fully supported
- 1+ non-Cisco template exists
- Input logic can handle required fields for each template
