# OSINTment

> Professional OSINT Automation and Reporting Tool with SpiderFoot Integration

OSINTment is a powerful command-line tool that integrates with SpiderFoot to automate Open Source Intelligence (OSINT) gathering and generates professional, consulting-grade reports in HTML and PDF formats.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

- **🔍 Automated OSINT Scanning**: Seamless integration with SpiderFoot for comprehensive intelligence gathering
- **📊 Professional Reports**: Generate elegant, consulting-grade reports in HTML and PDF formats
- **📈 Data Analysis**: Automatically categorize and analyze scan results
- **🎯 Multiple Scan Types**: Support for passive, footprint, and comprehensive scans
- **💼 Executive Summaries**: Auto-generated executive summaries with key metrics
- **🔐 Security Findings**: Highlight critical security issues and vulnerabilities
- **📱 Multiple Export Formats**: Export data in HTML, PDF, JSON, and CSV formats
- **🎨 Beautiful CLI**: Rich terminal interface with progress indicators and colored output

## Prerequisites

Before using OSINTment, you need to have SpiderFoot installed and running:

### Installing SpiderFoot

```bash
# Clone your SpiderFoot fork
git clone https://github.com/venutrue/spiderfoot.git
cd spiderfoot

# Install dependencies
pip3 install -r requirements.txt

# Run SpiderFoot
python3 sf.py -l 127.0.0.1:5001
```

SpiderFoot will be accessible at `http://localhost:5001`

## Installation

### Quick Install

```bash
# Clone the repository
git clone https://github.com/venutrue/OSINTment.git
cd OSINTment

# Install OSINTment
pip install -e .
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install the package
python setup.py install
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```bash
# SpiderFoot Configuration
SPIDERFOOT_URL=http://localhost:5001
SPIDERFOOT_API_KEY=

# Report Configuration
REPORT_OUTPUT_DIR=./reports
COMPANY_NAME=Your Company Name
REPORT_AUTHOR=OSINT Team

# Application Settings
LOG_LEVEL=INFO
DEBUG=False
```

## Usage

### Basic Commands

#### Run a Scan

```bash
# Scan a domain and generate HTML report
osintment scan example.com

# Scan with PDF output
osintment scan example.com --format pdf

# Scan with both HTML and PDF
osintment scan example.com --format both

# Run a passive scan only
osintment scan example.com --scan-type passive

# Custom output filename
osintment scan example.com --output my_report
```

#### Generate Report from Existing Scan

```bash
# Generate HTML report
osintment report SCAN_ID

# Generate PDF report
osintment report SCAN_ID --format pdf

# Export to JSON
osintment report SCAN_ID --format json

# Export to CSV
osintment report SCAN_ID --format csv
```

#### List All Scans

```bash
osintment list-scans
```

#### Check Scan Status

```bash
osintment status SCAN_ID
```

#### Check Configuration

```bash
osintment config-check
```

### Advanced Usage

#### Background Scans

Start a scan without waiting for completion:

```bash
# Start scan in background
osintment scan example.com --no-wait

# Later, generate report when ready
osintment report SCAN_ID --format pdf
```

#### Custom SpiderFoot Instance

Use a different SpiderFoot instance:

```bash
osintment scan example.com --spiderfoot-url http://192.168.1.100:5001
```

#### Scan Types

- **all**: Comprehensive scan with all modules
- **passive**: Passive reconnaissance only (no active queries)
- **footprint**: Footprinting and infrastructure mapping
- **investigate**: Deep investigation mode

```bash
osintment scan target.com --scan-type passive
```

## Report Features

OSINTment generates professional reports with the following sections:

### 📋 Executive Summary
- Total findings count
- Unique data types discovered
- Domain and IP statistics
- Top discovery categories with percentages

### 🎯 Critical Findings
- High-priority security issues
- Email addresses and phone numbers
- Leaked data and vulnerabilities
- Malicious indicators

### 🌐 Domain Intelligence
- Primary domains discovered
- Subdomains and affiliates
- IP address mapping
- Network infrastructure

### 💻 Technology Stack
- Web server technologies
- Software and frameworks
- Operating systems
- Server banners

### 📞 Contact Information
- Email addresses
- Phone numbers
- Physical addresses
- Social media profiles

### 🔒 Security Findings
- Vulnerabilities detected
- Malicious indicators
- Leaked credentials
- SSL/TLS issues

### 📊 Module Performance
- Module efficiency metrics
- Finding distribution
- Timeline of discoveries

## Output Examples

### HTML Report
Professional, web-based report with:
- Modern, responsive design
- Color-coded severity levels
- Interactive tables
- Executive dashboard with key metrics

### PDF Report
Print-ready PDF with:
- Professional cover page
- Table of contents
- Formatted sections
- Corporate branding options

### JSON Export
Structured data export for:
- Further analysis
- Integration with other tools
- Custom reporting
- Data archival

### CSV Export
Tabular data export for:
- Spreadsheet analysis
- Database import
- Bulk processing

## Project Structure

```
OSINTment/
├── osintment/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py                    # Command-line interface
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration management
│   │   └── spiderfoot_client.py  # SpiderFoot API client
│   ├── reports/
│   │   ├── __init__.py
│   │   ├── data_analyzer.py      # Data analysis and processing
│   │   └── report_generator.py   # Report generation engine
│   ├── templates/
│   │   └── html/
│   │       └── report_template.html  # HTML report template
│   └── utils/
│       ├── __init__.py
│       └── logger.py             # Logging configuration
├── reports/                      # Generated reports (created automatically)
├── .env.example                  # Example environment configuration
├── .gitignore
├── requirements.txt
├── setup.py
└── README.md
```

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/venutrue/OSINTment.git
cd OSINTment

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=osintment
```

## Troubleshooting

### SpiderFoot Connection Issues

If you get connection errors:

1. Ensure SpiderFoot is running:
   ```bash
   python3 sf.py -l 127.0.0.1:5001
   ```

2. Check the URL in your `.env` file matches SpiderFoot's address

3. Verify connectivity:
   ```bash
   osintment config-check
   ```

### PDF Generation Issues

If PDF generation fails:

1. Install WeasyPrint dependencies:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-dev python3-pip python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

   # macOS
   brew install cairo pango gdk-pixbuf libffi
   ```

2. Reinstall WeasyPrint:
   ```bash
   pip install --upgrade weasyprint
   ```

3. Reports will automatically fall back to HTML if PDF generation fails

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **SpiderFoot** - The powerful OSINT automation framework that powers OSINTment
- Built with Python, Click, Rich, Jinja2, and WeasyPrint

## Security Notice

This tool is designed for authorized security testing, research, and OSINT investigations only. Always ensure you have proper authorization before scanning any targets. Misuse of this tool may be illegal.

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/venutrue/OSINTment/issues
- SpiderFoot Documentation: https://github.com/venutrue/spiderfoot

---

**Made with ❤️ for the OSINT community**