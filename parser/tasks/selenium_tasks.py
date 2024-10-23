import time

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
        print(f"Error while closing the first modal window: {e}")

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
        print(f"Error while closing the second modal window: {e}")

def select_section_from_dropdown_menu(driver):
    element = driver.find_element(By.ID,"2534374302023689")
    time.sleep(3)
    element.click()

# def page_down(driver):
#     driver.execute_script('''
#                             const scrollStep = 400; // Размер шага прокрутки (в пикселях)
#                             const scrollInterval = 500; // Интервал между шагами (в миллисекундах)
#
#                             const scrollHeight = document.documentElement.scrollHeight;
#                             let currentPosition = 0;
#                             const interval = setInterval(() => {
#                                 window.scrollBy(0, scrollStep);
#                                 currentPosition += scrollStep;
#
#                                 if (currentPosition >= scrollHeight) {
#                                     clearInterval(interval);
#                                 }
#                             }, scrollInterval);
#                         ''')


def scroll_to_pagination(driver):
    """Прокручивает страницу вниз до тех пор, пока элемент  pagination не станет видимым."""
    scroll_step = 600

    while True:
        try:
            # Проверяем, видим ли уже элемент пагинации
            pagination = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//ul[@class='mx-auto pagination']"))
            )
            # Прокручиваем до видимости элемента
            driver.execute_script("arguments[0].scrollIntoView(true);", pagination)
            print("Pagination is now in view.")
            return pagination

        except Exception:
            # Если элемент не найден, прокручиваем вниз на определенное количество пикселей
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            time.sleep(0.5)  # Ждем немного перед следующей прокруткой

def get_pages(pagination):
    pages_urls_dict = dict()
    try:
        links_to_pages = [container.get_attribute("href") for container in pagination.find_elements(By.TAG_NAME, "a")]
        for num,link in enumerate(links_to_pages,start=1):
            pages_urls_dict.update({num:link})
            print(f"{num}: {link}")
        return pages_urls_dict
    except Exception as e:
        print(f"Error while parsing pagination object: {e}")


def scrape_products(driver):
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





# def navigate_to_next_page(driver):
#     """Переходит на следующую страницу, если кнопка 'Next' доступна."""
#     next_button = WebDriverWait(driver, 10).until(
#         EC.element_to_be_clickable((By.XPATH, "//a[@class='d-inline-block' and @aria-label='Next']"))
#     )
#     # Клик по найденному элементу
#     next_button.click()
#
#     print("Navigated to the next page.")

