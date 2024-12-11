import asyncio
from datetime import datetime

from selenium import webdriver
from selenium.common import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from other_scripts.selenium_proxy_auth import proxy_auth
from other_scripts.test_proxies import parse_proxy
from parser.settings import USER_AGENT


def setup_chrome_options(
    user_agent, use_proxy, require_proxy_auth, proxy
):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run in headless mode for efficiency
    chrome_options.add_argument('--disable-gpu')  # Disable GPU to reduce resource usage
    chrome_options.add_argument("--no-sandbox")

    # Set custom user agent if provided
    if user_agent:
        chrome_options.add_argument(f'--user-agent={USER_AGENT}')

    # Use proxy without authentication
    if use_proxy:
        if not require_proxy_auth:
            # Set both HTTP and HTTPS schemes to the same proxy address
            chrome_options.add_argument(f'--proxy-server=http={proxy};https={proxy}')

        # Use proxy with authentication
        else:
            try:
                host, port, user, password = asyncio.run(parse_proxy(proxy))
                plugin_file = proxy_auth(host, port, user, password)
                chrome_options.add_extension(plugin_file)

            except Exception as e:
               print(f"{type(e).__name__} occurred while trying to authenticate proxy in browser")
            except KeyError:
                print("Missing proxy authentication details. Check proxy configuration.")
    return chrome_options


def initialize_chrome_driver(chrome_options, timeout=60):
    try:
        print("Trying to initialize Chrome...")
        # Initialize the Chrome WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        # Set timeouts for page load and script execution
        driver.set_page_load_timeout(timeout)
        driver.set_script_timeout(timeout)

        # Wait for the browser to be fully initialized by ensuring the document is loaded
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "html"))
        )

        print("Chrome driver initialized successfully.")
        return driver

    except TimeoutException as e:
        error_message = f"TimeoutException: Chrome driver took too long to initialize (over {timeout} seconds)."
        print(error_message)
        raise TimeoutException(error_message) from e

    except WebDriverException as e:
        error_message = f"WebDriverException occurred while initializing Chrome driver: {e}"
        print(error_message)
        raise WebDriverException(error_message) from e

    except Exception as e:
        error_message = f"Unexpected {type(e).__name__} occurred: {e}"
        print(error_message)
        raise e


def get_chrome_driver(user_agent, use_proxy, require_proxy_auth, proxy):
    chrome_options = setup_chrome_options(
        user_agent=user_agent,
        use_proxy=use_proxy,
        require_proxy_auth=require_proxy_auth,
        proxy=proxy
    )
    return initialize_chrome_driver(
        chrome_options=chrome_options
    )