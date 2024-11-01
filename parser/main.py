from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from datetime import datetime
import time
import threading

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError, ProtocolError

from parser.exceptions import AccessDeniedException
from parser.proxy_auth import proxy_auth
from parser.tasks.bs4_tasks import parse_product_data
from parser.tasks.db_scripts import init_db, save_to_sqlite_db, check_sqlite_db
from parser.tasks.other_tasks import get_proxies
from parser.tasks.selenium_tasks import \
    select_section_from_dropdown_menu, scrape_product_links, \
    scroll_to_pagination, close_modal_windows
from parser.settings import TARGET_URL, DB_PATH


# Initialize the ThreadPoolExecutor for concurrent processing
executor = ThreadPoolExecutor(max_workers=5)  # Use a pool of 5 threads

# Replace the lock with a thread-safe queue
products_data_queue = Queue()  # Collect products data concurrently

def get_chromedriver(
    use_proxy=False, required_proxy_auth=False, proxy_index=None, user_agent=None
):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run in headless mode for efficiency
    chrome_options.add_argument('--disable-gpu')  # Disable GPU to reduce resource usage

    # Set custom user agent if provided
    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    # Handle proxy settings
    if use_proxy:
        path_to_proxies = "/Users/aldmikon/Desktop/Python_road/Projects/E-commerce_Parser/data/valid_proxies.txt"
        proxies = get_proxies(source=path_to_proxies)

        # Use proxy without authentication
        if not required_proxy_auth:
            try:
                # Ensure proxy_index is within the range
                if proxy_index is None or proxy_index >= len(proxies):
                    proxy_index = 0  # Reset to default if out of range
                # Get proxy address from list
                proxy_address = proxies[proxy_index]

                # Set both HTTP and HTTPS schemes to the same proxy address
                chrome_options.add_argument(f'--proxy-server=http={proxy_address};https={proxy_address}')
            except IndexError:
                print("Proxy index is out of range. Verify the proxy list and index.")

        # Use proxy with authentication
        else:
            try:
                # Define authentication settings for proxy
                proxy_info = proxies[proxy_index]
                plugin_file = proxy_auth(
                    host=proxy_info["host"],
                    port=proxy_info["port"],
                    user=proxy_info["user"],
                    password=proxy_info["pass"]
                )
                chrome_options.add_extension(plugin_file)
            except KeyError:
                print("Missing proxy authentication details. Check proxy configuration.")

    # Attempt to initialize the Chrome driver
    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Initialized Chrome driver.")
        return driver
    except Exception as e:
        print(f"Error occurred while initializing Chrome driver: {e}")


def fetch_product(driver, url):
    driver.get(url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-secondary-section")))

    # Obtaining page's HTML
    page_source = driver.page_source

    # Extracting products data
    product = parse_product_data(page_source=page_source)
    print(f"Parsed product: {product}")
    return product


def fetch_all_products(product_urls, driver, use_proxy=False, proxy_index=None, proxy_lock=None):
    # Reuse driver in each thread
    def worker(url, driver, max_retries=5):
        attempts = 0
        while attempts < max_retries:
            try:
                product = fetch_product(driver, url)
                with products_data_lock:
                    products_data.append(product)
                    print(f"Added {product}")
                break  # Success
            except WebDriverException:
                attempts += 1
                print(f"Retrying {url}... ({attempts}/{max_retries})")
                # If fails too many times, refresh driver and retry
                if attempts == max_retries:
                    raise ConnectionError("Max retries exceeded")

    # Multithreaded execution with driver reuse
    products_data = []
    products_data_lock = threading.Lock()
    threads = []
    with ThreadPoolExecutor() as executor:
        while not product.
            executor.map(worker, url)

    # Wait for all threads to complete
    for thread in threads:
        thread.result()  # This will also catch any raised exceptions

    return products_data


def main():
    max_retries = 10
    attempts = 0
    proxy_index = [0]  # Shared mutable proxy index
    proxy_lock = threading.Lock()  # Lock to synchronize access to the proxy index
    use_proxy = False

    # Initializing the database
    init_db(db=DB_PATH)

    if not use_proxy:
        driver = get_chromedriver(user_agent=True)
    else:
        with proxy_lock:
            current_proxy_index = proxy_index[0]
            print(f"Current proxy index: {current_proxy_index}")
            proxy_index[0] += 1

        driver = get_chromedriver(
            use_proxy=use_proxy,
            required_proxy_auth=False,
            proxy_index=current_proxy_index,
            user_agent=True)

    # Start up time
    start_time = datetime.now()

    # Start the main loop
    while attempts < max_retries:
        try:
            # Navigate to the target page
            driver.get(TARGET_URL)
            if driver.title == "Access Denied":
                raise AccessDeniedException("Access denied. Try again later")

            # Perform initial setup
            select_section_from_dropdown_menu(driver)

            # Scroll to pagination and scrape product links
            next_page = scroll_to_pagination(driver)

            product_urls = scrape_product_links(driver)

            # Process product URLs concurrently
            products = fetch_all_products(
                product_urls=product_urls,
                driver=driver,  # Reuse the driver instance here
                use_proxy=use_proxy,
                proxy_index=proxy_index,
                proxy_lock=proxy_lock
            )

            # Save to database
            save_to_sqlite_db(db=DB_PATH, data=products)

            # Move to the next page and wait briefly
            next_page.click()
            time.sleep(5)

            # Successfully completed; break out of retry loop
            break

        except (WebDriverException, AccessDeniedException) as e:
            attempts += 1
            print(f"Attempt {attempts}/{max_retries} failed.\n{e} ")
            # Only re-initialize driver on critical failures
            driver.quit()
            if not use_proxy:
                driver = get_chromedriver(user_agent=True)
            else:
                with proxy_lock:
                    current_proxy_index = proxy_index[0]
                    print(f"Current proxy index: {current_proxy_index}")
                    proxy_index[0] += 1

                driver = get_chromedriver(
                    use_proxy=use_proxy,
                    required_proxy_auth=False,
                    proxy_index=current_proxy_index,
                    user_agent=True)

        finally:
            if driver:
                driver.quit()

    end_time = datetime.now()
    print(f"Runtime: {end_time - start_time} ")
    check_sqlite_db(db=DB_PATH, table_name="products")

if __name__ == '__main__':
    main()
