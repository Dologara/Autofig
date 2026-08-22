"""Enhanced interactive topology builder with presets.

Guides users through topology creation with:
- Presets (Quick/Medium/Enterprise) or a fully custom build
- Input validation with actionable error messages (IPs, hostnames,
  VLANs, subnet masks)
- Inline help text on each prompt
- A skippable "advanced options" section (DNS/NTP/syslog) so a first-time
  user isn't forced through every field
- An edit-after-preview loop: after seeing the generated YAML, the user
  can jump back and redo any section instead of starting over

Uses schema from:
- docs/02_Input_Spec/Global_Fields.md
- docs/02_Input_Spec/Device_Specific_Fields.md
"""

from typing import Dict, List, Any

from .yaml_builder import YAMLBuilder, build_from_preset
from .validators import (
    ValidationError,
    validate_ip,
    validate_subnet_mask,
    validate_hostname,
    validate_vlan_id,
    validate_vlan_list,
    validate_interface_name,
)

DEFAULT_DNS_SERVERS = ["8.8.8.8", "8.8.4.4"]
DEFAULT_NTP_SERVERS = ["pool.ntp.org"]
DEFAULT_SYSLOG_SERVERS: List[str] = []


class PresetForm:
    """Interactive form with preset templates and a custom-build path."""

    def __init__(self):
        self.PRESETS = ["quick", "medium", "enterprise", "custom"]

    # ------------------------------------------------------------------
    # Low-level prompt helpers (validation, help text, retry loops)
    # ------------------------------------------------------------------

    def ask_validated(self, prompt: str, validator, default=None, help_text: str = None):
        """Ask for input, validate it, and keep re-prompting on failure.

        Args:
            prompt: The question text (without the trailing colon/brackets).
            validator: A function that takes the raw string and either
                returns the parsed/validated value or raises ValidationError.
            default: Value to use if the user presses Enter with no input.
                Not passed through the validator - assumed already valid.
            help_text: Optional one-line explanation shown above the prompt.

        Returns:
            The validated value.
        """
        if help_text:
            print(f"  \u2139 {help_text}")

        if default is None:
            suffix = ""
        elif isinstance(default, list):
            suffix = f" [{','.join(str(d) for d in default)}]"
        else:
            suffix = f" [{default}]"

        while True:
            raw = input(f"{prompt}{suffix}: ").strip()
            if not raw and default is not None:
                return default
            try:
                return validator(raw)
            except ValidationError as e:
                print(f"  \u2717 {e}")
                print("  Please try again.\n")

    def ask_yes_no(self, prompt: str, default: bool = True, help_text: str = None) -> bool:
        """Ask a yes/no question with a default."""
        if help_text:
            print(f"  \u2139 {help_text}")
        suffix = "[Y/n]" if default else "[y/N]"
        while True:
            raw = input(f"{prompt} {suffix}: ").strip().lower()
            if not raw:
                return default
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            print("  \u2717 Please answer 'y' or 'n'.\n")

    def ask_list(self, prompt: str, default: List[str], help_text: str = None) -> List[str]:
        """Ask for a comma-separated list, falling back to a default."""
        if help_text:
            print(f"  \u2139 {help_text}")
        value = input(f"{prompt} [{', '.join(default) if default else 'none'}]: ").strip()
        if not value:
            return default
        return [v.strip() for v in value.split(",") if v.strip()]

    def ask_int(self, prompt: str, default: int, help_text: str = None) -> int:
        """Ask for an integer with a default and a clear error on bad input."""
        if help_text:
            print(f"  \u2139 {help_text}")
        while True:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                return default
            try:
                return int(value)
            except ValueError:
                print(f"  \u2717 '{value}' isn't a whole number. Try again.\n")

    # ------------------------------------------------------------------
    # Banner / preset selection
    # ------------------------------------------------------------------

    def show_banner(self):
        """Show welcome banner."""
        print("\n" + "=" * 60)
        print("        AUTOFIG NETWORK BUILDER")
        print("=" * 60)
        print("Build network topologies interactively")
        print("Generates Cisco IOS configs in seconds\n")

    def ask_preset(self) -> str:
        """Ask user to choose a preset.

        Returns:
            Preset name: 'quick', 'medium', 'enterprise', or 'custom'
        """
        print("Choose a preset:\n")
        descriptions = {
            "quick": "2 routers, 2 switches - fastest way to get a working lab",
            "medium": "3 routers, 4 switches, 1 L3 switch, OSPF routing",
            "enterprise": "5 routers, 10 switches, 2 L3 switches, OSPF, 6 VLANs",
            "custom": "Build every device yourself, step by step",
        }
        for i, preset in enumerate(self.PRESETS, 1):
            print(f"  {i}. {preset.capitalize()} - {descriptions[preset]}")

        while True:
            choice = input("\nYour choice (1-4): ").strip()
            if choice in ["1", "2", "3", "4"]:
                return self.PRESETS[int(choice) - 1]
            print("  \u2717 Invalid choice. Enter a number from 1-4.")

    def ask_topology_name(self) -> str:
        """Ask for topology name with default."""
        print("  \u2139 Used as the filename (topology.yaml) and shown in generated configs.")
        name = input("\nTopology name [my_network]: ").strip() or "my_network"
        return name.lower().replace(" ", "_")

    # ------------------------------------------------------------------
    # Global settings (with skippable advanced section)
    # ------------------------------------------------------------------

    def ask_global_settings(self) -> Dict[str, Any]:
        """Ask for global settings, with DNS/NTP/syslog as skippable advanced options."""
        print("\n" + "-" * 60)
        print("GLOBAL SETTINGS")
        print("-" * 60)

        settings = {
            "vendor": input("Vendor [Cisco]: ").strip() or "Cisco",
            "routing": self.ask_routing_type(),
            "default_gateway": self.ask_validated(
                "Default gateway IP",
                validate_ip,
                default="10.0.0.1",
                help_text="The router/switch IP that acts as the network's default route.",
            ),
            "domain_name": input("Domain name [lab.local]: ").strip() or "lab.local",
            "enable_password": input(
                "Enable password (optional, press Enter to skip): "
            ).strip(),
            "ssh_enabled": self.ask_yes_no(
                "Enable SSH?", default=True,
                help_text="Adds SSH access config (username/password, RSA key generation) to every device.",
            ),
            "vlans": self.ask_vlans(),
        }

        if settings["ssh_enabled"]:
            settings["ssh_username"] = input("SSH username [admin]: ").strip() or "admin"
            settings["ssh_password"] = input("SSH password: ").strip() or "cisco123"

        settings.update(self.ask_advanced_options())

        return settings

    def ask_advanced_options(self) -> Dict[str, Any]:
        """Ask whether to configure DNS/NTP/syslog, or skip straight to smart defaults."""
        configure_advanced = self.ask_yes_no(
            "\nConfigure advanced options (DNS, NTP, syslog servers)?",
            default=False,
            help_text="Most labs work fine with the defaults below - only say yes if you need custom servers.",
        )

        if not configure_advanced:
            print(
                f"  Using defaults - DNS: {', '.join(DEFAULT_DNS_SERVERS)}, "
                f"NTP: {', '.join(DEFAULT_NTP_SERVERS)}, syslog: none"
            )
            return {
                "dns_servers": DEFAULT_DNS_SERVERS,
                "ntp_servers": DEFAULT_NTP_SERVERS,
                "syslog_servers": DEFAULT_SYSLOG_SERVERS,
            }

        dns_servers = self.ask_list(
            "DNS servers (comma-separated)", DEFAULT_DNS_SERVERS,
            help_text="Servers devices will use to resolve hostnames.",
        )
        ntp_servers = self.ask_list(
            "NTP servers (comma-separated)", DEFAULT_NTP_SERVERS,
            help_text="Servers devices will sync their clock against.",
        )
        syslog_servers = self.ask_list(
            "Syslog servers (comma-separated, blank for none)", DEFAULT_SYSLOG_SERVERS,
            help_text="Servers devices will forward log messages to. Leave blank if you don't run one.",
        )

        return {
            "dns_servers": dns_servers,
            "ntp_servers": ntp_servers,
            "syslog_servers": syslog_servers,
        }

    def ask_routing_type(self) -> str:
        """Ask for routing protocol."""
        print("\nRouting type:")
        print("  1. static  - simplest, manually defined routes")
        print("  2. ospf    - dynamic, routers learn routes from each other")
        print("  3. bgp     - for multi-domain/ISP-style topologies")

        choice = input("Choose (1-3) [1]: ").strip() or "1"
        mapping = {"1": "static", "2": "ospf", "3": "bgp"}
        return mapping.get(choice, "static")

    def ask_vlans(self) -> List[Dict[str, Any]]:
        """Ask for VLANs."""
        print("\nVLANs (enter IDs, comma-separated, e.g. '1,10,20'):")
        vlan_ids = self.ask_validated(
            "VLANs", validate_vlan_list, default=[1, 10, 20, 30],
            help_text="VLAN 1 is the default VLAN; avoid 1002-1005 (reserved by Cisco).",
        )

        vlan_names = {
            1: "default", 10: "management", 20: "users",
            30: "servers", 40: "guests", 50: "iot",
        }

        return [
            {"id": vlan_id, "name": vlan_names.get(vlan_id, f"vlan{vlan_id}")}
            for vlan_id in vlan_ids
        ]

    # ------------------------------------------------------------------
    # Device counts / details
    # ------------------------------------------------------------------

    def ask_device_counts(self) -> Dict[str, int]:
        """Ask how many devices of each type."""
        print("\n" + "-" * 60)
        print("DEVICE COUNTS")
        print("-" * 60)

        routers = self.ask_int("How many routers?", 1)
        switches = self.ask_int("How many L2 switches?", 2)
        ml_switches = self.ask_int(
            "How many L3 switches?", 0,
            help_text="L3 (multilayer) switches route between VLANs - most small labs don't need one.",
        )

        return {"routers": routers, "switches": switches, "ml_switches": ml_switches}

    def ask_device_details(self, device_type: str, device_num: int) -> Dict[str, Any]:
        """Ask for details of a specific device."""
        device_name = self.get_device_name(device_type, device_num)

        print(f"\n{device_type.upper()} {device_num}")
        print("-" * 40)

        hostname = self.ask_validated(
            "Hostname", validate_hostname, default=device_name,
            help_text="Cisco IOS hostnames: letters/digits/hyphens only, 15 chars max.",
        )

        if device_type == "router":
            return self.ask_router_details(hostname)
        else:
            is_l3 = device_type == "l3_switch"
            return self.ask_switch_details(hostname, is_l3)

    def get_device_name(self, device_type: str, num: int) -> str:
        """Generate default device name."""
        prefix_map = {"router": "Router", "switch": "Switch", "l3_switch": "MLSwitch"}
        return f"{prefix_map.get(device_type, 'Device')}-{num}"

    def ask_router_details(self, hostname: str) -> Dict[str, Any]:
        """Ask for router-specific details."""
        interfaces = self.ask_interfaces("router")

        router = {"hostname": hostname, "interfaces": interfaces}

        if self.ask_yes_no("Configure static routes?", default=False):
            router["static_routes"] = self.ask_static_routes()

        return router

    def ask_switch_details(self, hostname: str, is_l3: bool = False) -> Dict[str, Any]:
        """Ask for switch-specific details."""
        interfaces = self.ask_interfaces("switch")

        switch = {"hostname": hostname, "interfaces": interfaces}

        if is_l3:
            if self.ask_yes_no("Enable IP routing?", default=True):
                switch["ip_routing"] = True

            if self.ask_yes_no(
                "Configure VLAN interfaces (SVIs)?", default=True,
                help_text="SVIs give this switch an IP on each VLAN, letting it route between them.",
            ):
                switch["vlans"] = self.ask_svi_config()

        return switch

    def ask_interfaces(self, device_type: str) -> List[Dict[str, Any]]:
        """Ask for interfaces."""
        interfaces = []

        num_interfaces = self.ask_int("How many interfaces?", 2)

        for i in range(1, num_interfaces + 1):
            if device_type == "router":
                interface = self.ask_router_interface(i)
            else:
                interface = self.ask_switch_interface(i)

            interfaces.append(interface)

        return interfaces

    def ask_router_interface(self, num: int) -> Dict[str, Any]:
        """Ask for router interface config."""
        interface = {
            "name": self.ask_validated(
                f"Interface {num} name", validate_interface_name,
                default=f"GigabitEthernet0/{num - 1}",
            ),
            "ip": self.ask_validated(
                "IP address", validate_ip, default=f"10.0.{num}.1",
            ),
            "mask": self.ask_validated(
                "Subnet mask", validate_subnet_mask, default="255.255.255.0",
                help_text="Dotted-decimal format, e.g. 255.255.255.0 for a /24.",
            ),
        }

        desc = input("Description (optional): ").strip()
        if desc:
            interface["description"] = desc

        return interface

    def ask_switch_interface(self, num: int) -> Dict[str, Any]:
        """Ask for switch interface config."""
        interface = {
            "name": self.ask_validated(
                f"Interface {num} name", validate_interface_name,
                default=f"GigabitEthernet0/{num}",
            ),
        }

        mode = input("Mode (access/trunk) [access]: ").strip().lower() or "access"
        interface["mode"] = mode

        if mode == "access":
            interface["vlan"] = self.ask_validated(
                "VLAN", validate_vlan_id, default=20,
            )
        else:
            vlan_ids = self.ask_validated(
                "Allowed VLANs (comma-separated)", validate_vlan_list,
                default=[1, 10, 20, 30],
                help_text="VLANs allowed to pass over this trunk link.",
            )
            interface["allowed_vlans"] = vlan_ids

        desc = input("Description (optional): ").strip()
        if desc:
            interface["description"] = desc

        return interface

    def ask_static_routes(self) -> List[Dict[str, str]]:
        """Ask for static routes."""
        routes = []

        num_routes = self.ask_int("How many static routes?", 1)

        for i in range(1, num_routes + 1):
            route = {
                "destination": self.ask_validated(
                    f"Route {i} destination", validate_ip, default=f"10.0.{i}.0",
                    help_text="The network you want to reach (not a device's own IP).",
                ),
                "mask": self.ask_validated(
                    "Subnet mask", validate_subnet_mask, default="255.255.255.0",
                ),
                "next_hop": self.ask_validated(
                    "Next hop", validate_ip, default="10.0.1.1",
                    help_text="The IP of the router this device forwards matching traffic to.",
                ),
            }
            routes.append(route)

        return routes

    def ask_svi_config(self) -> List[Dict[str, Any]]:
        """Ask for SVI (VLAN interface) config."""
        vlans = []

        for vlan_id in [10, 20, 30]:
            vlan = {
                "id": vlan_id,
                "ip": self.ask_validated(
                    f"VLAN {vlan_id} IP", validate_ip, default=f"10.{vlan_id}.0.1",
                ),
                "mask": self.ask_validated(
                    "Subnet mask", validate_subnet_mask, default="255.255.255.0",
                ),
            }
            vlans.append(vlan)

        return vlans

    # ------------------------------------------------------------------
    # Preview + edit-after-preview loop
    # ------------------------------------------------------------------

    def show_preview(self, topology: Dict[str, Any]) -> str:
        """Show topology preview and ask what to do next.

        Returns:
            'save', 'edit', or 'cancel'
        """
        import yaml

        print("\n" + "=" * 60)
        print("TOPOLOGY PREVIEW")
        print("=" * 60)
        print(yaml.dump(topology, default_flow_style=False))
        print("=" * 60)

        print("What would you like to do?")
        print("  1. Save this topology")
        print("  2. Edit a section")
        print("  3. Cancel")

        while True:
            choice = input("Your choice (1-3): ").strip()
            if choice == "1":
                return "save"
            if choice == "2":
                return "edit"
            if choice == "3":
                return "cancel"
            print("  \u2717 Invalid choice. Enter 1, 2, or 3.")

    def ask_edit_section(self) -> str:
        """Ask which section of a custom build to redo.

        Returns:
            One of: 'global', 'devices', 'all'
        """
        print("\nWhat would you like to re-edit?")
        print("  1. Global settings (routing, VLANs, DNS/NTP/syslog, SSH)")
        print("  2. Devices (re-enter every device from scratch)")
        print("  3. Start over completely")

        while True:
            choice = input("Your choice (1-3): ").strip()
            if choice == "1":
                return "global"
            if choice == "2":
                return "devices"
            if choice == "3":
                return "all"
            print("  \u2717 Invalid choice. Enter 1, 2, or 3.")

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_custom(self, global_settings: Dict[str, Any] = None,
                    device_counts: Dict[str, int] = None,
                    reuse_devices: bool = False) -> Dict[str, Any]:
        """Run custom form (don't use preset).

        Accepts pre-existing answers so the edit loop can redo just one
        section:
        - global_settings=None -> re-ask global settings; otherwise reuse
        - device_counts=None -> re-ask device counts; otherwise reuse
        - reuse_devices=True -> reuse every previously-entered device's
          details verbatim instead of re-prompting for each one (used when
          only global settings changed, so the user isn't forced to retype
          every device just to fix a typo in, say, the domain name).
        """
        if global_settings is None:
            global_settings = self.ask_global_settings()
        if device_counts is None:
            device_counts = self.ask_device_counts()

        builder = YAMLBuilder()
        builder.set_global_fields(global_settings)

        if reuse_devices and self._last_devices is not None:
            for device_type, details in self._last_devices:
                if device_type == "router":
                    builder.add_router(details)
                elif device_type == "switch":
                    builder.add_switch(details, is_l3=False)
                else:  # l3_switch
                    builder.add_switch(details, is_l3=True)
        else:
            recorded_devices = []

            for i in range(1, device_counts["routers"] + 1):
                router_details = self.ask_device_details("router", i)
                builder.add_router(router_details)
                recorded_devices.append(("router", router_details))

            for i in range(1, device_counts["switches"] + 1):
                switch_details = self.ask_device_details("switch", i)
                builder.add_switch(switch_details, is_l3=False)
                recorded_devices.append(("switch", switch_details))

            for i in range(1, device_counts["ml_switches"] + 1):
                switch_details = self.ask_device_details("l3_switch", i)
                builder.add_switch(switch_details, is_l3=True)
                recorded_devices.append(("l3_switch", switch_details))

            self._last_devices = recorded_devices

        self._last_global_settings = global_settings
        self._last_device_counts = device_counts

        return builder.build()

    def run_preset(self, preset: str, name: str) -> Dict[str, Any]:
        """Run a preset template."""
        print(f"\nGenerating {preset.upper()} topology...")
        return build_from_preset(preset, name)

    def run(self):
        """Main entry point."""
        self.show_banner()

        preset = self.ask_preset()
        name = self.ask_topology_name()
        self._last_global_settings = None
        self._last_device_counts = None
        self._last_devices = None

        if preset == "custom":
            topology = self.run_custom()
        else:
            topology = self.run_preset(preset, name)

        while True:
            decision = self.show_preview(topology)

            if decision == "save":
                builder = YAMLBuilder()
                builder.topology = topology
                output_path = builder.save_yaml(name)
                print(f"\n\u2713 Topology saved to {output_path}")
                print(f"Next: autofig generate -i {output_path}")
                return

            if decision == "cancel":
                print("\n\u2717 Cancelled - nothing was saved.")
                return

            # decision == "edit"
            if preset == "custom":
                section = self.ask_edit_section()
                if section == "global":
                    topology = self.run_custom(
                        global_settings=None,
                        device_counts=self._last_device_counts,
                        reuse_devices=True,
                    )
                elif section == "devices":
                    topology = self.run_custom(
                        global_settings=self._last_global_settings,
                        device_counts=None,
                        reuse_devices=False,
                    )
                else:  # 'all'
                    topology = self.run_custom()
            else:
                # Presets are fixed templates - the only "edit" is switching
                # to a custom build so the user can actually change something.
                print(
                    "\nPresets aren't field-editable - switching to a custom "
                    "build so you can adjust things."
                )
                topology = self.run_custom()
                preset = "custom"


def build_topology():
    """Legacy function for compatibility."""
    form = PresetForm()
    form.run()


if __name__ == "__main__":
    build_topology()
