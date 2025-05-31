# Global vs Device Inputs

##  Decision

The input model is structured into **two distinct categories** within the YAML:
- **Global fields**: Network-wide settings shared across all devices (e.g., SSH credentials, routing method)
- **Device-specific blocks**: Fields that are unique or overridden for each device (e.g., interfaces, hostname, local config)

This separation keeps inputs maintainable, scalable, and easy to work with for both humans and the codebase.

---

##  Input Structure Overview

```yaml
# Global configuration
vendor: cisco
routing: static

ssh:
  enable: true
  username: admin
  password: net123
  domain_name: net.local

vlans:
  - id: 10
    name: Users
  - id: 20
    name: Management

# Per-device definitions
devices:
  - hostname: SW1
    device_type: l2_switch
    interfaces:
      - name: Gi0/1
        mode: access
        vlan: 10

  - hostname: R1
    device_type: router
    interfaces:
      - name: Gi0/0
        ip: 192.168.1.1
        mask: 255.255.255.0
```

##  Why This Split?

### 🔹 Logical Separation of Concerns

- **Global**: What’s shared across all devices
    
- **Device**: What’s local, physical, or specific
    

### 🔹 Prevents Repetition

- No need to write `ssh`, `routing`, or `vendor` in every device block
    

### 🔹 Easier to Maintain

- Change one global value (e.g., NTP server), and it updates across all configs
    

### 🔹 Simpler to Parse and Merge

- One merge pass fills in defaults from global into each device
    
- Templates always receive a complete, consistent config
    

---

##  Merge Behavior

During the `config_merger` step:

|Global Field|Merged Into|Notes|
|---|---|---|
|`vendor`|✅ All devices|Required for template selection|
|`routing`|✅ Routers, L3 switches|Not merged into L2|
|`ssh`|✅ All devices|Can be overridden per device|
|`vlans`|✅ Switches only|Injected into L2/L3 devices|
|`dns_servers`|✅ All devices|Optional, fallback used|
|`ntp_servers`|✅ All devices|Optional, future|
|`banner`|✅ All devices|Rendered into MOTD if present|

 **Device-level fields always override global fields**.

---

##  Edge Cases

|Case|Behavior|
|---|---|
|Missing global block|Device config still parsed if self-contained|
|Empty `devices[]` list|Validation error — nothing to render|
|Device type = unknown|Should be skipped or raise warning|
|Global field present but unused (e.g., `ntp_servers`)|Ignored for now, can be flagged by linter later|

---

##  Design Philosophy

This model is inspired by principles seen in:

- Infrastructure-as-code tools (e.g., Terraform modules + variable inheritance)
    
- Cloud config engines (e.g., AWS Launch Templates)
    
- Ansible inventory structure (group vs host vars)
    

By standardizing input this way, the system:

- Becomes easier to validate
    
- Reduces human error
    
- Remains extensible across vendors and formats
    

---

##  Future Extensions

- Support `globals.yaml` and `devices.yaml` as separate files (split loading)
    
- Add a `profile:` key to reference reusable config blocks
    
- Import defaults from vendor-level presets
    
- GUI form builder can be built around this exact model
    

---

##  Related Notes

- [[Field_Mapping_Reference]]
    
- [[Template_Design_Principles]]
    
- [[Input_Loader]]
    
- [[Config_Merger]]
