"""
Browser automation utilities using Selenium with Chrome.
Configured for headless operation in server environments like Render.
"""

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from typing import Optional


def create_chrome_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver instance configured for server environments.
    
    Args:
        headless: Run Chrome in headless mode (default: True for servers)
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    
    Example:
        >>> driver = create_chrome_driver()
        >>> driver.get('https://example.com')
        >>> title = driver.title
        >>> driver.quit()
    """
    chrome_options = Options()
    
    # Headless mode (required for servers without displays)
    if headless:
        chrome_options.add_argument('--headless=new')
    
    # Essential arguments for server environments
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    
    # Performance optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    
    # Window size (important for headless rendering)
    chrome_options.add_argument('--window-size=1920,1080')
    
    # User agent
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
    
    # Get Chrome binary path from environment or use default
    chrome_bin = os.environ.get('CHROME_BIN')
    if chrome_bin:
        chrome_options.binary_location = chrome_bin
    
    # Get ChromeDriver path from environment or use default
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
    
    # Create service
    service = Service(executable_path=chromedriver_path)
    
    # Create and return driver
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Set timeouts
    driver.set_page_load_timeout(30)
    driver.implicitly_wait(10)
    
    return driver


def test_browser() -> dict:
    """
    Test browser functionality and return diagnostics.
    
    Returns:
        dict: Diagnostics information including Chrome version and test results
    """
    try:
        driver = create_chrome_driver(headless=True)
        driver.get('https://www.google.com')
        title = driver.title
        driver.quit()
        
        return {
            'success': True,
            'title': title,
            'chrome_bin': os.environ.get('CHROME_BIN', 'default'),
            'chromedriver_path': os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver'),
            'message': 'Browser test successful'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'chrome_bin': os.environ.get('CHROME_BIN', 'not set'),
            'chromedriver_path': os.environ.get('CHROMEDRIVER_PATH', 'not set'),
            'message': 'Browser test failed'
        }


if __name__ == '__main__':
    # Run diagnostics when executed directly
    result = test_browser()
    print('Browser Test Results:')
    for key, value in result.items():
        print(f'  {key}: {value}')
