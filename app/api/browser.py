"""
Browser test API endpoint for diagnostics.
"""

from flask import Blueprint, jsonify
import sys
import os

# Add parent utils to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

browser_bp = Blueprint('browser', __name__, url_prefix='/api/browser')


@browser_bp.route('/test', methods=['GET'])
def test_browser():
    """
    Test browser functionality and return diagnostics.
    
    GET /api/browser/test
    
    Returns:
        JSON with browser test results and diagnostics
    """
    try:
        from utils.browser import test_browser
        result = test_browser()
        status_code = 200 if result.get('success') else 500
        return jsonify(result), status_code
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to import or run browser test'
        }), 500


@browser_bp.route('/status', methods=['GET'])
def browser_status():
    """
    Check if browser dependencies are available.
    
    GET /api/browser/status
    
    Returns:
        JSON with status of browser components
    """
    import subprocess
    
    status = {
        'chrome_installed': False,
        'chromedriver_installed': False,
        'selenium_installed': False,
        'chrome_version': None,
        'chromedriver_version': None,
        'chrome_bin_env': os.environ.get('CHROME_BIN', 'not set'),
        'chromedriver_path_env': os.environ.get('CHROMEDRIVER_PATH', 'not set')
    }
    
    # Check if Chrome is installed
    try:
        result = subprocess.run(
            ['google-chrome', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            status['chrome_installed'] = True
            status['chrome_version'] = result.stdout.strip()
    except Exception as e:
        status['chrome_error'] = str(e)
    
    # Check if ChromeDriver is installed
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
    try:
        result = subprocess.run(
            [chromedriver_path, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            status['chromedriver_installed'] = True
            status['chromedriver_version'] = result.stdout.strip()
    except Exception as e:
        status['chromedriver_error'] = str(e)
    
    # Check if Selenium is installed
    try:
        import selenium
        status['selenium_installed'] = True
        status['selenium_version'] = selenium.__version__
    except ImportError:
        status['selenium_installed'] = False
    
    return jsonify(status), 200
