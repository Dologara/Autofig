#  Device-Specific Input Fields

This document defines the fields used in **per-device configuration** blocks. These fields follow after global configuration (see `[[Global_Fields]]`) and are applied individually to each router, switch, or L3 switch.

---

##  NOTE

Global fields like `vendor`, `routing`, `enable_password`, `vlans`, and `ssh` are defined in:
- [[Global_Fields]]

This note focuses **only on per-device fields**.

---

##  Router Fields

| Field | Type | Required | Description | Phase |
|-------|------|----------|-------------|--------|
| `hostname` | string | ✅ | Device name shown in prompt | MVP 1 |
| `interfaces[].name` | string | ✅ | Interface name (e.g., `GigabitEthernet0/0`) | MVP 1 |
| `interfaces[].ip` | string | ✅ | IP address | MVP 1 |
| `interfaces[].mask` | string | ✅ | Subnet mask | MVP 1 |
| `interfaces[].description` | string | ❌ | Label/usage context | MVP 1 |
| `interfaces[].shutdown` | bool | ❌ | Shutdown the interface | MVP 1 |
| `interfaces[].speed` | string | ❌ | e.g., `100`, `1000` | Later |
| `interfaces[].duplex` | string | ❌ | e.g., `auto`, `full` | Later |
| `static_routes[]` | object | ❌ | Static route list | MVP 1 |
| `static_routes[].destination` | string | ✅ | Destination subnet | MVP 1 |
| `static_routes[].mask` | string | ✅ | Subnet mask | MVP 1 |
| `static_routes[].next_hop` | string | ✅ | Next hop IP | MVP 1 |
| `nat` | object | ❌ | NAT config (PAT, inside/outside) | Later |
| `ospf` | object | ❌ | Area, networks, process ID | Later |

---

##  L2 Switch Fields

| Field | Type | Required | Description | Phase |
|-------|------|----------|-------------|--------|
| `hostname` | string | ✅ | Device hostname | MVP 1 |
| `interfaces[].name` | string | ✅ | Physical port name | MVP 1 |
| `interfaces[].mode` | enum | ✅ | `access` or `trunk` | MVP 1 |
| `interfaces[].vlan` | int | ⚠️ | Needed for access mode | MVP 1 |
| `interfaces[].allowed_vlans` | list | ⚠️ | Needed for trunk mode | MVP 1 |
| `interfaces[].description` | string | ❌ | Port description | MVP 1 |
| `interfaces[].shutdown` | bool | ❌ | Shut/no shut | MVP 1 |
| `interfaces[].port_security` | object | ❌ | MAC, max addresses | Later |
| `interfaces[].portfast` | bool | ❌ | Enable PortFast | Later |

---

##  L3 Switch Fields

Inherits **all L2 fields**, and supports inter-VLAN routing.

| Field | Type | Required | Description | Phase |
|-------|------|----------|-------------|--------|
| `vlans[]` | reference | ❌ | List of VLAN IDs to SVI | MVP 1 |
| `vlans[].ip` | string | ⚠️ | VLAN interface IP | MVP 1 |
| `vlans[].mask` | string | ⚠️ | Subnet mask | MVP 1 |
| `interfaces[].ip` | string | ⚠️ | IP on physical routed port | MVP 1 |
| `interfaces[].mask` | string | ⚠️ | Mask for routed interface | MVP 1 |
| `interfaces[].routing_enabled` | bool | ❌ | Enables `no switchport` + IP | Later |
| `ip_routing` | bool | ❌ | Enables `ip routing` command | MVP 1 |

---

##  Related Notes

- [[Global_Fields]]
- [[YAML_Examples]]
- [[Execution_Flow]]
- [[Template_System]]
