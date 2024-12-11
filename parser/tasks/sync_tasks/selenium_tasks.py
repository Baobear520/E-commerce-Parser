import random
import time
from urllib3.exceptions import NewConnectionError
from selenium.common import TimeoutException, ElementClickInterceptedException, WebDriverException, \
    NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from other_scripts.exceptions import AccessDeniedException, MaxRetriesExceeded
from other_scripts.utils import runtime_counter
from parser.settings import MAX_RETRIES, USER_AGENT, DELAY
from parser.tasks.sync_tasks.bs4_tasks import scrape_product_data
from parser.tasks.sync_tasks.chrome_driver_setup import get_chrome_driver


def connect_to_base_url(base_url, use_proxy, require_proxy_auth, proxies, max_retries=MAX_RETRIES):
    attempts = 1
    while attempts <= max_retries:
        try:
            if use_proxy:
                proxy = random.choice(proxies)
                print(f"Selected proxy: {proxy}")
            else:
                proxy = None

            driver = get_chrome_driver(
                user_agent=USER_AGENT,
                use_proxy=use_proxy,
                require_proxy_auth=require_proxy_auth,
                proxy=proxy

            )

            # Navigate to the target page
            driver.get(base_url)
            if driver.title == "Access Denied":
                raise AccessDeniedException("Access denied. Try again later")

            return driver


        except (AccessDeniedException, NewConnectionError, WebDriverException, Exception) as e:
            if isinstance(e, AccessDeniedException):
                if not use_proxy:
                    print("Access denied.")
                else:
                    print(f"Access denied with proxy {proxy}.")
            else:
                print(f"{type(e).__name__} while trying to obtain {base_url}. Retrying {attempts}/{max_retries}...")
                if not isinstance(e, Exception):
                    print(f"\n{e}")

            if 'driver' in locals():
                driver.quit()

        finally:
            if use_proxy:
                proxies = [p for p in proxies if p != proxy]
            time.sleep(DELAY)
            attempts += 1
    raise MaxRetriesExceeded(base_url)


# def close_modal_windows(driver):
#     # First modal window configuration
#     top_modal_selector = (By.CLASS_NAME, "bfx-wm-dialog")
#     top_close_button_selector = (By.ID, "bfx-wm-close-button")
#
#     # Second modal window configuration
#     bottom_modal_selector = (By.ID, "welcome-email-modal")
#     bottom_close_button_selector = (By.ID, "consent-close")
#
#     # Attempt to close the first modal
#     try:
#         top_modal = WebDriverWait(driver, 5).until(
#             EC.visibility_of_element_located(top_modal_selector)
#         )
#         if top_modal:
#             close_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable(top_close_button_selector)
#             )
#             close_button.click()
#             print("Top modal window closed.")
#     except TimeoutException:
#         print("Top modal window not found. Moving on...")
#     except Exception as e:
#         print(f"Unexpected error occurred while handling modals: {e}")
#
#
#     # Attempt to close the second modal
#     try:
#         bottom_modal = WebDriverWait(driver, 5).until(
#             EC.visibility_of_element_located(bottom_modal_selector)
#         )
#         if bottom_modal:
#             close_button = WebDriverWait(driver, 5).until(
#                 EC.element_to_be_clickable(bottom_close_button_selector)
#             )
#             close_button.click()
#             print("Bottom modal window closed.")
#             return True
#     except TimeoutException:
#         print("Bottom modal window not found. Moving on...")
#         return True
#
#     except Exception as e:
#         print(f"Unexpected error occurred while handling modals: {e}")
#         driver.quit()
#
#
# def select_section_from_dropdown_menu(driver):
#     while True:
#         try:
#             element = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.ID,"2534374302023689"))
#             )
#             element.click()
#             print(f"Navigated to {driver.current_url}")
#             break
#
#         except TimeoutException:
#             print("Could not find the dropdown menu. Retrying...")
#
#         except ElementClickInterceptedException as e:
#             print("Encountered modal windows.")
#             modals_passed = close_modal_windows(driver)
#             if not modals_passed:
#                 print("Could not close all modal windows. Exiting.")
#                 break  # Exit the loop if modals cannot be closed

