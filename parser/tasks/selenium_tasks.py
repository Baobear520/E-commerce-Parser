import queue
import time

from bs4 import BeautifulSoup
from selenium.common import TimeoutException,ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError


# top window
# <div class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-front bfx-wm-dialog ui-draggable ui-resizable" tabindex="-1" role="dialog" aria-describedby="bfx-wm-wrapper"
# button
# <a id="bfx-wm-close-button" class="bfx-wm-close" href="javascript:void(0)" aria-label="close"></a>

# second window
# <div class="modal show" id="welcome-email-modal" role="dialog" aria-modal="true" style="display: block;
# button
# <span class="consent-tracking-close svg-svg-22-cross-dims svg-svg-22-cross" id="consent-close"></span>


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
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID,"2534374302023689"))
            )
            element.click()
            driver.implicitly_wait(3)
            print(driver.current_url)
            break

        except ElementClickInterceptedException as e:
            print("Encountered modal windows.")
            modals_passed = close_modal_windows(driver)
            if not modals_passed:
                print("Could not close all modal windows. Exiting.")
                break  # Exit the loop if modals cannot be closed




def scroll_to_pagination(driver):
    """Прокручивает страницу вниз до тех пор, пока элемент  pagination не станет видимым."""
    scroll_step = 800
    attempts = 0
    max_retries = 5

    while attempts < max_retries:
            try:
                pagination = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "p.page-item.d-flex.next > a.d-inline-block"))
                )

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination)
                print("Pagination is now in view.")
                return pagination

            except TimeoutException as e:
                # Если элемент существует, но не взаимодействуемый (например, невидим), продолжаем прокручивать
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                time.sleep(0.25)  # Ждем немного перед следующей прокруткой


            except Exception as e:
                # Обработка любых других исключений
                if attempts == max_retries:
                    raise MaxRetryError
                attempts +=1
                print(f"Something went wrong during scrolling. Retrying {attempts}/{max_retries}")

def scrape_product_links(driver):
    """Извлекаем ссылки на продукты с текущей страницы."""

    # После завершения прокрутки извлекаем все ссылки
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    print(f"Got {len(product_elements)} items from the page")
    return list([link.get_attribute('href') for link in product_elements])







