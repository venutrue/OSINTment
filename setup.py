"""Setup configuration for OSINTment"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='osintment',
    version='1.0.0',
    description='Professional OSINT Automation and Reporting Tool with SpiderFoot Integration',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='OSINTment Team',
    author_email='',
    url='https://github.com/venutrue/OSINTment',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
        'aiohttp>=3.9.0',
        'jinja2>=3.1.2',
        'weasyprint>=60.0',
        'markdown>=3.5',
        'plotly>=5.18.0',
        'pandas>=2.1.0',
        'reportlab>=4.0.0',
        'pypdf>=3.17.0',
        'matplotlib>=3.8.0',
        'seaborn>=0.13.0',
        'click>=8.1.7',
        'colorama>=0.4.6',
        'rich>=13.7.0',
        'flask>=3.0.0',
        'flask-cors>=4.0.0',
        'pyyaml>=6.0.1',
        'python-dateutil>=2.8.2',
    ],
    entry_points={
        'console_scripts': [
            'osintment=osintment.cli:main',
            'osintment-web=osintment.web_server:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Topic :: Security',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    keywords='osint intelligence spiderfoot security reconnaissance reporting',
    project_urls={
        'Bug Reports': 'https://github.com/venutrue/OSINTment/issues',
        'Source': 'https://github.com/venutrue/OSINTment',
    },
)
