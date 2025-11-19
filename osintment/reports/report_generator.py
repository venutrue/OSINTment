"""Professional report generator for OSINT findings"""
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import weasyprint
from .data_analyzer import ScanDataAnalyzer
from ..core.config import Config


class ReportGenerator:
    """Generate professional OSINT reports in multiple formats"""

    def __init__(self, config: Optional[Config] = None):
        """
        Initialize report generator

        Args:
            config: Configuration object (uses default if not provided)
        """
        self.config = config or Config()

        # Setup Jinja2 environment
        template_path = self.config.TEMPLATE_DIR / 'html'
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_path)),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_report(
        self,
        scan_results: list,
        scan_info: Dict[str, Any],
        output_format: str = 'html',
        output_filename: Optional[str] = None
    ) -> Path:
        """
        Generate a professional OSINT report

        Args:
            scan_results: Raw scan results from SpiderFoot
            scan_info: Scan metadata
            output_format: Output format ('html' or 'pdf')
            output_filename: Optional custom filename

        Returns:
            Path to generated report
        """
        # Analyze scan data
        analyzer = ScanDataAnalyzer(scan_results, scan_info)
        analysis = analyzer.generate_full_analysis()

        # Prepare report context
        context = self._prepare_report_context(analysis, scan_info)

        # Generate HTML
        html_content = self._render_html(context)

        # Determine output path
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            target_safe = scan_info.get('target', 'unknown').replace(':', '_').replace('/', '_')
            output_filename = f"osint_report_{target_safe}_{timestamp}"

        output_path = self.config.REPORT_OUTPUT_DIR / f"{output_filename}.{output_format}"

        # Save based on format
        if output_format == 'html':
            output_path.write_text(html_content, encoding='utf-8')
        elif output_format == 'pdf':
            self._generate_pdf(html_content, output_path)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        return output_path

    def _prepare_report_context(self, analysis: Dict[str, Any], scan_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare context data for report template

        Args:
            analysis: Analyzed scan data
            scan_info: Scan metadata

        Returns:
            Context dictionary for template
        """
        summary = analysis['executive_summary']

        # Parse scan date
        scan_date_str = summary.get('scan_date', datetime.now().isoformat())
        try:
            if 'T' in scan_date_str:
                scan_date = datetime.fromisoformat(scan_date_str.replace('Z', '+00:00'))
            else:
                scan_date = datetime.now()
        except:
            scan_date = datetime.now()

        return {
            'report_title': f"OSINT Assessment - {summary['scan_target']}",
            'target': summary['scan_target'],
            'scan_date': scan_date.strftime('%B %d, %Y at %H:%M UTC'),
            'report_date': datetime.now().strftime('%B %d, %Y at %H:%M UTC'),
            'author': self.config.REPORT_AUTHOR,
            'company_name': self.config.COMPANY_NAME,
            'logo_path': self.config.REPORT_LOGO_PATH if Path(self.config.REPORT_LOGO_PATH).exists() else None,

            # Analysis data
            'summary': summary,
            'critical_findings': analysis['critical_findings'],
            'domain_intel': analysis['domain_intelligence'],
            'technology_stack': analysis['technology_stack'],
            'network_intel': analysis['network_intelligence'],
            'contacts': analysis['contact_information'],
            'security_findings': analysis['security_findings'],
            'timeline': analysis['timeline'],
            'module_efficiency': analysis['module_efficiency'],
        }

    def _render_html(self, context: Dict[str, Any]) -> str:
        """
        Render HTML report from template

        Args:
            context: Template context

        Returns:
            Rendered HTML string
        """
        template = self.jinja_env.get_template('report_template.html')
        return template.render(**context)

    def _generate_pdf(self, html_content: str, output_path: Path):
        """
        Generate PDF from HTML content

        Args:
            html_content: HTML string
            output_path: Path to save PDF
        """
        try:
            # Create PDF using WeasyPrint
            html = weasyprint.HTML(string=html_content)
            html.write_pdf(
                str(output_path),
                stylesheets=None,
                presentational_hints=True
            )
        except Exception as e:
            # Fallback: save as HTML if PDF generation fails
            html_path = output_path.with_suffix('.html')
            html_path.write_text(html_content, encoding='utf-8')
            raise RuntimeError(
                f"PDF generation failed: {e}. "
                f"HTML report saved to: {html_path}"
            )

    def generate_json_export(self, scan_results: list, scan_info: Dict[str, Any], output_path: Path):
        """
        Export analyzed data as JSON

        Args:
            scan_results: Raw scan results
            scan_info: Scan metadata
            output_path: Path to save JSON
        """
        import json

        analyzer = ScanDataAnalyzer(scan_results, scan_info)
        analysis = analyzer.generate_full_analysis()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)

    def generate_csv_export(self, scan_results: list, output_path: Path):
        """
        Export raw scan results as CSV

        Args:
            scan_results: Raw scan results
            output_path: Path to save CSV
        """
        import csv

        if not scan_results:
            return

        # Get all unique keys from results
        keys = set()
        for result in scan_results:
            keys.update(result.keys())

        keys = sorted(list(keys))

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(scan_results)

    def generate_executive_summary(self, scan_results: list, scan_info: Dict[str, Any]) -> str:
        """
        Generate a brief text executive summary

        Args:
            scan_results: Raw scan results
            scan_info: Scan metadata

        Returns:
            Executive summary text
        """
        analyzer = ScanDataAnalyzer(scan_results, scan_info)
        summary = analyzer.get_executive_summary()
        domain_intel = analyzer.get_domain_intelligence()

        text = f"""
OSINT INTELLIGENCE REPORT - EXECUTIVE SUMMARY
{'=' * 60}

Target: {summary['scan_target']}
Scan Date: {summary['scan_date']}
Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

KEY METRICS
-----------
Total Findings: {summary['total_findings']}
Unique Data Types: {summary['unique_data_types']}
Domains Discovered: {domain_intel['total_domains']}
Subdomains Found: {domain_intel['total_subdomains']}
IP Addresses: {domain_intel['total_ips']}

TOP DISCOVERY CATEGORIES
------------------------
"""

        for category, count in summary['top_categories'][:5]:
            percentage = (count / summary['total_findings'] * 100)
            text += f"{category:<40} {count:>6} ({percentage:>5.1f}%)\n"

        text += f"\n{'=' * 60}\n"
        text += "For detailed findings, please refer to the full HTML/PDF report.\n"

        return text
