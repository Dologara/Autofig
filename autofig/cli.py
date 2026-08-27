"""Command-line interface for Autofig network configuration generator."""

import json
import sys
from pathlib import Path

import click

from autofig import __version__
from autofig.core.loader import load_yaml, load_device_defaults
from autofig.core.processor import process_topology, build_device_defaults_map
from autofig.core.renderer import render_topology_with_errors
from autofig.core.validators import validate_topology
from autofig.core.cli_builder import PresetForm
from autofig.core.config import AUTOFIG_OUTPUT_DIR
from autofig.core.exceptions import AutofigError, TopologyValidationError, DeviceValidationError
from autofig.db.database import (
    DB_PATH,
    init_db,
    import_topology,
    hydrate_topology,
    list_topologies,
    delete_topology,
)


@click.group()
@click.version_option(version=__version__)
def cli():
    """🚀 Autofig - Network Configuration Generator

    Generate Cisco IOS configurations for learning labs.

    GENERATE CONFIGS:
      generate       Generate configs from a YAML topology file
      build          Build a topology interactively
      generate-from  Generate configs from a saved (DB) topology

    MANAGE SAVED TOPOLOGIES:
      list           List all saved topologies
      show           Display a saved topology's details
      import         Import a topology from YAML into the database
      delete         Delete a saved topology

    UTILITIES:
      info           Show version and supported vendors

    Examples:
        autofig generate --input topology.yaml --output ./configs
        autofig build --preset quick --name my_lab
        autofig import topology.yaml
        autofig generate-from 1
    """
    # Lazily create the DB on first use, so a bare `autofig generate`
    # against a YAML file (no DB involved at all) doesn't require it -
    # but any command that touches autofig.db.database gets a ready DB.
    if not DB_PATH.exists():
        init_db()


# ============================================================================
# CONFIG GENERATION (Phase 1)
# ============================================================================

