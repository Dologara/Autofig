import yaml
from pathlib import Path

TOPOLOGY_DIR = Path("data/topologies")
TOPOLOGY_DIR.mkdir(parents=True, exist_ok=True)

def ask_int(prompt, default=0):
    """Ask for an integer with a default."""
    value = input(f"{prompt} [{default}]: ").strip()
    return int(value) if value.isdigit() else default

def build_topology():
    print("\n=== Autofig Dynamic Builder ===\n")

    # 1️⃣ Basic setup
    name = input("Enter topology name [dynamic_lab]: ").strip() or "dynamic_lab"
    vendor = input("Vendor (e.g., Cisco) [Cisco]: ").strip() or "Cisco"

    # 2️⃣ Device counts
    routers = ask_int("How many routers?", 1)
    mls = ask_int("How many multilayer switches?", 1)
    switches = ask_int("How many access switches?", 2)

    devices = []

    # 3️⃣ Generate routers
    for i in range(1, routers + 1):
        devices.append({
            "name": f"R{i}",
            "type": "router",
            "vendor": vendor,
            "hostname": f"Router{i}"
        })

    # 4️⃣ Generate multilayer switches
    for i in range(1, mls + 1):
        devices.append({
            "name": f"MLS{i}",
            "type": "multilayer_switch",
            "vendor": vendor,
            "hostname": f"MLSwitch{i}"
        })

    # 5️⃣ Generate access switches
    for i in range(1, switches + 1):
        devices.append({
            "name": f"SW{i}",
            "type": "switch",
            "vendor": vendor,
            "hostname": f"Switch{i}"
        })

    topology = {
        "topology_name": name,
        "devices": devices
    }

    # 6️⃣ Save YAML
    out_file = TOPOLOGY_DIR / f"{name}.yaml"
    with open(out_file, "w") as f:
        yaml.safe_dump(topology, f)
    print(f"\n✅ Topology saved as {out_file}")

    return out_file

if __name__ == "__main__":
    build_topology()
