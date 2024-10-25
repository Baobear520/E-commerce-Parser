import time

from bs4 import BeautifulSoup
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def close_first_modal_window(driver):
    try:
        # Implicitly wait for the window to show
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "bfx-wm-close-button"))
        )
        # Imitate a delay
        time.sleep(2)
        close_button.click()
        print("First modal window closed.")

    except Exception as e:
        print(type(e))
        print(f"Error while closing the first modal window: {e}")
        driver.quit()

def close_second_modal_window(driver):
    try:
        # Implicitly wait for the window to show
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "consent-close"))
        )
        #Imitate a delay
        time.sleep(2)
        close_button.click()
        print("Second modal window closed.")

    except Exception as e:
        print(type(e))
        print(f"Error while closing the second modal window: {e}")
        driver.quit()


def select_section_from_dropdown_menu(driver):
    element = driver.find_element(By.ID,"2534374302023689")
    time.sleep(3)
    element.click()


def scroll_to_pagination(driver):
    """Прокручивает страницу вниз до тех пор, пока элемент  pagination не станет видимым."""
    scroll_step = 600
    max_retries = 5

    while max_retries:
            try:
                # Проверяем, видим ли уже элемент пагинации
                pagination = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//ul[@class='mx-auto pagination']"))
                )
                # Прокручиваем до видимости элемента
                driver.execute_script("arguments[0].scrollIntoView(true);", pagination)
                print("Pagination is now in view.")
                return True

            except TimeoutException as e:
                # Если элемент существует, но не взаимодействуемый (например, невидим), продолжаем прокручивать
                driver.execute_script(f"window.scrollBy(0, {scroll_step});")
                time.sleep(0.5)  # Ждем немного перед следующей прокруткой

            except Exception as e:
                # Обработка любых других исключений
                max_retries -= 1
                print(f"Something went wrong during scrolling. Retrying ({max_retries} retries left)...")


def get_pages(driver):
    if scroll_to_pagination(driver):
        try:
            # Получаем HTML-код страницы после появления элемента пагинации
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            # Ищем контейнер с классом 'mx-auto pagination'
            pagination = soup.find('ul', class_='mx-auto pagination')
            if not pagination:
                print("Pagination container not found.")
                return []

            # Извлекаем все ссылки на страницы из контейнера
            return [a['href'] for a in pagination.find_all('a', href=True)]


        except Exception as e:
            print(type(e))
            print(f"Error while parsing pagination object: {e}")

        return []


def scrape_product_links(driver):
    """Извлекаем ссылки на продукты с текущей страницы."""

    # После завершения прокрутки извлекаем все ссылки
    product_urls_dict = dict()
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    print(f"Got {len(product_elements)} items from the page")
    for num, link in enumerate(product_elements, start=1):
        url = link.get_attribute('href')
        product_urls_dict.update({num:url})
        print(f"{num}: {url}")
    return product_urls_dict

def refresh_window(driver,url):
    driver.get(url)




