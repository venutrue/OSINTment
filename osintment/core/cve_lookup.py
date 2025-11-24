"""CVE Lookup Service for OSINTment

Fetches CVE information for detected technologies from public vulnerability databases.
"""
import requests
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class CVELookupService:
    """Service to lookup CVEs for technologies and versions"""

    def __init__(self):
        """Initialize CVE lookup service"""
        self.nvd_api_base = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'OSINTment/1.0 (OSINT Security Tool)'
        })
        self._cache = {}

    def lookup_cves(self, technology: str, version: Optional[str] = None,
                    max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Lookup CVEs for a specific technology and version

        Args:
            technology: Technology name (e.g., 'Apache', 'nginx', 'WordPress')
            version: Optional version string
            max_results: Maximum number of CVEs to return

        Returns:
            List of CVE information dictionaries
        """
        cache_key = f"{technology}:{version or 'any'}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        cves = []

        try:
            # Build search query
            keyword = technology
            if version:
                keyword = f"{technology} {version}"

            # Query NVD API
            params = {
                'keywordSearch': keyword,
                'resultsPerPage': max_results,
                'keywordExactMatch': ''
            }

            response = self.session.get(self.nvd_api_base, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])

                for vuln in vulnerabilities[:max_results]:
                    cve_data = vuln.get('cve', {})
                    cve_info = self._parse_cve(cve_data)
                    if cve_info:
                        cves.append(cve_info)

        except Exception as e:
            # If NVD fails, try alternative sources or return empty
            pass

        self._cache[cache_key] = cves
        return cves

    def _parse_cve(self, cve_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse CVE data from NVD response"""
        try:
            cve_id = cve_data.get('id', '')

            # Get description
            descriptions = cve_data.get('descriptions', [])
            description = ''
            for desc in descriptions:
                if desc.get('lang') == 'en':
                    description = desc.get('value', '')
                    break

            # Get CVSS score
            metrics = cve_data.get('metrics', {})
            cvss_score = None
            severity = 'UNKNOWN'

            # Try CVSS 3.1 first, then 3.0, then 2.0
            for cvss_version in ['cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2']:
                if cvss_version in metrics:
                    cvss_data = metrics[cvss_version][0]
                    if cvss_version in ['cvssMetricV31', 'cvssMetricV30']:
                        cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                        severity = cvss_data.get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                    else:
                        cvss_score = cvss_data.get('cvssData', {}).get('baseScore')
                        severity = cvss_data.get('baseSeverity', 'UNKNOWN')
                    break

            # Get published date
            published = cve_data.get('published', '')
            if published:
                published = published.split('T')[0]

            # Get references
            references = []
            for ref in cve_data.get('references', [])[:3]:
                references.append(ref.get('url', ''))

            return {
                'cve_id': cve_id,
                'description': description[:500] + '...' if len(description) > 500 else description,
                'cvss_score': cvss_score,
                'severity': severity,
                'published': published,
                'references': references
            }

        except Exception as e:
            return None

    def get_technology_cves(self, technologies: List[Dict[str, Any]],
                           max_per_tech: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get CVEs for a list of technologies

        Args:
            technologies: List of technology dicts with 'name' and optional 'version'
            max_per_tech: Maximum CVEs per technology

        Returns:
            Dictionary mapping technology names to their CVEs
        """
        results = {}

        for tech in technologies:
            name = tech.get('name', '')
            version = tech.get('version')

            if not name:
                continue

            cves = self.lookup_cves(name, version, max_per_tech)

            if cves:
                key = f"{name} {version}" if version else name
                results[key] = cves

        return results

    def get_critical_cves(self, technologies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get only critical and high severity CVEs

        Args:
            technologies: List of technology dicts

        Returns:
            List of critical/high CVEs
        """
        all_cves = self.get_technology_cves(technologies)
        critical = []

        for tech, cves in all_cves.items():
            for cve in cves:
                severity = cve.get('severity', '').upper()
                if severity in ['CRITICAL', 'HIGH']:
                    cve['technology'] = tech
                    critical.append(cve)

        # Sort by CVSS score (highest first)
        critical.sort(key=lambda x: x.get('cvss_score', 0) or 0, reverse=True)

        return critical


def parse_technology_string(tech_string: str) -> Dict[str, Any]:
    """
    Parse a technology string to extract name and version

    Args:
        tech_string: Technology string like "Apache/2.4.41" or "nginx 1.18.0"

    Returns:
        Dictionary with 'name' and 'version' keys
    """
    # Common patterns for version extraction
    patterns = [
        r'^([^/\s]+)[/\s]+(\d+[\d.]+\d*).*$',  # Apache/2.4.41, nginx 1.18.0
        r'^([^(]+)\s*\(([^)]+)\).*$',          # Name (version)
        r'^([^0-9]+?)[\s]*([\d.]+).*$',        # Name 1.2.3
    ]

    for pattern in patterns:
        match = re.match(pattern, tech_string.strip())
        if match:
            return {
                'name': match.group(1).strip(),
                'version': match.group(2).strip(),
                'original': tech_string
            }

    # No version found
    return {
        'name': tech_string.strip(),
        'version': None,
        'original': tech_string
    }


def extract_technologies_from_results(scan_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Extract technology information from SpiderFoot scan results

    Args:
        scan_results: Raw scan results from SpiderFoot

    Returns:
        List of technology dictionaries with name and version
    """
    technologies = []
    seen = set()

    # Technology-related data types from SpiderFoot
    tech_types = [
        'WEBSERVER_TECHNOLOGY',
        'WEBSERVER_BANNER',
        'SOFTWARE_USED',
        'OPERATING_SYSTEM',
        'WEB_FRAMEWORK',
        'PROGRAMMING_LANGUAGE'
    ]

    for result in scan_results:
        data_type = result.get('type', '')
        data = result.get('data', '')

        if not data or data_type not in tech_types:
            continue

        # Parse technology string
        tech_info = parse_technology_string(data)

        # Create unique key
        key = f"{tech_info['name']}:{tech_info.get('version', '')}"

        if key not in seen:
            seen.add(key)
            tech_info['type'] = data_type
            tech_info['module'] = result.get('module', '')
            technologies.append(tech_info)

    return technologies


class TechnologyAnalyzer:
    """Analyze technologies and their security implications"""

    def __init__(self):
        self.cve_service = CVELookupService()

    def analyze(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive technology analysis

        Args:
            scan_results: Raw scan results from SpiderFoot

        Returns:
            Complete technology analysis with CVEs
        """
        # Extract technologies
        technologies = extract_technologies_from_results(scan_results)

        # Group by category
        categorized = self._categorize_technologies(technologies)

        # Get CVEs for each technology
        cves_by_tech = self.cve_service.get_technology_cves(technologies, max_per_tech=5)

        # Get critical CVEs
        critical_cves = self.cve_service.get_critical_cves(technologies)

        # Calculate risk score
        risk_score = self._calculate_risk_score(critical_cves)

        return {
            'technologies': technologies,
            'categorized': categorized,
            'cves_by_technology': cves_by_tech,
            'critical_cves': critical_cves[:10],  # Top 10 critical
            'total_technologies': len(technologies),
            'total_cves_found': sum(len(cves) for cves in cves_by_tech.values()),
            'critical_cve_count': len([c for c in critical_cves if c.get('severity') == 'CRITICAL']),
            'high_cve_count': len([c for c in critical_cves if c.get('severity') == 'HIGH']),
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score)
        }

    def _categorize_technologies(self, technologies: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize technologies by type"""
        categories = {
            'Web Servers': [],
            'Frameworks': [],
            'Programming Languages': [],
            'Operating Systems': [],
            'Other Software': []
        }

        type_mapping = {
            'WEBSERVER_TECHNOLOGY': 'Web Servers',
            'WEBSERVER_BANNER': 'Web Servers',
            'WEB_FRAMEWORK': 'Frameworks',
            'PROGRAMMING_LANGUAGE': 'Programming Languages',
            'OPERATING_SYSTEM': 'Operating Systems',
            'SOFTWARE_USED': 'Other Software'
        }

        for tech in technologies:
            category = type_mapping.get(tech.get('type', ''), 'Other Software')
            categories[category].append(tech)

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def _calculate_risk_score(self, critical_cves: List[Dict[str, Any]]) -> float:
        """Calculate overall risk score based on CVEs"""
        if not critical_cves:
            return 0.0

        total_score = 0
        for cve in critical_cves:
            cvss = cve.get('cvss_score', 0) or 0
            total_score += cvss

        # Average CVSS score weighted by count
        avg_score = total_score / len(critical_cves) if critical_cves else 0

        # Factor in the number of critical CVEs
        count_factor = min(len(critical_cves) / 10, 1.0)

        return round(avg_score * (1 + count_factor * 0.5), 1)

    def _get_risk_level(self, score: float) -> str:
        """Convert risk score to risk level"""
        if score >= 9.0:
            return 'CRITICAL'
        elif score >= 7.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        elif score > 0:
            return 'LOW'
        else:
            return 'NONE'
