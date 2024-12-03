import asyncio
import time

from selenium.common import ElementNotInteractableException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from other_scripts.test_proxies import read_proxies, check_proxies
from other_scripts.db_scripts import init_db, save_to_sqlite_db, check_sqlite_db
from other_scripts.utils import runtime_counter
from parser.settings import TARGET_URL, DB_PATH, PATH_TO_VALID_PROXIES
from parser.tasks.async_tasks.async_scraping import product_scraper
from parser.tasks.sync_tasks.selenium_tasks import \
    select_section_from_dropdown_menu, scrape_product_links, \
    scroll_to_pagination, connect_to_base_url


"""Main script for scraping products data and saving it to the SQLite database."""

@runtime_counter
def main(use_proxy, require_proxy_auth):

    # Initializing the database
    # init_db(db=DB_PATH)

    if use_proxy:
        proxies = asyncio.run(read_proxies(source=PATH_TO_VALID_PROXIES))
        # Ensure proxies is a list and has entries
        if not proxies:
            print("No proxies available. Switching to no-proxy mode.")
            use_proxy = False
            require_proxy_auth = False
    proxies = None

    driver = connect_to_base_url(TARGET_URL,use_proxy,require_proxy_auth, proxies)
    # Perform initial setup on the page and switch to the desired section
    select_section_from_dropdown_menu(driver)

    # Main loop
    products_data = []

    try:
        while len(products_data) < 1000:
            try:
                # Scroll to pagination and scrape product links
                scroll_to_pagination(driver)
                # Scrape product links on the current page
                product_urls = scrape_product_links(driver)

                # Fetch products data from asynchronous loop and append to shared list
                # products_batch = product_scraper(
                #     input_container=product_urls, use_proxy=use_proxy, require_proxy_auth=require_proxy_auth
                # )
                products_data.extend(product_urls)

                print(f"Added {len(product_urls)} dummy products")
                print(f"Total: {len(products_data)} dummy products")

                # Optionally save the batch to a database
                # save_to_sqlite_db(db=DB_PATH, data=products_batch)

            except Exception as e:
                print(f"{type(e).__name__}, {e}")
                break

            finally:
                # Click the 'Next' button even if the scraping of the current page failed
                try:
                    # Locate the 'Next' button
                    next_page = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
                    if next_page.is_displayed() and next_page.is_enabled():
                        print("'Next' is now in view and clickable.")
                        next_page.click()
                        print("Clicked 'Next'. Waiting for the next page to load...")
                        # Log the current URL for debugging
                        print(f"Current URL: {driver.current_url}")
                    else:
                        raise WebDriverException("Couldn't click 'Next'")


                except WebDriverException as e:
                    print(f"{type(e).__name__} while trying to click 'Next'.\n{e}")
                    break  # Exit the loop if the 'Next' button can't be clicked
                except Exception as e:
                    print(f"Something happened: {e}")
                    break  # Exit the loop if the 'Next' button can't be clicked

    finally:
        # Quit the driver once scraping is done
        driver.quit()

        # Print final results
        print(f"We have {len(products_data)} dummy products in the database.")


if __name__ == '__main__':
    use_proxy = False
    require_proxy_auth = False

    #asyncio.run(check_proxies(has_proxy_auth=require_proxy_auth))
    main(use_proxy=use_proxy,require_proxy_auth=require_proxy_auth)
    #check_sqlite_db(db=DB_PATH, table_name="products")
