import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

DATA_FILE = Path("data/devices.yaml")
TEMPLATE_DIR = Path("templates")
OUTPUT_DIR = Path("output")

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    with open(DATA_FILE) as f:
        data = yaml.safe_load(f)

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    for device in data["devices"]:
        # Pick template by device type
        template_name = f"{device['type'].lower()}.j2"
        try:
            template = env.get_template(template_name)
        except Exception:
            template = env.get_template("base_template.j2")

        config_text = template.render(device=device, defaults=data["defaults"])
        out_path = OUTPUT_DIR / f"{device['name']}_config.txt"
        out_path.write_text(config_text)
        print(f"✅ Generated config for {device['name']} using {template_name}")

if __name__ == "__main__":
    main()
