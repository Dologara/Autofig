
#  YAML Input Examples

This document provides sample YAML inputs for different device types.  
Each file consists of:
- Global config block (applies to all devices)
- Device list (each with specific settings)

---

##  Global Block Example

```yaml
vendor: cisco
routing: static
default_gateway: 192.168.1.254
enable_password: cisco123

vlans:
  - id: 10
    name: Users
  - id: 20
    name: Management
    ip: 192.168.20.1
    mask: 255.255.255.0

ssh:
  enable: true
  domain_name: netautogen.local
  username: admin
  password: admin123
  generate_rsa_bits: 2048
  ```

## Router Example


``` yaml 
devices:
  - hostname: Router1
    device_type: router
    interfaces:
      - name: GigabitEthernet0/0
        ip: 192.168.1.1
        mask: 255.255.255.0
        description: LAN Interface
      - name: GigabitEthernet0/1
        ip: 10.0.0.1
        mask: 255.255.255.252
        description: Uplink to ISP
    static_routes:
      - destination: 0.0.0.0
        mask: 0.0.0.0
        next_hop: 10.0.0.2

```
## L3 Switch Example


``` yaml 
devices:
  - hostname: Switch2
    device_type: l3_switch
    ip_routing: true
    interfaces:
      - name: GigabitEthernet1/0
        mode: access
        vlan: 10
        description: Floor 1 Host
      - name: GigabitEthernet1/1
        mode: trunk
        allowed_vlans: [10, 20]
        description: Trunk to L2 Switch
    vlans:
      - id: 20
        ip: 192.168.20.1
        mask: 255.255.255.0
```

###  Notes

- Only **one global block** is needed per input file.
    
- VLANs defined in the global `vlans:` list can be **referenced by any switch** (L2 or L3).
    
- Device-specific `vlans:` (used in L3 switches) can **override or extend** the global VLANs for **SVI configuration**.
    
- SSH settings and routing type will apply from the **global config** unless explicitly overridden in the device block.
    

---

###  Related Notes

- [[Global_Fields]]
    
- [[Device_Specific_Fields]]
    
- [[Template_System]]
