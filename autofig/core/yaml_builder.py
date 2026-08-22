"""Build YAML topology from form answers.

Converts user inputs into a topology dict matching Autofig's schema
(see docs/02_Input_Spec/Global_Fields.md and Device_Specific_Fields.md).
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

# Matches the PACKAGE_ROOT convention used by loader.py / renderer.py /
# generator.py: this file lives at autofig/core/yaml_builder.py, so
# parent.parent is the autofig/ package root.
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
TOPOLOGY_DIR = PACKAGE_ROOT / "data" / "topologies"
TOPOLOGY_DIR.mkdir(parents=True, exist_ok=True)


class YAMLBuilder:
    """Build a topology dict from form answers, then save/export it as YAML."""

    def __init__(self):
        self.topology: Dict[str, Any] = {}
        self.devices: List[Dict[str, Any]] = []

    def set_global_fields(self, answers: Dict[str, Any]) -> None:
        """Set global (topology-level) fields from form answers.

        Args:
            answers: dict with keys such as name, vendor, routing,
                default_gateway, enable_password, domain_name,
                ssh_enabled/ssh_username/ssh_password, vlans,
                dns_servers, ntp_servers, syslog_servers (all but
                name/vendor/routing/default_gateway are optional).
        """
        self.topology["name"] = answers.get("name", "generated_topology")
        self.topology["vendor"] = answers.get("vendor", "Cisco")
        self.topology["routing"] = answers.get("routing", "static")
        self.topology["default_gateway"] = answers.get("default_gateway")

        if answers.get("enable_password"):
            self.topology["enable_password"] = answers["enable_password"]

        if answers.get("domain_name"):
            self.topology["domain_name"] = answers["domain_name"]

        vlans = answers.get("vlans", [])
        if vlans:
            self.topology["vlans"] = vlans

        if answers.get("ssh_enabled"):
            self.topology["ssh"] = {
                "enable": True,
                "domain_name": answers.get("domain_name", "example.com"),
                "username": answers.get("ssh_username", "admin"),
                "password": answers.get("ssh_password", "cisco123"),
                "generate_rsa_bits": 2048,
            }

        if answers.get("dns_servers"):
            self.topology["dns_servers"] = answers["dns_servers"]

        if answers.get("ntp_servers"):
            self.topology["ntp_servers"] = answers["ntp_servers"]

        if answers.get("syslog_servers"):
            self.topology["syslog_servers"] = answers["syslog_servers"]

    def add_router(self, answers: Dict[str, Any]) -> None:
        """Add a router device.

        Args:
            answers: dict with hostname, interfaces, static_routes (optional).
        """
        device = {
            "name": answers.get("hostname").lower().replace(" ", "_"),
            "type": "router",
            "vendor": self.topology.get("vendor", "Cisco"),
            "hostname": answers.get("hostname"),
        }

        if answers.get("interfaces"):
            device["interfaces"] = answers["interfaces"]

        if answers.get("static_routes"):
            device["static_routes"] = answers["static_routes"]

        self.devices.append(device)

    def add_switch(self, answers: Dict[str, Any], is_l3: bool = False) -> None:
        """Add a switch device (L2 or L3/multilayer).

        Args:
            answers: dict with hostname, interfaces, ip_routing (L3 only),
                vlans (L3 only, SVI configs).
            is_l3: True for multilayer switch, False for plain L2 switch.
        """
        device_type = "multilayer_switch" if is_l3 else "switch"

        device = {
            "name": answers.get("hostname").lower().replace(" ", "_"),
            "type": device_type,
            "vendor": self.topology.get("vendor", "Cisco"),
            "hostname": answers.get("hostname"),
        }

        if answers.get("interfaces"):
            device["interfaces"] = answers["interfaces"]

        if is_l3:
            if answers.get("ip_routing"):
                device["ip_routing"] = True
            if answers.get("vlans"):
                device["vlans"] = answers["vlans"]

        self.devices.append(device)

    def build(self) -> Dict[str, Any]:
        """Finalize the topology dict with all devices attached."""
        self.topology["devices"] = self.devices
        return self.topology

    def save_yaml(self, filename: str = None) -> Path:
        """Save the topology to a YAML file under data/topologies/."""
        if not filename:
            filename = self.topology.get("name", "topology")

        output_path = TOPOLOGY_DIR / f"{filename}.yaml"

        with open(output_path, "w") as f:
            yaml.safe_dump(self.topology, f, default_flow_style=False, sort_keys=False)

        return output_path

    def to_yaml_string(self) -> str:
        """Get the topology as a YAML string without saving to disk."""
        return yaml.safe_dump(self.topology, default_flow_style=False, sort_keys=False)

    def get_topology(self) -> Dict[str, Any]:
        """Get the built topology dict."""
        return self.topology


def build_from_preset(preset_name: str, topology_name: str) -> Dict[str, Any]:
    """Build a topology from a preset template ('quick', 'medium', 'enterprise')."""
    builder = YAMLBuilder()

    if preset_name == "quick":
        builder.set_global_fields({
            "name": topology_name,
            "vendor": "Cisco",
            "routing": "static",
            "default_gateway": "10.0.0.1",
            "domain_name": "lab.local",
            "ssh_enabled": True,
            "ssh_username": "admin",
            "ssh_password": "cisco123",
            "vlans": [
                {"id": 1, "name": "default"},
                {"id": 10, "name": "management"},
                {"id": 20, "name": "users"},
            ],
            "dns_servers": ["8.8.8.8", "8.8.4.4"],
            "ntp_servers": ["pool.ntp.org"],
        })

        builder.add_router({
            "hostname": "Router-1",
            "interfaces": [
                {"name": "GigabitEthernet0/0", "ip": "10.0.1.1", "mask": "255.255.255.0"},
                {"name": "GigabitEthernet0/1", "ip": "10.0.2.1", "mask": "255.255.255.0"},
            ],
        })

        builder.add_router({
            "hostname": "Router-2",
            "interfaces": [
                {"name": "GigabitEthernet0/0", "ip": "10.0.3.1", "mask": "255.255.255.0"},
                {"name": "GigabitEthernet0/1", "ip": "10.0.4.1", "mask": "255.255.255.0"},
            ],
        })

        builder.add_switch({
            "hostname": "Switch-1",
            "interfaces": [
                {"name": "GigabitEthernet0/1", "mode": "access", "vlan": 20},
                {"name": "GigabitEthernet0/2", "mode": "trunk", "allowed_vlans": [1, 10, 20]},
            ],
        })

        builder.add_switch({
            "hostname": "Switch-2",
            "interfaces": [
                {"name": "GigabitEthernet0/1", "mode": "access", "vlan": 20},
                {"name": "GigabitEthernet0/2", "mode": "trunk", "allowed_vlans": [1, 10, 20]},
            ],
        })

    elif preset_name == "medium":
        builder.set_global_fields({
            "name": topology_name,
            "vendor": "Cisco",
            "routing": "ospf",
            "default_gateway": "10.0.0.1",
            "domain_name": "corp.local",
            "ssh_enabled": True,
            "ssh_username": "admin",
            "ssh_password": "cisco123",
            "vlans": [
                {"id": 1, "name": "native"},
                {"id": 10, "name": "management"},
                {"id": 20, "name": "users"},
                {"id": 30, "name": "servers"},
            ],
            "dns_servers": ["8.8.8.8"],
            "ntp_servers": ["pool.ntp.org"],
        })

        for i in range(1, 4):
            builder.add_router({
                "hostname": f"Router-{i}",
                "interfaces": [
                    {"name": "GigabitEthernet0/0", "ip": f"10.0.{i}.1", "mask": "255.255.255.0"},
                    {"name": "GigabitEthernet0/1", "ip": f"10.1.{i}.1", "mask": "255.255.255.0"},
                ],
            })

        for i in range(1, 5):
            builder.add_switch({
                "hostname": f"Switch-{i}",
                "interfaces": [
                    {"name": "GigabitEthernet0/1", "mode": "access", "vlan": 20},
                    {"name": "GigabitEthernet0/2", "mode": "trunk", "allowed_vlans": [1, 10, 20, 30]},
                ],
            })

        builder.add_switch({
            "hostname": "MLSwitch-1",
            "ip_routing": True,
            "interfaces": [
                {"name": "GigabitEthernet0/1", "mode": "trunk", "allowed_vlans": [1, 10, 20, 30]},
            ],
            "vlans": [
                {"id": 10, "ip": "10.10.0.1", "mask": "255.255.255.0"},
                {"id": 20, "ip": "10.20.0.1", "mask": "255.255.255.0"},
                {"id": 30, "ip": "10.30.0.1", "mask": "255.255.255.0"},
            ],
        }, is_l3=True)

    elif preset_name == "enterprise":
        builder.set_global_fields({
            "name": topology_name,
            "vendor": "Cisco",
            "routing": "ospf",
            "default_gateway": "10.0.0.1",
            "domain_name": "enterprise.local",
            "ssh_enabled": True,
            "ssh_username": "admin",
            "ssh_password": "enterprise123",
            "vlans": [
                {"id": 1, "name": "native"},
                {"id": 10, "name": "management"},
                {"id": 20, "name": "users"},
                {"id": 30, "name": "servers"},
                {"id": 40, "name": "guests"},
                {"id": 50, "name": "iot"},
            ],
            "dns_servers": ["8.8.8.8", "1.1.1.1"],
            "ntp_servers": ["pool.ntp.org"],
        })

        for i in range(1, 6):
            builder.add_router({
                "hostname": f"Router-{i}",
                "interfaces": [
                    {"name": "GigabitEthernet0/0", "ip": f"10.0.{i}.1", "mask": "255.255.255.0"},
                    {"name": "GigabitEthernet0/1", "ip": f"10.1.{i}.1", "mask": "255.255.255.0"},
                ],
            })

        for i in range(1, 11):
            builder.add_switch({
                "hostname": f"Switch-{i}",
                "interfaces": [
                    {"name": "GigabitEthernet0/1", "mode": "access", "vlan": 20},
                    {"name": "GigabitEthernet0/2", "mode": "trunk", "allowed_vlans": [1, 10, 20, 30]},
                ],
            })

        for j in range(1, 3):
            builder.add_switch({
                "hostname": f"MLSwitch-{j}",
                "ip_routing": True,
                "interfaces": [
                    {"name": "GigabitEthernet0/1", "mode": "trunk", "allowed_vlans": [1, 10, 20, 30, 40, 50]},
                ],
                "vlans": [
                    {"id": 10, "ip": f"10.10.{j}.1", "mask": "255.255.255.0"},
                    {"id": 20, "ip": f"10.20.{j}.1", "mask": "255.255.255.0"},
                    {"id": 30, "ip": f"10.30.{j}.1", "mask": "255.255.255.0"},
                    {"id": 40, "ip": f"10.40.{j}.1", "mask": "255.255.255.0"},
                    {"id": 50, "ip": f"10.50.{j}.1", "mask": "255.255.255.0"},
                ],
            }, is_l3=True)

    return builder.build()