def close_modal_windows(driver):
    modal_configs = [
        {"modal_selector": (By.CLASS_NAME, "bfx-wm-dialog"), "close_button_selector": (By.ID, "bfx-wm-close-button")},
        {"modal_selector": (By.ID, "welcome-email-modal"), "close_button_selector": (By.ID, "consent-close")},
    ]

    for config in modal_configs:
        try:
            modal = WebDriverWait(driver, 5).until(
                EC.visibility_of_element_located(config["modal_selector"])
            )
            if modal:
                close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(config["close_button_selector"])
                )
                close_button.click()
                print(f"Modal window {config['modal_selector']} closed.")
        except TimeoutException:
            print(f"Modal window {config['modal_selector']} not found. Moving on...")
        except Exception as e:
            print(f"Error occurred while handling modal {config['modal_selector']}: {e}")

    # Verify no residual modals
    try:
        WebDriverWait(driver, 2).until_not(
            EC.any_of(
                EC.visibility_of_element_located((By.CLASS_NAME, "bfx-wm-dialog")),
                EC.visibility_of_element_located((By.ID, "welcome-email-modal"))
            )
        )
        print("All modal windows dismissed.")
        return True
    except TimeoutException:
        print("Residual modal windows detected. Retrying...")
        return False


def select_section_from_dropdown_menu(driver, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "2534374302023689"))
            )
            element.click()
            print(f"Navigated to {driver.current_url}")
            return  # Exit once the dropdown is successfully clicked

        except TimeoutException:
            print("Could not find the dropdown menu. Retrying...")

        except ElementClickInterceptedException as e:
            print("Encountered modal windows.")
            if not close_modal_windows(driver):
                print("Could not close all modal windows. Retrying...")
                retries += 1
                continue

        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            break

    print("Max retries reached. Could not interact with the dropdown.")
    raise MaxRetriesExceeded(url=driver.current_url, message="Max retries exceeded. Could not interact with the dropdown.")

@runtime_counter
def locate_pagination(driver,require_action):
    """Scrolls to the bottom of the page, then scrolls up to the pagination element and clicks 'next' if required."""
    retry_attempts = 0
    max_retries = 3
    max_scroll_attempts = 15
    print("Started scrolling...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    scrolling_attempts = 1
    while scrolling_attempts <= max_scroll_attempts:
        try:
            next_page = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[aria-label='Next']"))
            )
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_page)
            print("Pagination in view.")
            if require_action:
                if next_page.is_displayed() and next_page.is_enabled():
                    print("'Next' is now in view and clickable.")
                    try:
                        next_page.click()
                        print("Clicked 'Next'.")
                        return next_page

                    except (ElementClickInterceptedException, Exception) as e:
                        if isinstance(e, ElementClickInterceptedException):
                            print(
                                f"Something is blocking the 'Next' button.\nPerforming modal windows check.")
                            close_modal_windows(driver)
                            retry_attempts += 1
                        else:
                            print(f"Error during scrolling: {e.args}. Retrying.{retry_attempts}//{max_retries}..")
                        time.sleep(DELAY)
                        retry_attempts += 1

                elif "disabled" in next_page.get_attribute("class"):
                    print("Pagination is disabled, last page reached.")
                    raise NoSuchElementException("Pagination is disabled, last page reached.")

                else:
                    print("'Next' is not clickable")
                    raise TimeoutException("Pagination button is not clickable.")

            return next_page

        except TimeoutException:
            # If pagination isn't found, scroll and retry
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Scrolled down. Retrying to find pagination {scrolling_attempts}//{max_scroll_attempts}...")
            scrolling_attempts += 1
            time.sleep(0.2)  # Short wait to allow page rendering

        except NoSuchElementException:
            print("There are no more pages to go to.")
            return None

        except (ElementClickInterceptedException, Exception) as e:
            if isinstance(e, ElementClickInterceptedException):
                print(f"Something is blocking the 'Next' button. Retrying.{retry_attempts}//{max_retries}..")
            else:
                print(f"Error during scrolling: {e.args}. Retrying.{retry_attempts}//{max_retries}..")
            time.sleep(DELAY)
            retry_attempts += 1
            if retry_attempts >= max_retries:
                print(f"Max retries reached. Could not find pagination element.")
                raise MaxRetriesExceeded(driver.current_url)

        except MaxRetriesExceeded as e:
            print(f"Max retries reached. Could not find pagination element.")
            raise e

    # If the loop ends without finding the pagination button, raise an error
    print("Failed to locate pagination after maximum retries.")
    raise MaxRetriesExceeded(driver.current_url)


def scrape_product_links(driver):
    """Извлекаем ссылки на продукты с текущей страницы."""

    # Extracting all the product links after the scrolldown is done
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    print(f"Got {len(product_elements)} items from the page {driver.current_url}")
    return list([link.get_attribute('href') for link in product_elements])


def get_product(driver, url):
    driver.get(url)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "product-secondary-section")))

    # Obtaining page's HTML
    page_source = driver.page_source

    # Extracting products data
    product = scrape_product_data(page_source=page_source)
    print(f"Got the product: {product}")
    return product




