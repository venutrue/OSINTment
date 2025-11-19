"""Data analysis and processing for scan results"""
from typing import Dict, List, Any, Set
from collections import defaultdict, Counter
from datetime import datetime


class ScanDataAnalyzer:
    """Analyze and structure SpiderFoot scan results"""

    def __init__(self, scan_results: List[Dict[str, Any]], scan_info: Dict[str, Any]):
        """
        Initialize analyzer with scan data

        Args:
            scan_results: Raw scan results from SpiderFoot
            scan_info: Scan metadata
        """
        self.scan_results = scan_results
        self.scan_info = scan_info
        self.categorized_data = self._categorize_results()

    def _categorize_results(self) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize scan results by data type"""
        categories = defaultdict(list)

        for result in self.scan_results:
            data_type = result.get('type', 'Unknown')
            categories[data_type].append({
                'data': result.get('data', ''),
                'module': result.get('module', ''),
                'source': result.get('source', ''),
                'confidence': result.get('confidence', 100),
                'timestamp': result.get('timestamp', '')
            })

        return dict(categories)

    def get_executive_summary(self) -> Dict[str, Any]:
        """Generate executive summary statistics"""
        total_findings = len(self.scan_results)
        unique_types = len(self.categorized_data.keys())

        # Count findings by category
        category_counts = {cat: len(items) for cat, items in self.categorized_data.items()}

        # Get top categories
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        # Module statistics
        module_stats = Counter(r.get('module', 'Unknown') for r in self.scan_results)

        return {
            'total_findings': total_findings,
            'unique_data_types': unique_types,
            'category_counts': category_counts,
            'top_categories': top_categories,
            'module_stats': dict(module_stats.most_common(10)),
            'scan_target': self.scan_info.get('target', 'Unknown'),
            'scan_name': self.scan_info.get('name', 'Unknown'),
            'scan_date': self.scan_info.get('created', datetime.now().isoformat())
        }

    def get_critical_findings(self) -> List[Dict[str, Any]]:
        """Extract critical/high-priority findings"""
        critical_types = [
            'EMAILADDR',
            'PHONE_NUMBER',
            'IP_ADDRESS',
            'NETBLOCK_OWNER',
            'AFFILIATE_INTERNET_NAME',
            'INTERNET_NAME',
            'WEBSERVER_TECHNOLOGY',
            'VULNERABILITY',
            'LEAKED_DATA',
            'DEFACED',
            'MALICIOUS_IPADDR',
            'MALICIOUS_INTERNET_NAME'
        ]

        critical = []
        for data_type in critical_types:
            if data_type in self.categorized_data:
                critical.extend([{
                    'type': data_type,
                    'data': item['data'],
                    'module': item['module'],
                    'confidence': item.get('confidence', 100)
                } for item in self.categorized_data[data_type][:5]])  # Limit to top 5 per type

        return critical

    def get_domain_intelligence(self) -> Dict[str, Any]:
        """Extract domain-related intelligence"""
        domains = set()
        subdomains = set()
        ip_addresses = set()

        for result in self.scan_results:
            data_type = result.get('type', '')
            data = result.get('data', '')

            if data_type == 'INTERNET_NAME':
                domains.add(data)
            elif data_type == 'AFFILIATE_INTERNET_NAME':
                subdomains.add(data)
            elif data_type == 'IP_ADDRESS':
                ip_addresses.add(data)

        return {
            'domains': sorted(list(domains)),
            'subdomains': sorted(list(subdomains)),
            'ip_addresses': sorted(list(ip_addresses)),
            'total_domains': len(domains),
            'total_subdomains': len(subdomains),
            'total_ips': len(ip_addresses)
        }

    def get_technology_stack(self) -> Dict[str, List[str]]:
        """Extract technology information"""
        technologies = defaultdict(set)

        tech_types = {
            'WEBSERVER_TECHNOLOGY': 'Web Servers',
            'WEBSERVER_BANNER': 'Server Banners',
            'SOFTWARE_USED': 'Software',
            'OPERATING_SYSTEM': 'Operating Systems'
        }

        for tech_type, label in tech_types.items():
            if tech_type in self.categorized_data:
                for item in self.categorized_data[tech_type]:
                    technologies[label].add(item['data'])

        return {key: sorted(list(val)) for key, val in technologies.items()}

    def get_network_intelligence(self) -> Dict[str, Any]:
        """Extract network-related intelligence"""
        network_data = {
            'ip_addresses': [],
            'netblocks': [],
            'asn_info': [],
            'bgp_info': []
        }

        type_mapping = {
            'IP_ADDRESS': 'ip_addresses',
            'NETBLOCK_OWNER': 'netblocks',
            'BGP_AS_OWNER': 'asn_info',
            'BGP_AS_MEMBER': 'bgp_info'
        }

        for data_type, key in type_mapping.items():
            if data_type in self.categorized_data:
                network_data[key] = [item['data'] for item in self.categorized_data[data_type]]

        return network_data

    def get_contact_information(self) -> Dict[str, List[str]]:
        """Extract contact information"""
        contacts = {
            'emails': [],
            'phone_numbers': [],
            'physical_addresses': [],
            'social_profiles': []
        }

        type_mapping = {
            'EMAILADDR': 'emails',
            'PHONE_NUMBER': 'phone_numbers',
            'PHYSICAL_ADDRESS': 'physical_addresses',
            'SOCIAL_MEDIA': 'social_profiles'
        }

        for data_type, key in type_mapping.items():
            if data_type in self.categorized_data:
                contacts[key] = list(set(item['data'] for item in self.categorized_data[data_type]))

        return contacts

    def get_security_findings(self) -> Dict[str, List[Dict[str, Any]]]:
        """Extract security-related findings"""
        security_data = {
            'vulnerabilities': [],
            'malicious_indicators': [],
            'leaked_data': [],
            'ssl_issues': []
        }

        security_types = {
            'VULNERABILITY': 'vulnerabilities',
            'MALICIOUS_IPADDR': 'malicious_indicators',
            'MALICIOUS_INTERNET_NAME': 'malicious_indicators',
            'LEAKED_DATA': 'leaked_data',
            'SSL_CERTIFICATE_MISMATCH': 'ssl_issues',
            'SSL_CERTIFICATE_EXPIRED': 'ssl_issues'
        }

        for data_type, category in security_types.items():
            if data_type in self.categorized_data:
                for item in self.categorized_data[data_type]:
                    security_data[category].append({
                        'type': data_type,
                        'data': item['data'],
                        'module': item['module'],
                        'source': item.get('source', '')
                    })

        return security_data

    def get_timeline_data(self) -> List[Dict[str, Any]]:
        """Create timeline of discoveries"""
        timeline = []

        for result in self.scan_results:
            if result.get('timestamp'):
                timeline.append({
                    'timestamp': result['timestamp'],
                    'type': result.get('type', 'Unknown'),
                    'data': result.get('data', '')[:100],  # Truncate long data
                    'module': result.get('module', '')
                })

        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])

        return timeline

    def get_module_efficiency(self) -> List[Dict[str, Any]]:
        """Calculate module efficiency metrics"""
        module_findings = defaultdict(int)

        for result in self.scan_results:
            module = result.get('module', 'Unknown')
            module_findings[module] += 1

        efficiency = [
            {'module': module, 'findings': count}
            for module, count in module_findings.items()
        ]

        efficiency.sort(key=lambda x: x['findings'], reverse=True)

        return efficiency

    def generate_full_analysis(self) -> Dict[str, Any]:
        """Generate complete analysis package"""
        return {
            'executive_summary': self.get_executive_summary(),
            'critical_findings': self.get_critical_findings(),
            'domain_intelligence': self.get_domain_intelligence(),
            'technology_stack': self.get_technology_stack(),
            'network_intelligence': self.get_network_intelligence(),
            'contact_information': self.get_contact_information(),
            'security_findings': self.get_security_findings(),
            'timeline': self.get_timeline_data(),
            'module_efficiency': self.get_module_efficiency(),
            'categorized_data': self.categorized_data
        }
