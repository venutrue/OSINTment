"""Command-line interface for OSINTment"""
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

from .core.config import Config
from .core.spiderfoot_client import SpiderFootClient
from .reports.report_generator import ReportGenerator
from .utils.logger import setup_logger


console = Console()
logger = setup_logger()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    OSINTment - Professional OSINT Automation and Reporting Tool

    Integrates with SpiderFoot for automated intelligence gathering
    and generates consulting-grade reports.
    """
    pass


@cli.command()
@click.argument('target')
@click.option('--name', '-n', help='Custom scan name')
@click.option('--scan-type', '-t', default='all',
              type=click.Choice(['all', 'passive', 'footprint', 'investigate']),
              help='Type of scan to perform')
@click.option('--format', '-f', 'output_format', default='html',
              type=click.Choice(['html', 'pdf', 'both']),
              help='Report output format')
@click.option('--output', '-o', help='Custom output filename (without extension)')
@click.option('--no-wait', is_flag=True, help='Start scan but don\'t wait for completion')
@click.option('--spiderfoot-url', help='SpiderFoot server URL (overrides config)')
def scan(target, name, scan_type, output_format, output, no_wait, spiderfoot_url):
    """
    Run an OSINT scan on a target and generate a professional report

    TARGET: Domain, IP address, email, or other identifier to investigate

    Examples:
        osintment scan example.com
        osintment scan 192.168.1.1 --format pdf
        osintment scan john@example.com --scan-type passive
    """
    console.print(Panel.fit(
        "[bold blue]OSINTment[/bold blue] - Professional OSINT Automation",
        border_style="blue"
    ))

    # Initialize SpiderFoot client
    sf_url = spiderfoot_url or Config.SPIDERFOOT_URL
    client = SpiderFootClient(sf_url, Config.SPIDERFOOT_API_KEY)

    console.print(f"\n[cyan]Target:[/cyan] {target}")
    console.print(f"[cyan]Scan Type:[/cyan] {scan_type}")
    console.print(f"[cyan]SpiderFoot:[/cyan] {sf_url}")

    try:
        # Start the scan
        console.print("\n[yellow]Starting scan...[/yellow]")
        scan_id = client.start_scan(target, scan_name=name, scan_type=scan_type)
        console.print(f"[green]✓[/green] Scan started with ID: [bold]{scan_id}[/bold]")

        if no_wait:
            console.print("\n[yellow]Scan is running in the background.[/yellow]")
            console.print(f"Use 'osintment report {scan_id}' to generate report when complete.")
            return

        # Wait for scan completion with progress indicator
        console.print("\n[yellow]Waiting for scan to complete...[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scanning...", total=None)

            success = client.wait_for_scan(scan_id, timeout=3600, poll_interval=10)
            progress.update(task, completed=True)

        if not success:
            console.print("[red]✗[/red] Scan failed or timed out")
            sys.exit(1)

        console.print("[green]✓[/green] Scan completed successfully")

        # Generate report
        _generate_report_for_scan(client, scan_id, output_format, output)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.exception("Scan failed")
        sys.exit(1)


@cli.command()
@click.argument('scan_id')
@click.option('--format', '-f', 'output_format', default='html',
              type=click.Choice(['html', 'pdf', 'both', 'json', 'csv']),
              help='Report output format')
@click.option('--output', '-o', help='Custom output filename (without extension)')
@click.option('--spiderfoot-url', help='SpiderFoot server URL (overrides config)')
def report(scan_id, output_format, output, spiderfoot_url):
    """
    Generate a professional report from an existing scan

    SCAN_ID: SpiderFoot scan identifier

    Examples:
        osintment report abc123 --format pdf
        osintment report abc123 --format both --output my_report
    """
    console.print(Panel.fit(
        "[bold blue]Report Generation[/bold blue]",
        border_style="blue"
    ))

    # Initialize SpiderFoot client
    sf_url = spiderfoot_url or Config.SPIDERFOOT_URL
    client = SpiderFootClient(sf_url, Config.SPIDERFOOT_API_KEY)

    try:
        _generate_report_for_scan(client, scan_id, output_format, output)
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.exception("Report generation failed")
        sys.exit(1)


@cli.command()
@click.option('--spiderfoot-url', help='SpiderFoot server URL (overrides config)')
def list_scans(spiderfoot_url):
    """List all available scans"""
    sf_url = spiderfoot_url or Config.SPIDERFOOT_URL
    client = SpiderFootClient(sf_url, Config.SPIDERFOOT_API_KEY)

    try:
        scans = client.list_scans()

        if not scans:
            console.print("[yellow]No scans found[/yellow]")
            return

        table = Table(title="Available Scans")
        table.add_column("Scan ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Target", style="yellow")
        table.add_column("Status", style="magenta")
        table.add_column("Created", style="blue")

        for scan in scans:
            table.add_row(
                scan.get('id', 'N/A')[:12],
                scan.get('name', 'N/A'),
                scan.get('target', 'N/A'),
                scan.get('status', 'N/A'),
                scan.get('created', 'N/A')
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument('scan_id')
@click.option('--spiderfoot-url', help='SpiderFoot server URL (overrides config)')
def status(scan_id, spiderfoot_url):
    """Check the status of a scan"""
    sf_url = spiderfoot_url or Config.SPIDERFOOT_URL
    client = SpiderFootClient(sf_url, Config.SPIDERFOOT_API_KEY)

    try:
        status_info = client.get_scan_status(scan_id)

        if not status_info or not status_info[0]:
            console.print("[red]Scan not found[/red]")
            return

        info = status_info[0]

        console.print(f"\n[cyan]Scan ID:[/cyan] {scan_id}")
        console.print(f"[cyan]Name:[/cyan] {info.get('name', 'N/A')}")
        console.print(f"[cyan]Target:[/cyan] {info.get('target', 'N/A')}")
        console.print(f"[cyan]Status:[/cyan] {info.get('status', 'N/A')}")
        console.print(f"[cyan]Created:[/cyan] {info.get('created', 'N/A')}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


@cli.command()
def config_check():
    """Check configuration and connectivity"""
    console.print(Panel.fit(
        "[bold blue]Configuration Check[/bold blue]",
        border_style="blue"
    ))

    # Check SpiderFoot connectivity
    console.print(f"\n[cyan]SpiderFoot URL:[/cyan] {Config.SPIDERFOOT_URL}")

    try:
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        modules = client.get_modules()
        console.print(f"[green]✓[/green] Connected successfully ({len(modules)} modules available)")
    except Exception as e:
        console.print(f"[red]✗[/red] Connection failed: {str(e)}")

    # Check directories
    console.print(f"\n[cyan]Report Output Directory:[/cyan] {Config.REPORT_OUTPUT_DIR}")
    console.print(f"[green]✓[/green] Directory exists" if Config.REPORT_OUTPUT_DIR.exists() else "[yellow]![/yellow] Directory will be created")

    console.print(f"\n[cyan]Company Name:[/cyan] {Config.COMPANY_NAME}")
    console.print(f"[cyan]Report Author:[/cyan] {Config.REPORT_AUTHOR}")


def _generate_report_for_scan(client: SpiderFootClient, scan_id: str, output_format: str, custom_output: str = None):
    """Helper function to generate reports"""
    console.print(f"\n[yellow]Retrieving scan results for {scan_id}...[/yellow]")

    # Get scan data
    scan_results = client.get_scan_results(scan_id)
    scan_summary = client.get_scan_summary(scan_id)

    if not scan_results:
        console.print("[yellow]Warning:[/yellow] No results found for this scan")
        return

    # Prepare scan info
    scan_info = {
        'id': scan_id,
        'name': scan_summary.get('name', 'Unknown') if scan_summary else 'Unknown',
        'target': scan_summary.get('target', 'Unknown') if scan_summary else 'Unknown',
        'created': scan_summary.get('created', '') if scan_summary else ''
    }

    console.print(f"[green]✓[/green] Retrieved {len(scan_results)} findings")

    # Initialize report generator
    generator = ReportGenerator()

    # Generate reports based on format
    formats_to_generate = ['html', 'pdf'] if output_format == 'both' else [output_format]

    generated_files = []

    for fmt in formats_to_generate:
        if fmt in ['html', 'pdf']:
            console.print(f"\n[yellow]Generating {fmt.upper()} report...[/yellow]")
            output_path = generator.generate_report(
                scan_results,
                scan_info,
                output_format=fmt,
                output_filename=custom_output
            )
            console.print(f"[green]✓[/green] {fmt.upper()} report saved: [bold]{output_path}[/bold]")
            generated_files.append(output_path)

        elif fmt == 'json':
            console.print(f"\n[yellow]Exporting JSON data...[/yellow]")
            json_path = Config.REPORT_OUTPUT_DIR / f"{custom_output or f'scan_{scan_id}'}.json"
            generator.generate_json_export(scan_results, scan_info, json_path)
            console.print(f"[green]✓[/green] JSON export saved: [bold]{json_path}[/bold]")
            generated_files.append(json_path)

        elif fmt == 'csv':
            console.print(f"\n[yellow]Exporting CSV data...[/yellow]")
            csv_path = Config.REPORT_OUTPUT_DIR / f"{custom_output or f'scan_{scan_id}'}.csv"
            generator.generate_csv_export(scan_results, csv_path)
            console.print(f"[green]✓[/green] CSV export saved: [bold]{csv_path}[/bold]")
            generated_files.append(csv_path)

    # Show executive summary
    console.print("\n" + "="*60)
    exec_summary = generator.generate_executive_summary(scan_results, scan_info)
    console.print(exec_summary)
    console.print("="*60 + "\n")

    console.print("[bold green]Report generation complete![/bold green]")
    for file_path in generated_files:
        console.print(f"  → {file_path}")


def main():
    """Entry point for the CLI"""
    cli()


if __name__ == '__main__':
    main()
