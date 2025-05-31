#  Field Mapping Reference (Full Schema Overview)

This table documents **every known input field** for NetAutoGen, including type, scope, device coverage, and implementation status.

---

##  Global Fields

| Field | Type | Required | Devices | In YAML | In Template | Phase | Notes |
|-------|------|----------|---------|---------|-------------|--------|-------|
| `vendor` | string | ✅ | All | ✅ | ❌ | MVP 1 | Selects vendor-specific templates |
| `routing` | string | ✅ | Router, L3 | ✅ | ✅ | MVP 1 | `static`, `ospf`, etc. |
| `default_gateway` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Used for static routes |
| `enable_password` | string | ❌ | All | ✅ | ✅ | MVP 1 | Enables privileged EXEC |
| `vlans[]` | object[] | ❌ | L2, L3 | ✅ | ✅ | MVP 1 | Global VLAN definitions |
| `vlans[].id` | int | ✅ | — | ✅ | ✅ | MVP 1 | VLAN ID |
| `vlans[].name` | string | ✅ | — | ✅ | ✅ | MVP 1 | VLAN name |
| `vlans[].ip` | string | ⚠️ | L3 | ✅ | ✅ | MVP 1 | IP for VLAN SVI |
| `vlans[].mask` | string | ⚠️ | L3 | ✅ | ✅ | MVP 1 | Mask for VLAN SVI |
| `ssh.enable` | bool | ✅ | All | ✅ | ✅ | MVP 1 | Enables SSH |
| `ssh.domain_name` | string | ✅ | All | ✅ | ✅ | MVP 1 | Required for keygen |
| `ssh.username` | string | ✅ | All | ✅ | ✅ | MVP 1 | SSH login username |
| `ssh.password` | string | ✅ | All | ✅ | ✅ | MVP 1 | SSH login password |
| `ssh.generate_rsa_bits` | int | ❌ | All | ✅ | ✅ | MVP 1 | Default: 1024 |
| `dns_servers[]` | string[] | ❌ | Router, L3 | ✅ | ✅ | Later | System DNS config |
| `ntp_servers[]` | string[] | ❌ | All | ✅ | ✅ | Later | Time sync |
| `timezone` | string | ❌ | All | ✅ | ✅ | Later | e.g., `UTC`, `IST` |
| `banner` | string | ❌ | All | ✅ | ✅ | Later | MOTD or login banner |
| `syslog_server` | string | ❌ | All | ✅ | ✅ | Later | Remote logging |
| `management_vlan` | int | ❌ | L2, L3 | ✅ | ❌ | Later | Tag interface for mgmt use |

---

##  Router Fields

| Field | Type | Required | Devices | In YAML | In Template | Phase | Notes |
|-------|------|----------|---------|---------|-------------|--------|-------|
| `hostname` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Prompt and SSH hostname |
| `interfaces[].name` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Interface name |
| `interfaces[].ip` | string | ✅ | Router | ✅ | ✅ | MVP 1 | IP address |
| `interfaces[].mask` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Subnet mask |
| `interfaces[].description` | string | ❌ | Router | ✅ | ✅ | MVP 1 | Optional |
| `interfaces[].shutdown` | bool | ❌ | Router | ✅ | ✅ | MVP 1 | Defaults to `no` |
| `interfaces[].speed` | string | ❌ | Router | ✅ | ✅ | Later | e.g., `1000` |
| `interfaces[].duplex` | string | ❌ | Router | ✅ | ✅ | Later | e.g., `full` |
| `static_routes[]` | object[] | ❌ | Router | ✅ | ✅ | MVP 1 | Basic routing |
| `static_routes[].destination` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Target subnet |
| `static_routes[].mask` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Mask for route |
| `static_routes[].next_hop` | string | ✅ | Router | ✅ | ✅ | MVP 1 | Next-hop IP |
| `ospf` | object | ❌ | Router | ✅ | ✅ | Later | Area, process ID |
| `nat` | object | ❌ | Router | ✅ | ✅ | Later | Inside/outside + overload |

---

##  L2 Switch Fields

| Field | Type | Required | Devices | In YAML | In Template | Phase | Notes |
|-------|------|----------|---------|---------|-------------|--------|-------|
| `hostname` | string | ✅ | L2 | ✅ | ✅ | MVP 1 | Prompt/SSH name |
| `interfaces[].name` | string | ✅ | L2 | ✅ | ✅ | MVP 1 | Port label |
| `interfaces[].mode` | enum | ✅ | L2 | ✅ | ✅ | MVP 1 | `access` or `trunk` |
| `interfaces[].vlan` | int | ⚠️ | L2 | ✅ | ✅ | MVP 1 | For access ports |
| `interfaces[].allowed_vlans[]` | int[] | ⚠️ | L2 | ✅ | ✅ | MVP 1 | For trunk ports |
| `interfaces[].description` | string | ❌ | L2 | ✅ | ✅ | MVP 1 | Optional |
| `interfaces[].shutdown` | bool | ❌ | L2 | ✅ | ✅ | MVP 1 | Default: `no` |
| `interfaces[].port_security` | object | ❌ | L2 | ✅ | ✅ | Later | MAC filtering |
| `interfaces[].portfast` | bool | ❌ | L2 | ✅ | ✅ | Later | STP enhancement |

---

##  L3 Switch Fields

| Field | Type | Required | Devices | In YAML | In Template | Phase | Notes |
|-------|------|----------|---------|---------|-------------|--------|-------|
| `hostname` | string | ✅ | L3 | ✅ | ✅ | MVP 1 | Same as other devices |
| `ip_routing` | bool | ❌ | L3 | ✅ | ✅ | MVP 1 | Enables `ip routing` |
| `interfaces[]` | list | ✅ | L3 | ✅ | ✅ | MVP 1 | Routed & switched ports |
| `interfaces[].ip` | string | ⚠️ | L3 | ✅ | ✅ | MVP 1 | Routed port |
| `interfaces[].mask` | string | ⚠️ | L3 | ✅ | ✅ | MVP 1 | For routed port |
| `interfaces[].routing_enabled` | bool | ❌ | L3 | ✅ | ✅ | Later | `no switchport` |
| `vlans[]` | reference[] | ❌ | L3 | ✅ | ✅ | MVP 1 | For SVIs |
| `vlans[].ip` | string | ⚠️ | L3 | ✅ | ✅ | MVP 1 | SVI address |
| `vlans[].mask` | string | ⚠️ | L3 | ✅ | ✅ | MVP 1 | SVI mask |

---

##  Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Required |
| ❌ | Optional |
| ⚠️ | Conditional |
| MVP 1 | Used in current phase |
| Later | Planned for future |

---

## 🔗 Related

- [[Global_Fields]]
- [[Device_Specific_Fields]]
- [[YAML_Examples]]
- [[Template_Design_Principles]]
