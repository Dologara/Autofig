"""Command-line interface for Autofig network configuration generator."""

import click
from pathlib import Path
import sys

from autofig import __version__
from autofig.core.loader import load_yaml, load_device_defaults
from autofig.core.processor import process_topology, build_device_defaults_map
from autofig.core.renderer import render_topology_with_errors
from autofig.core.validators import validate_topology
from autofig.core.cli_builder import PresetForm
from autofig.core.config import AUTOFIG_OUTPUT_DIR
from autofig.core.exceptions import AutofigError, TopologyValidationError, DeviceValidationError


@click.group()
@click.version_option(version=__version__)
def cli():
    """🚀 Autofig - Network Configuration Generator
    
    Generate Cisco IOS configurations for learning labs.
    
    Examples:
        autofig generate --input topology.yaml --output ./configs
        autofig build
        autofig build --preset quick --name my_lab
    """
    pass

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
            click.echo(f"\n❌ FAILED: no configs were generated.", err=True)
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


@cli.command()
def info():
    """Show Autofig information and supported vendors.
    
    Displays version, supported vendors, device types, and system info.
    """
    from autofig.core.vendors import get_supported_vendors, get_supported_device_types
    
    click.echo("\n" + "="*60)
    click.echo("🚀 AUTOFIG - Network Configuration Generator")
    click.echo("="*60)
    click.echo(f"\nVersion: {__version__}")
    click.echo("Status: Beta")
    click.echo("License: MIT")
    
    click.echo("\n" + "-"*60)
    click.echo("Supported Vendors:")
    click.echo("-"*60)
    for vendor in get_supported_vendors():
        device_types = get_supported_device_types(vendor)
        click.echo(f"\n  {vendor}")
        for device_type in device_types:
            click.echo(f"    - {device_type}")
    
    click.echo("\n" + "-"*60)
    click.echo("Commands:")
    click.echo("-"*60)
    click.echo("  autofig generate   Generate configs from YAML")
    click.echo("  autofig build      Build topology interactively")
    click.echo("  autofig info       Show this information")
    
    click.echo("\n" + "-"*60)
    click.echo("Examples:")
    click.echo("-"*60)
    click.echo("  autofig generate --input topology.yaml --output ./configs")
    click.echo("  autofig build")
    click.echo("  autofig build --preset quick --name my_lab")
    click.echo("\n" + "="*60 + "\n")


if __name__ == "__main__":
    cli()
