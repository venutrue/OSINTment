"""SpiderFoot API client for OSINTment"""
import requests
import json
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class SpiderFootClient:
    """Client for interacting with SpiderFoot API"""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize SpiderFoot client

        Args:
            base_url: SpiderFoot server URL
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})

    def start_scan(self, target: str, scan_name: Optional[str] = None,
                   modules: Optional[List[str]] = None, scan_type: str = 'all') -> str:
        """
        Start a new SpiderFoot scan

        Args:
            target: Target to scan (domain, IP, email, etc.)
            scan_name: Optional name for the scan
            modules: List of specific modules to run (None = all modules)
            scan_type: Type of scan ('all', 'passive', 'investigate', etc.)

        Returns:
            Scan ID
        """
        if not scan_name:
            scan_name = f"Scan_{target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Get available module list if not specified
        if modules is None:
            modules_data = self.get_modules()
            if scan_type == 'passive':
                modules = [m for m, info in modules_data.items()
                          if info.get('type') == 'passive']
            else:
                modules = list(modules_data.keys())

        payload = {
            'scanname': scan_name,
            'scantarget': target,
            'modulelist': ','.join(modules) if modules else '',
            'typelist': scan_type
        }

        response = self.session.post(f'{self.base_url}/api', params=payload)
        response.raise_for_status()

        result = response.json()
        return result[0]  # Returns scan ID

    def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """
        Get status of a scan

        Args:
            scan_id: Scan ID to check

        Returns:
            Scan status information
        """
        response = self.session.get(f'{self.base_url}/api',
                                    params={'q': 'scanstatus', 'id': scan_id})
        response.raise_for_status()
        return response.json()

    def wait_for_scan(self, scan_id: str, timeout: int = 3600,
                     poll_interval: int = 10) -> bool:
        """
        Wait for scan to complete

        Args:
            scan_id: Scan ID to wait for
            timeout: Maximum time to wait in seconds
            poll_interval: Time between status checks in seconds

        Returns:
            True if scan completed successfully, False otherwise
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_scan_status(scan_id)

            if status and status[0]:
                scan_status = status[0].get('status', '')

                if 'FINISHED' in scan_status:
                    return True
                elif 'ERROR' in scan_status or 'ABORTED' in scan_status:
                    return False

            time.sleep(poll_interval)

        return False

    def get_scan_results(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Get results from a completed scan

        Args:
            scan_id: Scan ID to retrieve results for

        Returns:
            List of scan results
        """
        response = self.session.get(f'{self.base_url}/api',
                                    params={'q': 'scanresults', 'id': scan_id})
        response.raise_for_status()
        return response.json()

    def get_scan_logs(self, scan_id: str) -> List[Dict[str, Any]]:
        """
        Get logs from a scan

        Args:
            scan_id: Scan ID to retrieve logs for

        Returns:
            List of log entries
        """
        response = self.session.get(f'{self.base_url}/api',
                                    params={'q': 'scanlogs', 'id': scan_id})
        response.raise_for_status()
        return response.json()

    def get_modules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available SpiderFoot modules

        Returns:
            Dictionary of module information
        """
        response = self.session.get(f'{self.base_url}/api', params={'q': 'modules'})
        response.raise_for_status()
        return response.json()

    def export_scan(self, scan_id: str, export_format: str = 'json') -> Any:
        """
        Export scan results in specified format

        Args:
            scan_id: Scan ID to export
            export_format: Format to export (json, csv, gexf)

        Returns:
            Exported data
        """
        params = {
            'q': 'scanexport',
            'id': scan_id,
            'format': export_format
        }

        response = self.session.get(f'{self.base_url}/api', params=params)
        response.raise_for_status()

        if export_format == 'json':
            return response.json()
        else:
            return response.text

    def get_scan_summary(self, scan_id: str) -> Dict[str, Any]:
        """
        Get summary information about a scan

        Args:
            scan_id: Scan ID

        Returns:
            Summary information
        """
        response = self.session.get(f'{self.base_url}/api',
                                    params={'q': 'scansummary', 'id': scan_id})
        response.raise_for_status()
        return response.json()

    def list_scans(self) -> List[Dict[str, Any]]:
        """
        List all scans

        Returns:
            List of scan information
        """
        response = self.session.get(f'{self.base_url}/api', params={'q': 'scanlist'})
        response.raise_for_status()
        return response.json()

    def delete_scan(self, scan_id: str) -> bool:
        """
        Delete a scan

        Args:
            scan_id: Scan ID to delete

        Returns:
            True if successful
        """
        response = self.session.get(f'{self.base_url}/api',
                                    params={'q': 'scandelete', 'id': scan_id})
        response.raise_for_status()
        return True
