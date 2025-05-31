print("Script starting...")

import os

print("Current directory:", os.getcwd())

import yaml
from jinja2 import Environment, FileSystemLoader

# Load YAML input
with open("inputs/sample.yaml", "r") as f:
    data = yaml.safe_load(f)

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("sample_router.j2")

# Render config
output = template.render(data)

# Print result
print("Rendered output:\n", output)
