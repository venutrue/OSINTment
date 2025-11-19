# OSINTment Quick Start Guide

Get up and running with OSINTment in 5 minutes!

## Step 1: Install SpiderFoot

```bash
# Clone SpiderFoot
git clone https://github.com/venutrue/spiderfoot.git
cd spiderfoot

# Install and run
pip3 install -r requirements.txt
python3 sf.py -l 127.0.0.1:5001
```

Keep SpiderFoot running in this terminal.

## Step 2: Install OSINTment

Open a new terminal:

```bash
# Clone OSINTment
git clone https://github.com/venutrue/OSINTment.git
cd OSINTment

# Install
pip install -e .

# Create configuration
cp .env.example .env
```

## Step 3: Run Your First Scan

```bash
# Check configuration
osintment config-check

# Run a scan
osintment scan example.com
```

The tool will:
1. Start the OSINT scan in SpiderFoot
2. Wait for completion (this may take several minutes)
3. Automatically generate a professional HTML report
4. Display an executive summary in your terminal

## Step 4: View Your Report

Reports are saved in the `./reports` directory:

```bash
# List generated reports
ls -lh reports/

# Open the HTML report in your browser
# (Path will be shown in the terminal output)
```

## Common Commands

```bash
# Scan with PDF output
osintment scan example.com --format pdf

# Run passive scan only (faster, non-intrusive)
osintment scan example.com --scan-type passive

# List all scans
osintment list-scans

# Generate report from existing scan
osintment report SCAN_ID --format pdf
```

## Customization

Edit your `.env` file to customize:

```bash
# Your company name (appears on reports)
COMPANY_NAME=My Security Firm

# Report author
REPORT_AUTHOR=Security Team

# Output directory
REPORT_OUTPUT_DIR=./my_reports
```

## Tips

1. **Passive scans** are faster and less intrusive - great for initial reconnaissance
2. **PDF reports** are perfect for client deliverables
3. Use `--no-wait` for long scans and generate the report later
4. Export to JSON/CSV for integration with other tools

## Need Help?

- Check configuration: `osintment config-check`
- View all commands: `osintment --help`
- Get command help: `osintment scan --help`
- Report issues: https://github.com/venutrue/OSINTment/issues

Happy OSINT hunting!
