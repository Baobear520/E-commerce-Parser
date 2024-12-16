import asyncio
from selenium.common import WebDriverException

from other_scripts.test_proxies import read_proxies
from other_scripts.db_scripts import init_db, save_to_db_in_bulk, check_sqlite_db
from other_scripts.utils import runtime_counter, scheduler
from parser.settings import TARGET_URL, DB_PATH, PATH_TO_VALID_PROXIES
from parser.tasks.async_tasks.async_scraping import product_scraper, async_scraper
from parser.tasks.async_tasks.other_async_tasks import mock_products_scraper
from parser.tasks.sync_tasks.selenium_tasks import \
    select_section_from_dropdown_menu, scrape_product_links, \
    connect_to_base_url, locate_pagination

"""Main script for scraping products data and saving it to the SQLite database."""

@runtime_counter
def main(use_proxy, require_proxy_auth):

    # Initializing the database
    init_db(db=DB_PATH)
    products_data = {}

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
        while len(products_data) < 250:
            locate_pagination(driver,require_action=False)
            try:
                product_urls = scrape_product_links(driver)
                products_batch = asyncio.run(
                        async_scraper(
                            input_container=product_urls,
                            use_proxy=use_proxy,
                            require_proxy_auth=require_proxy_auth,
                            proxies=proxies
                        )
                )
                if products_batch is not None:
                    products_data.update(products_batch)
                    # Optionally save the batch to a database
                    save_to_db_in_bulk(db=DB_PATH, data=products_batch)
                print(f"Total products scraped: {len(products_data)}")
            except Exception as e:
                print(f"Scraping error: {e}")

            finally:
                try:
                    locate_pagination(driver, require_action=True)

                except WebDriverException:
                    print("Cannot find 'Next' button. Exiting loop.")
                    break

    finally:
        print("Finished script execution.")
        print(f"We have {len(products_data)} dummy products in the database.")
        if driver:
            driver.quit()


if __name__ == '__main__':
    try:
        scheduler(main, interval=600, use_proxy=False, require_proxy_auth=False)
        check_sqlite_db(db=DB_PATH, table_name="products")
    except KeyboardInterrupt:
        print("Script execution interrupted by the user.")

