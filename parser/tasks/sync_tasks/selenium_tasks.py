import random
import time

from selenium.common import TimeoutException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from other_scripts.exceptions import AccessDeniedException, MaxRetriesExceeded
from other_scripts.utils import runtime_counter
from parser.settings import MAX_RETRIES, USER_AGENT, DELAY
from parser.tasks.sync_tasks.chrome_driver_setup import get_chrome_driver


def connect_to_base_url(base_url, use_proxy, require_proxy_auth, proxies=None, max_retries=MAX_RETRIES):
    attempts = 1
    while attempts < max_retries:
        try:
            proxy = random.choice(proxies) if use_proxy else None
            print(f"Selected proxy: {proxy}")

            driver = get_chrome_driver(
                user_agent=USER_AGENT,
                use_proxy=use_proxy,
                require_proxy_auth=require_proxy_auth,
                proxy=proxy
            )

            # Navigate to the target page
            driver.get(base_url)
            time.sleep(2)
            if driver.title == "Access Denied":
                raise AccessDeniedException("Access denied. Try again later")
            return driver

        except AccessDeniedException:
            if not use_proxy:
                print("Access denied.")
            else:
                print(f"Access denied with proxy {proxy}.")
                proxies = [p for p in proxies if p != proxy]

        except WebDriverException as e:
            print(f"{type(e).__name__} while trying to obtain {base_url}. Retrying {attempts}/{max_retries}...")
            if 'driver' in locals():
                driver.quit()
        except Exception as e:
            print(f"{type(e).__name__} while trying to obtain {base_url}.")
            if 'driver' in locals():
                driver.quit()

        finally:
            time.sleep(DELAY * attempts)
            attempts += 1

    raise MaxRetriesExceeded(base_url)


def close_modal_windows(driver):
    # First modal window configuration
    top_modal_selector = (By.CLASS_NAME, "bfx-wm-dialog")
    top_close_button_selector = (By.ID, "bfx-wm-close-button")

    # Second modal window configuration
    bottom_modal_selector = (By.ID, "welcome-email-modal")
    bottom_close_button_selector = (By.ID, "consent-close")

    # Attempt to close the first modal
    try:
        top_modal = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(top_modal_selector)
        )
        if top_modal:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(top_close_button_selector)
            )
            time.sleep(2)  # Adding a slight delay before clicking
            close_button.click()
            print("Top modal window closed.")
    except TimeoutException:
        print("Top modal window not found. Moving on...")
    except Exception as e:
        print(f"Unexpected error occurred while handling modals: {e}")
        driver.quit()

    # Attempt to close the second modal
    try:
        bottom_modal = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located(bottom_modal_selector)
        )
        if bottom_modal:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(bottom_close_button_selector)
            )
            time.sleep(2)  # Adding a slight delay before clicking
            close_button.click()
            print("Bottom modal window closed.")
            return True
    except TimeoutException:
        print("Bottom modal window not found. Moving on...")
        return True

    except Exception as e:
        print(f"Unexpected error occurred while handling modals: {e}")
        driver.quit()


def select_section_from_dropdown_menu(driver):
    while True:
        try:
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID,"2534374302023689"))
            )
            element.click()
            driver.implicitly_wait(3)
            print(f"Navigated to {driver.current_url}")
            break

        except ElementClickInterceptedException as e:
            print("Encountered modal windows.")
            modals_passed = close_modal_windows(driver)
            if not modals_passed:
                print("Could not close all modal windows. Exiting.")
                break  # Exit the loop if modals cannot be closed

# @runtime_counter
# def scroll_to_pagination(driver):
#     """Прокручивает страницу вниз до тех пор, пока элемент next не станет видимым."""
#     scroll_step = 800
#     attempts = 1
#     max_retries = 5
#     max_scroll_attempts = 15
#     print("Started scrolling...")
#     while attempts < max_scroll_attempts:
#             try:
#                 pagination = WebDriverWait(driver, 5).until(
#                     EC.element_to_be_clickable((By.CSS_SELECTOR, "p.page-item.d-flex.next > a.d-inline-block"))
#                 )
#                 driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination)
#                 time.sleep(0.5)
#                 return True
#
#             except TimeoutException as e:
#                 # Если элемент существует, но не взаимодействуемый (например, невидим), продолжаем прокручивать
#                 driver.execute_script(f"window.scrollBy(0, {scroll_step});")
#                 print(f"I have scrolled to the bottom of the page. Trying again {attempts}/{max_scroll_attempts}...")
#                 attempts += 1
#                 time.sleep(0.25)  # Ждем немного перед следующей прокруткой
#
#             except WebDriverException as e:
#                 if 'disconnected' in str(e):
#                     print(f"Disconnected error: {e}. Retrying...")
#                     attempts += 1
#                     time.sleep(2)  # wait before retrying
#                 else:
#                     raise  # Re-raise other WebDriver exceptions
#
#             except Exception as e:
#                 # Обработка любых других исключений
#                 print(f"Something went wrong during scrolling:{e}.\nRetrying {attempts}/{max_retries}...")
#                 if attempts == max_retries:
#                     raise MaxRetriesExceeded(driver.current_url)
#                 attempts += 1
#
#     print("Failed to locate pagination after maximum retries.")
#     raise MaxRetriesExceeded(driver.current_url)

@runtime_counter
def scroll_to_pagination(driver):
    """Scrolls to the bottom of the page, then scrolls up to the pagination element."""
    retry_attempts = 0
    max_retries = 3
    max_scroll_attempts = 15
    print("Started scrolling...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    scrolling_attempts = 1
    while scrolling_attempts <= max_scroll_attempts:
        try:
            # Step 2: Attempt to find the 'Next' pagination button and ensure it's clickable
            pagination = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "p.page-item.d-flex.next > a.d-inline-block"))
            )
            # Scroll the pagination element into view
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination)
            print("Pagination in view.")
            return pagination
        except TimeoutException:
            # If pagination isn't found, scroll up and retry
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Scrolled down. Retrying to find pagination.{scrolling_attempts}//{max_scroll_attempts}..")
            scrolling_attempts += 1
            time.sleep(0.2)  # Short wait to allow page rendering
        except Exception as e:
            # Handle other unexpected errors
            retry_attempts += 1
            print(f"Error during scrolling: {e}. Retrying.{retry_attempts}//{max_retries}..")
            if retry_attempts >= max_retries:
                print(f"Max retries reached. Could not find pagination element.")
                raise MaxRetriesExceeded(driver.current_url)


    # If the loop ends without finding the pagination button, raise an error
    print("Failed to locate pagination after maximum retries.")
    raise MaxRetriesExceeded(driver.current_url)


def scrape_product_links(driver):
    """Извлекаем ссылки на продукты с текущей страницы."""

    # Extracting all the product links after the scrolldown is done
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    print(f"Got {len(product_elements)} items from the page")
    return list([link.get_attribute('href') for link in product_elements])


# def get_product(driver, url):
#     driver.get(url)
#     WebDriverWait(driver, 5).until(
#         EC.presence_of_element_located((By.CLASS_NAME, "product-secondary-section")))
#
#     # Obtaining page's HTML
#     page_source = driver.page_source
#
#     # Extracting products data
#     product = scrape_product_data(page_source=page_source)
#     print(f"Got the product: {product}")
#     return product




