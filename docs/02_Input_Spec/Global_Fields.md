# Global Fields
#  Global Input Fields

These fields are provided before any per-device configuration begins. They define network-wide settings and apply to all devices unless overridden.

---

##  Global Field List

| Field | Type | Required | Description | Phase |
|-------|------|----------|-------------|--------|
| `vendor` | string | ✅ | Vendor for config generation (e.g., `cisco`) | MVP 1 |
| `routing` | string | ✅ | Routing type: `static`, `ospf`, etc. | MVP 1 |
| `default_gateway` | string | ✅ | Used for static routing or fallback route | MVP 1 |
| `enable_password` | string | ❌ | Sets privileged EXEC mode password | MVP 1 |
| `vlans` | list | ❌ | Globally available VLANs | MVP 1 |
| `ssh` | object | ❌ | Default SSH setup (inherited by devices) | MVP 1 |
| `dns_servers` | list of strings | ❌ | Sets system DNS servers | Later |
| `ntp_servers` | list of strings | ❌ | Sets NTP sources for time sync | Later |
| `timezone` | string | ❌ | Configures device timezone (e.g., `UTC`) | Later |
| `banner` | string | ❌ | Message of the day (login banner) | Later |
| `domain_name` | string | ❌ | Used for SSH keygen and hostname FQDN | MVP 1 |
| `syslog_server` | string | ❌ | Remote syslog logging destination | Later |
| `snmp` | object | ❌ | SNMP config block for monitoring | Later |
| `management_vlan` | int | ❌ | Global VLAN for management-only use | Later |

---

## VLAN Object Fields

VLANs are defined globally using the `vlans` list. Each VLAN can be referenced in device-specific interfaces and may optionally include L3 settings.

| Field | Type | Required | Description | Used In |
|-------|------|----------|-------------|---------|
| `id` | int | ✅ | VLAN ID (e.g., 10) | All switches |
| `name` | string | ✅ | VLAN name (e.g., `Users`) | All switches |
| `ip` | string | ❌ | IP address for VLAN interface (SVI) | L3 switches only |

---

###  Notes

- VLANs are **declared globally**, then **referenced** on each device via:
  - Interface config (`access vlan`)
  - Trunk config (`allowed_vlans`)
  - SVI config (`interface vlan X`)
- For **L2 switches**, `ip` and `mask` are ignored.
- For **L3 switches**, `ip` + `mask` define the VLAN interface config (SVI).
- VLANs can be reused across multiple devices — they’re assumed consistent.



---

## SSH Object Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `enable` | bool | ✅ | Whether to enable SSH |
| `domain_name` | string | ✅ | Needed for RSA key generation |
| `username` | string | ✅ | SSH username |
| `password` | string | ✅ | SSH password |
| `generate_rsa_bits` | int | ❌ | Defaults to 1024 |

---

## 🔗 Related Notes

- [[Device_Specific_Fields]]
- [[YAML_Examples]]
- [[Data_Model]]