@cli.command()
@click.option("--input", "-i", type=click.Path(exists=True), required=True, help="Input YAML topology file")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output directory for configs")
def generate(input, output):
    """Generate Cisco IOS configs from a YAML topology file."""
    try:
        if output:
            output_dir = Path(output)
        else:
            output_dir = AUTOFIG_OUTPUT_DIR

        output_dir.mkdir(parents=True, exist_ok=True)

        click.echo(f"📂 Output directory: {output_dir}")
        click.echo(f"📖 Loading topology from {input}...")
        topology = load_yaml(input)

        click.echo("🔍 Validating topology...")
        validate_topology(topology)

        click.echo("🔧 Building device defaults...")
        device_defaults_map = build_device_defaults_map(load_device_defaults)

        click.echo("⚙️  Processing topology...")
        processed_topology = process_topology(topology, device_defaults_map)

        click.echo("🎨 Rendering configurations...")
        result = render_topology_with_errors(processed_topology, output_dir)

        generated = result["data"]["generated"]
        total = result["metadata"]["total_devices"]

        if result["status"] == "success":
            click.echo(f"\n✅ SUCCESS! Generated {generated} config file(s):")
            for filepath in result["data"]["saved"]:
                click.echo(f"   - {Path(filepath).name}")
            click.echo(f"\n📁 All configs saved to: {output_dir}")
        elif result["status"] == "partial_success":
            click.echo(f"\n⚠️  PARTIAL SUCCESS: {generated}/{total} config(s) generated.")
            for filepath in result["data"]["saved"]:
                click.echo(f"   - {Path(filepath).name}")
            click.echo("\nErrors:")
            for err in result["errors"]:
                click.echo(f"   ✗ {err['device']}: {err['error']}", err=True)
            click.echo(f"\n📁 Successful configs saved to: {output_dir}")
        else:
            click.echo("\n❌ FAILED: no configs were generated.", err=True)
            for err in result["errors"]:
                click.echo(f"   ✗ {err['device']}: {err['error']}", err=True)
            sys.exit(1)

    except (TopologyValidationError, DeviceValidationError) as e:
        click.echo(f"❌ Invalid topology: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError as e:
        click.echo(f"❌ ERROR: File not found - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--preset",
    type=click.Choice(["quick", "medium", "enterprise", "custom"], case_sensitive=False),
    default=None,
    help="Use preset template (quick/medium/enterprise/custom)"
)
@click.option(
    "--name", "-n",
    default=None,
    help="Topology name"
)
def build(preset, name):
    """Build a new topology interactively.

    Launch an interactive form to create a network topology.
    Choose a preset template or build custom configuration.

    Examples:
        autofig build                              # Full interactive form
        autofig build --preset quick --name my_lab # Quick preset
    """
    try:
        form = PresetForm()
        form.run(preset=preset, name=name)
    except KeyboardInterrupt:
        click.echo("\n\n❌ Build cancelled by user")
        sys.exit(1)
    except AutofigError as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


# ============================================================================
# SAVED TOPOLOGIES - DATABASE COMMANDS (Phase 2.0)
# ============================================================================

@cli.command(name="list")
def list_cmd():
    """List all saved topologies."""
    try:
        topologies = list_topologies()
        if not topologies:
            click.echo("No topologies saved yet")
            return

        click.echo("\n📋 Saved Topologies:")
        click.echo("═" * 70)
        click.echo(f"{'ID':<4} {'Name':<20} {'Vendor':<10} {'Routing':<12} {'Created':<20}")
        click.echo("─" * 70)

        for topo in topologies:
            click.echo(
                f"{topo['id']:<4} "
                f"{topo['name']:<20} "
                f"{topo['vendor']:<10} "
                f"{topo['routing_protocol']:<12} "
                f"{topo['created_at']:<20}"
            )

        click.echo("═" * 70)
        click.echo(f"\nTotal: {len(topologies)} topology(ies)\n")

    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("topology_id", type=int)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def show(topology_id, output_json):
    """Show a saved topology's details."""
    try:
        topology = hydrate_topology(topology_id)

        if output_json:
            click.echo(json.dumps(topology, indent=2))
            return

        click.echo(f"\n📊 Topology: {topology['name']}")
        click.echo("─" * 60)
        click.echo(f"ID:              {topology_id}")
        click.echo(f"Vendor:          {topology['vendor']}")
        click.echo(f"Routing:         {topology['routing_protocol']}")

        if topology.get("domain_name"):
            click.echo(f"Domain:          {topology['domain_name']}")

        if topology.get("devices"):
            click.echo(f"\n🖥️  Devices ({len(topology['devices'])}):")
            for device in topology["devices"]:
                click.echo(f"  - {device.get('name', 'unknown')} ({device.get('type', 'unknown')})")

        # Note: keyed on 'id' to match the topology dict shape load_yaml()
        # already produces (see data/topologies/*.yaml) - not 'vid'.
        if topology.get("vlans"):
            click.echo(f"\n📡 VLANs ({len(topology['vlans'])}):")
            for vlan in topology["vlans"]:
                click.echo(f"  {vlan.get('id', '?')} - {vlan.get('name', 'unknown')}")

        if topology.get("devices"):
            total_ifaces = sum(len(d.get("interfaces", [])) for d in topology["devices"])
            if total_ifaces > 0:
                click.echo(f"\n🛣️  Interfaces: {total_ifaces} total")

        click.echo()

    except ValueError as e:
        click.echo(f"❌ Topology not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


@cli.command(name="import")
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--name", "-n", help="Topology name (defaults to the value in the YAML, or the filename)")
def import_cmd(yaml_file, name):
    """Import a topology from a YAML file into the database."""
    try:
        topology = load_yaml(yaml_file)

        if name:
            topology["name"] = name
        elif "name" not in topology:
            topology["name"] = Path(yaml_file).stem

        validate_topology(topology)

        topology_id = import_topology(topology)

        click.echo(f"✅ Topology '{topology['name']}' imported (ID {topology_id})")

    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("topology_id", type=int)
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation")
def delete(topology_id, yes):
    """Delete a saved topology."""
    try:
        if not yes:
            if not click.confirm(f"Delete topology {topology_id}?"):
                click.echo("Cancelled")
                return

        if delete_topology(topology_id):
            click.echo(f"✅ Topology {topology_id} deleted")
        else:
            click.echo(f"❌ Topology {topology_id} not found", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


@cli.command(name="generate-from")
@click.argument("topology_id", type=int)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def generate_from(topology_id, output):
    """Generate configs from a saved (DB) topology."""
    try:
        topology = hydrate_topology(topology_id)

        # Reuses AUTOFIG_OUTPUT_DIR (same default + env-var override as
        # `generate`) rather than a separately hardcoded path, so
        # AUTOFIG_OUTPUT_DIR behaves consistently across both commands.
        if output:
            output_dir = Path(output)
        else:
            output_dir = AUTOFIG_OUTPUT_DIR / f"topology_{topology_id}"

        output_dir.mkdir(parents=True, exist_ok=True)

        validate_topology(topology)

        device_defaults = build_device_defaults_map(load_device_defaults)
        processed = process_topology(topology, device_defaults)

        result = render_topology_with_errors(processed, output_dir)

        click.echo("\n✅ Generation Complete")
        click.echo(f"Generated: {result['data']['generated']}/{result['metadata']['total_devices']}")
        click.echo(f"Output: {output_dir}")

        if result["data"]["saved"]:
            click.echo("\nFiles:")
            for fname in result["data"]["saved"]:
                click.echo(f"  - {Path(fname).name}")

        if result["errors"]:
            click.echo("\n⚠️  Errors:")
            for err in result["errors"]:
                click.echo(f"  - {err['device']}: {err['error']}")

        click.echo()

    except ValueError as e:
        click.echo(f"❌ Topology not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ ERROR: {e}", err=True)
        sys.exit(1)


# ============================================================================
# UTILITIES
# ============================================================================

@cli.command()
def info():
    """Show Autofig information and supported vendors.

    Displays version, supported vendors, device types, and system info.
    """
    from autofig.core.vendors import get_supported_vendors, get_supported_device_types

    click.echo("\n" + "=" * 60)
    click.echo("🚀 AUTOFIG - Network Configuration Generator")
    click.echo("=" * 60)
    click.echo(f"\nVersion: {__version__}")
    click.echo("Status: Beta")
    click.echo("License: MIT")

    click.echo("\n" + "-" * 60)
    click.echo("Supported Vendors:")
    click.echo("-" * 60)
    for vendor in get_supported_vendors():
        device_types = get_supported_device_types(vendor)
        click.echo(f"\n  {vendor}")
        for device_type in device_types:
            click.echo(f"    - {device_type}")

    click.echo("\n" + "-" * 60)
    click.echo("Commands:")
    click.echo("-" * 60)
    click.echo("  autofig generate       Generate configs from YAML")
    click.echo("  autofig build          Build topology interactively")
    click.echo("  autofig list           List saved topologies")
    click.echo("  autofig show ID        Show a saved topology")
    click.echo("  autofig import FILE    Import a topology into the database")
    click.echo("  autofig delete ID      Delete a saved topology")
    click.echo("  autofig generate-from ID  Generate configs from a saved topology")
    click.echo("  autofig info           Show this information")

    click.echo("\n" + "-" * 60)
    click.echo("Examples:")
    click.echo("-" * 60)
    click.echo("  autofig generate --input topology.yaml --output ./configs")
    click.echo("  autofig build --preset quick --name my_lab")
    click.echo("  autofig import topology.yaml")
    click.echo("  autofig generate-from 1")
    click.echo("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    cli()
