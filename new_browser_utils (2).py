import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
import time


def create_driver(headless=False):
    """Create a robust undetected Chrome WebDriver."""
    chrome_options = Options()
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1200,800")

    # Create undetected Chrome driver
    driver = uc.Chrome(options=chrome_options)

    # Extra anti-detection tweaks
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
        """
    })

    time.sleep(1)  # brief pause to stabilize
    return driver
