import asyncio
import random
import threading
import time

from queue import Queue

from selenium.common import WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from other_scripts.exceptions import MaxRetriesExceeded
from other_scripts.test_proxies import read_proxies
from other_scripts.db_scripts import init_db, save_to_sqlite_db, check_sqlite_db
from other_scripts.utils import runtime_counter, scheduler, put_in_queue
from parser.settings import TARGET_URL, DB_PATH, PATH_TO_VALID_PROXIES, USER_AGENT, MAX_RETRIES
from parser.tasks.sync_tasks.bs4_tasks import scrape_product_data
from parser.tasks.sync_tasks.chrome_driver_setup import get_chrome_driver
from parser.tasks.sync_tasks.selenium_tasks import \
    select_section_from_dropdown_menu, scrape_product_links, \
    connect_to_base_url, locate_pagination


"""Main script for scraping products data and saving it to the SQLite database.
Threads are used to parallelize the scraping process."""


def worker_task(queue, all_products, products_batch, use_proxy, require_proxy_auth, proxies):
    """Worker function to scrape data using a separate WebDriver instance."""
    driver = None
    try:
        driver = get_chrome_driver(
            user_agent=USER_AGENT,
            use_proxy=use_proxy,
            require_proxy_auth=require_proxy_auth,
            proxy=random.choice(proxies) if proxies else None,
        )
        driver.set_page_load_timeout(20)

        while not queue.empty():
            url = queue.get()
            attempts = 1
            while attempts <= MAX_RETRIES:
                try:
                    print(f"[{threading.current_thread().name}] Processing URL: {url}")

                    # Navigate to the product URL
                    driver.get(url)
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".product-secondary-section.pdp-standard"))
                    )
                    print(f"[{threading.current_thread().name}] Navigated to {driver.current_url}")
                    html = driver.page_source
                    print(f"[{threading.current_thread().name}] Page source retrieved")

                    # Scrape product data
                    print(f"[{threading.current_thread().name}] Scraping {driver.current_url.removeprefix('https://www.saksoff5th.com/product')}...")
                    result = scrape_product_data(html)
                    print(f"[{threading.current_thread().name}] Product data scraped: {result}")

                    if result:
                        with threading.Lock():
                            products_batch.append(result)
                            all_products.append(result)
                            queue.task_done()
                            print(f"[{threading.current_thread().name}] Task done")  # Mark the task as done
                            break

                except (WebDriverException, Exception) as e:
                    if isinstance(e, WebDriverException):
                        print(f"[{threading.current_thread().name}] WebDriverException occurred for {url}. Retrying {attempts}/{MAX_RETRIES}...")
                    else:
                        print(f"[{threading.current_thread().name}] Error processing {url}: {e.args}.\nRetrying {attempts}/{MAX_RETRIES}...")
                    attempts += 1
                    if attempts > MAX_RETRIES:
                        print(f"[{threading.current_thread().name}] Max retries exceeded for {url}. Skipping...")
                        queue.task_done()
                        print(f"[{threading.current_thread().name}] Task done")  # Mark the task as done
                        break

    finally:
        if driver:
            driver.quit()


@runtime_counter
def main(use_proxy, require_proxy_auth):

    # Initializing the database
    init_db(db=DB_PATH)
    all_products = []
    # Proxy initialization
    proxies = None
    if use_proxy:
        try:
            proxies = asyncio.run(
                read_proxies(source=PATH_TO_VALID_PROXIES)
            )

            if not proxies:
                print("No proxies loaded. Switching to no-proxy mode.")
                use_proxy, require_proxy_auth = False, False
            else:
                print(f"Proxies loaded: {len(proxies)}")
        except Exception as e:
            print(f"Proxy error: {e}. Switching to no-proxy mode.")
            use_proxy, require_proxy_auth = False, False

    # WebDriver setup
    driver = None
    try:
        driver = connect_to_base_url(TARGET_URL, use_proxy, require_proxy_auth, proxies)
        print(f"Object 'Driver' initialized in 'main': {driver}")
        print(f"Navigated to {driver.current_url}")
        select_section_from_dropdown_menu(driver)

        # Scraping loop
        while len(all_products) < 1000:
            products_batch = []
            try:
                locate_pagination(driver,require_action=False)
                product_urls = scrape_product_links(driver)
                urls = put_in_queue(data=product_urls)
                try:
                    locate_pagination(driver, require_action=True)
                    print(f"Main browser window navigated to {driver.current_url}")
                except WebDriverException:
                    print("Cannot find 'Next' button. Exiting loop.")
                    break
                try:
                    # Use ThreadPoolExecutor for parallel scraping
                    max_workers = 10
                    with ThreadPoolExecutor(max_workers=max_workers) as executor:
                        # Submit worker tasks to the executor
                        futures = [executor.submit(worker_task, urls, all_products, products_batch, use_proxy, require_proxy_auth, proxies)
                                   for _ in range(min(max_workers, urls.qsize()))] #initialize as many workers as needed

                        # Wait for all tasks to complete
                        for future in as_completed(futures):
                            future.result()

                    urls.join()
                    print("Queue is empty")
                    save_to_sqlite_db(db=DB_PATH, data=products_batch)
                except Exception as e:
                    print(f"{type(e).__name__} occurred: {e}")

            except Exception as e:
                print(f"{type(e).__name__} while scraping product urls: {e}")
    finally:
        if driver:
            driver.quit()
        print("Finished script execution.")
        print(f"We have {len(all_products)} products in the database.")


if __name__ == '__main__':
    try:
        print("Starting the script...")
        scheduler(main, interval=60, use_proxy=False, require_proxy_auth=False)
    except KeyboardInterrupt:
        print("Script execution interrupted by user. Exiting...")
    finally:
        check_sqlite_db(db=DB_PATH)
