"""Web application for OSINTment"""
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_cors import CORS
import os
from datetime import datetime
from pathlib import Path
import json
import threading
import time

from ..core.config import Config
from ..core.spiderfoot_client import SpiderFootClient
from ..reports.report_generator import ReportGenerator
from ..utils.logger import setup_logger

logger = setup_logger('osintment.web')

app = Flask(__name__)
app.secret_key = os.urandom(24)
CORS(app)

# Global storage for active scans (in production, use Redis or database)
active_scans = {}
scan_progress = {}


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard showing all scans"""
    try:
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        scans = client.list_scans()
        return render_template('dashboard.html', scans=scans)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('dashboard.html', scans=[], error=str(e))


@app.route('/scan/new')
def new_scan_page():
    """Page to create a new scan"""
    return render_template('new_scan.html')


@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """API endpoint to start a new scan"""
    try:
        data = request.json
        target = data.get('target')
        scan_name = data.get('scan_name')
        scan_type = data.get('scan_type', 'all')

        if not target:
            return jsonify({'error': 'Target is required'}), 400

        # Initialize SpiderFoot client
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)

        # Start the scan
        scan_id = client.start_scan(target, scan_name=scan_name, scan_type=scan_type)

        # Store scan info
        active_scans[scan_id] = {
            'target': target,
            'scan_name': scan_name or f"Scan_{target}",
            'scan_type': scan_type,
            'started_at': datetime.now().isoformat(),
            'status': 'running'
        }

        # Start background thread to monitor progress
        thread = threading.Thread(target=monitor_scan, args=(scan_id,))
        thread.daemon = True
        thread.start()

        logger.info(f"Started scan {scan_id} for target {target}")

        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'message': 'Scan started successfully'
        })

    except Exception as e:
        logger.exception("Error starting scan")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan/<scan_id>/status')
def get_scan_status(scan_id):
    """API endpoint to get scan status"""
    try:
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        status = client.get_scan_status(scan_id)

        # Get progress info if available
        progress = scan_progress.get(scan_id, {})

        if status and status[0]:
            return jsonify({
                'success': True,
                'status': status[0],
                'progress': progress
            })
        else:
            return jsonify({'error': 'Scan not found'}), 404

    except Exception as e:
        logger.exception("Error getting scan status")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scan/<scan_id>/results')
def get_scan_results(scan_id):
    """API endpoint to get scan results"""
    try:
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        results = client.get_scan_results(scan_id)

        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        logger.exception("Error getting scan results")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """API endpoint to generate a report"""
    try:
        data = request.json
        scan_id = data.get('scan_id')
        output_format = data.get('format', 'html')
        custom_filename = data.get('filename')

        if not scan_id:
            return jsonify({'error': 'Scan ID is required'}), 400

        # Get scan data
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        scan_results = client.get_scan_results(scan_id)
        scan_summary = client.get_scan_summary(scan_id)

        if not scan_results:
            return jsonify({'error': 'No results found for this scan'}), 404

        # Prepare scan info
        scan_info = {
            'id': scan_id,
            'name': scan_summary.get('name', 'Unknown') if scan_summary else 'Unknown',
            'target': scan_summary.get('target', 'Unknown') if scan_summary else 'Unknown',
            'created': scan_summary.get('created', '') if scan_summary else ''
        }

        # Generate report
        generator = ReportGenerator()

        if output_format in ['html', 'pdf']:
            report_path = generator.generate_report(
                scan_results,
                scan_info,
                output_format=output_format,
                output_filename=custom_filename
            )
        elif output_format == 'json':
            report_path = Config.REPORT_OUTPUT_DIR / f"{custom_filename or f'scan_{scan_id}'}.json"
            generator.generate_json_export(scan_results, scan_info, report_path)
        elif output_format == 'csv':
            report_path = Config.REPORT_OUTPUT_DIR / f"{custom_filename or f'scan_{scan_id}'}.csv"
            generator.generate_csv_export(scan_results, report_path)
        else:
            return jsonify({'error': 'Invalid format'}), 400

        logger.info(f"Generated {output_format} report for scan {scan_id}")

        return jsonify({
            'success': True,
            'report_path': str(report_path),
            'filename': report_path.name,
            'download_url': f'/api/report/download/{report_path.name}'
        })

    except Exception as e:
        logger.exception("Error generating report")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/download/<filename>')
def download_report(filename):
    """Download a generated report"""
    try:
        report_path = Config.REPORT_OUTPUT_DIR / filename

        if not report_path.exists():
            return jsonify({'error': 'Report not found'}), 404

        return send_file(
            report_path,
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        logger.exception("Error downloading report")
        return jsonify({'error': str(e)}), 500


@app.route('/api/reports/list')
def list_reports():
    """List all generated reports"""
    try:
        reports = []

        if Config.REPORT_OUTPUT_DIR.exists():
            for file_path in Config.REPORT_OUTPUT_DIR.iterdir():
                if file_path.is_file():
                    reports.append({
                        'filename': file_path.name,
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        'extension': file_path.suffix,
                        'download_url': f'/api/report/download/{file_path.name}'
                    })

        # Sort by modification time, newest first
        reports.sort(key=lambda x: x['modified'], reverse=True)

        return jsonify({
            'success': True,
            'reports': reports
        })

    except Exception as e:
        logger.exception("Error listing reports")
        return jsonify({'error': str(e)}), 500


@app.route('/api/scans/list')
def list_scans():
    """API endpoint to list all scans"""
    try:
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        scans = client.list_scans()

        return jsonify({
            'success': True,
            'scans': scans
        })

    except Exception as e:
        logger.exception("Error listing scans")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config/check')
def check_config():
    """API endpoint to check configuration"""
    try:
        # Check SpiderFoot connectivity
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)
        modules = client.get_modules()

        return jsonify({
            'success': True,
            'spiderfoot_url': Config.SPIDERFOOT_URL,
            'connected': True,
            'modules_count': len(modules),
            'report_dir': str(Config.REPORT_OUTPUT_DIR),
            'company_name': Config.COMPANY_NAME,
            'report_author': Config.REPORT_AUTHOR
        })

    except Exception as e:
        logger.exception("Error checking config")
        return jsonify({
            'success': False,
            'spiderfoot_url': Config.SPIDERFOOT_URL,
            'connected': False,
            'error': str(e)
        }), 500


@app.route('/scan/<scan_id>')
def view_scan(scan_id):
    """View detailed scan information"""
    return render_template('scan_detail.html', scan_id=scan_id)


@app.route('/reports')
def reports_page():
    """Page to view all reports"""
    return render_template('reports.html')


def monitor_scan(scan_id):
    """Background thread to monitor scan progress"""
    try:
        client = SpiderFootClient(Config.SPIDERFOOT_URL, Config.SPIDERFOOT_API_KEY)

        while True:
            status = client.get_scan_status(scan_id)

            if status and status[0]:
                scan_status = status[0].get('status', '')

                # Update progress
                scan_progress[scan_id] = {
                    'status': scan_status,
                    'updated_at': datetime.now().isoformat()
                }

                # Check if scan is complete
                if 'FINISHED' in scan_status or 'ERROR' in scan_status or 'ABORTED' in scan_status:
                    if scan_id in active_scans:
                        active_scans[scan_id]['status'] = 'completed' if 'FINISHED' in scan_status else 'failed'
                    break

            time.sleep(10)  # Poll every 10 seconds

    except Exception as e:
        logger.exception(f"Error monitoring scan {scan_id}")


def run_web_server(host='0.0.0.0', port=5000, debug=False):
    """Run the Flask web server"""
    logger.info(f"Starting OSINTment Web Server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web_server(debug=True)
