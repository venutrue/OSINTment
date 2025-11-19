"""Configuration management for OSINTment"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # SpiderFoot settings
    SPIDERFOOT_URL = os.getenv('SPIDERFOOT_URL', 'http://localhost:5001')
    SPIDERFOOT_API_KEY = os.getenv('SPIDERFOOT_API_KEY', '')

    # Report settings
    REPORT_OUTPUT_DIR = Path(os.getenv('REPORT_OUTPUT_DIR', './reports'))
    REPORT_LOGO_PATH = os.getenv('REPORT_LOGO_PATH', './osintment/templates/assets/logo.png')
    COMPANY_NAME = os.getenv('COMPANY_NAME', 'Professional OSINT Services')
    REPORT_AUTHOR = os.getenv('REPORT_AUTHOR', 'OSINT Team')

    # Application settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Template directory
    TEMPLATE_DIR = Path(__file__).parent.parent / 'templates'

    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        cls.REPORT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (cls.TEMPLATE_DIR / 'html').mkdir(parents=True, exist_ok=True)
        (cls.TEMPLATE_DIR / 'assets').mkdir(parents=True, exist_ok=True)


# Initialize directories on import
Config.ensure_directories()
