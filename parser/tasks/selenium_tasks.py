import queue
import time

from bs4 import BeautifulSoup
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib3.exceptions import MaxRetryError

def close_modal_windows(driver):
    # First modal window configuration
    first_modal_selector = (By.CLASS_NAME, "bfx-wm-dialog")
    first_close_button_selector = (By.ID, "bfx-wm-close-button")

    # Second modal window configuration
    second_modal_selector = (By.ID, "welcome-email-modal")
    second_close_button_selector = (By.ID, "consent-close")

    # Attempt to close the first modal
    try:
        first_modal = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(first_modal_selector)
        )
        if first_modal:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(first_close_button_selector)
            )
            time.sleep(2)  # Adding a slight delay before clicking
            close_button.click()
            print("First modal window closed.")
    except TimeoutException:
        print("First modal window not found. Moving on...")

    # Attempt to close the second modal
    try:
        second_modal = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located(second_modal_selector)
        )
        if second_modal:
            close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(second_close_button_selector)
            )
            time.sleep(2)  # Adding a slight delay before clicking
            close_button.click()
            print("Second modal window closed.")
    except TimeoutException:
        print("Second modal window not found. Moving on...")

    except Exception as e:
        print(f"Unexpected error occurred while handling modals: {e}")
        driver.quit()


    #first window
    #<div class="ui-dialog ui-widget ui-widget-content ui-corner-all ui-front bfx-wm-dialog ui-draggable ui-resizable" tabindex="-1" role="dialog" aria-describedby="bfx-wm-wrapper"
    #button
    #<a id="bfx-wm-close-button" class="bfx-wm-close" href="javascript:void(0)" aria-label="close"></a>

    #second window
    #<div class="modal show" id="welcome-email-modal" role="dialog" aria-modal="true" style="display: block;
    #button
    #<span class="consent-tracking-close svg-svg-22-cross-dims svg-svg-22-cross" id="consent-close"></span>

def select_section_from_dropdown_menu(driver):
    element = driver.find_element(By.ID,"2534374302023689")
    time.sleep(3)
    element.click()


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
    product_urls = queue.Queue()
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    print(f"Got {len(product_elements)} items from the page")
    [product_urls.put(link.get_attribute('href')) for link in product_elements]
    return product_urls






