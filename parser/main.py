from datetime import datetime
import threading
import time

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError

from parser.exceptions import AccessDeniedException
from parser.proxy_auth import proxy_auth
from parser.tasks.bs4_tasks import parse_product_data
from parser.tasks.db_scripts import init_db, save_to_sqlite_db, check_sqlite_db
from parser.tasks.other_tasks import get_proxies
from parser.tasks.selenium_tasks import \
    select_section_from_dropdown_menu, scrape_product_links, \
    scroll_to_pagination, close_modal_windows
from parser.settings import TARGET_URL, DB_PATH


def get_chromedriver(
    use_proxy=False, required_proxy_auth=False, proxy_index=None, user_agent=None
):
    chrome_options = webdriver.ChromeOptions()

    # Set custom user agent if provided
    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    # Handle proxy settings
    if use_proxy:
        path_to_proxies = "/parser/tasks/test_proxies.py"
        proxies = get_proxies(source=path_to_proxies)

        # Use proxy without authentication
        if not required_proxy_auth:
            try:
                # Ensure proxy_index is within the range
                if proxy_index is None or proxy_index>= len(proxies):
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

def preparations_in_browser(driver):
    close_modal_windows(driver)
    time.sleep(1)
    select_section_from_dropdown_menu(driver)
    print(f"The page {driver.current_url} is ready for parsing!")


def fetch_product(driver,url):

    driver.get(url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-secondary-section")))

    # Obtaining page's HTML
    page_source = driver.page_source

    # Extracting products data
    product = parse_product_data(page_source=page_source)

    print(f"Parsed product: {product}")
    return product


def fetch_all_products(product_urls, use_proxy=False,proxy_index=None, proxy_lock=None):
    products_data = []
    products_data_lock = threading.Lock()
    threads = []

    def worker(
            product_urls,
            products_data,
            products_data_lock,
            proxy_index,
            proxy_lock,
            max_retries=10
    ):
        attempts = 0
        driver = None

        while attempts < max_retries:
            try:
                if not use_proxy:
                    driver = get_chromedriver(user_agent=True)
                else:
                    with proxy_lock:
                        # Each thread fetches the current proxy index and increments it
                        current_proxy_index = proxy_index[0]
                        proxy_index[0] += 1  # Move to next proxy for subsequent threads

                    # Initialize the WebDriver with the current proxy
                    driver = get_chromedriver(
                        use_proxy=use_proxy,
                        required_proxy_auth=False,
                        proxy_index=current_proxy_index,
                        user_agent=True)

                attempts = 0
                # Process product URLs from the queue
                while not product_urls.empty():
                    url = product_urls.get()
                    if url is None:
                        print("No more product URLs in the queue")
                        break
                    try:
                        data = fetch_product(driver=driver, url=url)
                        with products_data_lock:
                            products_data.append(data)
                            print(f"Added product: {data}")
                    except Exception as e:
                        print(type(e))
                        print(f"Error processing {url}: {e}. Retrying with another proxy.")
                        product_urls.put(url)  # Re-add URL to the queue for retry
                    finally:
                        product_urls.task_done()
                # Exit loop on successful processing
                break

            except WebDriverException:
                attempts += 1
                if use_proxy:
                    print(f"Proxy at index {current_proxy_index} failed. Retrying... ({attempts}/{max_retries})")
                else:
                    print(f"Failed to connect. Retrying... ({attempts}/{max_retries})")
                if driver:
                    driver.quit()

                if attempts == max_retries:
                    if use_proxy:
                        print("Maximum retry attempts reached with different proxies.")
                        raise ConnectionError("Unable to establish connection with any proxy.")
                    else:
                        print("Maximum retry attempts reached.")
                        raise ConnectionError("Unable to establish connection.")

            finally:
                if driver:
                    driver.quit()

    # Start threads with shared proxy index and lock
    for _ in range(5):
        thread = threading.Thread(
            target=worker,
            args=(product_urls, products_data, products_data_lock, proxy_index, proxy_lock)
        )
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    product_urls.join()
    for thread in threads:
        thread.join()

    return products_data


def main():
    max_retries = 10
    attempts = 0
    proxy_index = [0]  # Shared mutable proxy index
    proxy_lock = threading.Lock()  # Lock to synchronize access to the proxy index
    driver = None
    use_proxy = False

    #Initializing the database
    init_db(db=DB_PATH)

    #Starting the main loop
    while attempts < max_retries:
        try:
            if not use_proxy:
                driver = get_chromedriver(user_agent=True)
            else:
                with proxy_lock:
                    # Each thread fetches the current proxy index and increments it
                    current_proxy_index = proxy_index[0]
                    print(f"Current proxy index: {current_proxy_index}")
                    # Move to next proxy for subsequent threads
                    proxy_index[0] += 1

                driver = get_chromedriver(
                    use_proxy=use_proxy,
                    required_proxy_auth=False,
                    proxy_index=current_proxy_index,
                    user_agent=True)


            # Записываем время начала выполнения скрипта
            start_time = datetime.now()

            # Переход на целевой URL
            driver.get(TARGET_URL)
            if driver.title == "Access Denied":
                raise AccessDeniedException("Access denied. Try again later")

            #Resetting attempts counter
            attempts = 0

            # Подготовительные действия
            preparations_in_browser(driver)

            print(f"Navigated to: {driver.current_url}")
            next_page = scroll_to_pagination(driver)

            # Extracting products URLs from current page
            product_urls = scrape_product_links(driver)

            #Concurrent parsing of the products data in multiple threads
            if not use_proxy:
                products = fetch_all_products(product_urls=product_urls)
            else:
                products = fetch_all_products(
                    product_urls=product_urls,
                    use_proxy=use_proxy,
                    proxy_index=proxy_index,
                    proxy_lock=proxy_lock)

            # Saving in the db
            save_to_sqlite_db(db=DB_PATH, data=products)
            # Directing to the next page
            next_page.click()
            time.sleep(5)
            print(f"Navigated to {driver.current_url}")

            # Script runtime
            end_time = datetime.now()
            elapsed_time = end_time - start_time
            print(f"Script execution time: {elapsed_time}")

            # Проверка всех записей в таблице "products"
            check_sqlite_db(db=DB_PATH)
            break


        except (WebDriverException, AccessDeniedException) as e:
            attempts += 1
            print(f"{type(e)}: {e}")
            print(f"Couldn't establish internet connection. Retrying... ({attempts}/{max_retries} attempt).")
            if attempts == max_retries:
                raise MaxRetryError("Reached maximum number of attempts to connect to the server.")
            time.sleep(5)

        finally:
            driver.quit()


if __name__ == '__main__':
    main()