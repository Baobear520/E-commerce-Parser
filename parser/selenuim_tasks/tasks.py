import time
from multiprocessing.dummy import current_process

from selenium.common import ElementNotInteractableException
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


# def wait_for_all_products_to_load(driver):
#     """Ждем, пока все элементы товаров подгрузятся в 'row grid'."""
#     page_down(driver)
#     # Ожидаем, пока высота страницы перестанет изменяться, что указывает на завершение подгрузки элементов
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     scroll_attempts = 0
#     max_attempts = 5
#
#     while scroll_attempts < max_attempts:
#         time.sleep(3)  # Даем время для подгрузки новых элементов
#         new_height = driver.execute_script("return document.body.scrollHeight")
#
#         if new_height == last_height:
#             scroll_attempts += 1
#         else:
#             scroll_attempts = 0  # Сбрасываем счетчик, если высота изменилась
#
#         last_height = new_height


def scroll_to_pagination(driver):
    """Прокручивает страницу вниз до тех пор, пока элемент <ul class='mx-auto pagination'> не станет видимым."""
    scroll_step = 400

    elements_per_row = 4
    expected_number_of_items = 92
    estimated_number_of_rows = expected_number_of_items//elements_per_row

    max_attempts = estimated_number_of_rows * 2
   # attempts = 0

    while True:
        try:
            # Проверяем, видим ли уже элемент пагинации
            pagination = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='d-inline-block' and @aria-label='Next']"))
            )
            # Прокручиваем до видимости элемента
            driver.execute_script("arguments[0].scrollIntoView(true);", pagination)
            print("Pagination is now in view.")
            break
             # Выходим из цикла, если элемент найден и видим

        except Exception:
            # Если элемент не найден, прокручиваем вниз на определенное количество пикселей
            driver.execute_script(f"window.scrollBy(0, {scroll_step});")
            time.sleep(0.5)  # Ждем немного перед следующей прокруткой
            # attempts += 1
            # print(f"Scrolling attempt {attempts}...")
#
#     if attempts == max_attempts:
#         print("Pagination element not found after multiple attempts.")


# def scroll_down(driver):
#     """A method for scrolling the page and collecting product URLs."""
#
#     # Get initial scroll height.
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     scroll_step = 400
#     current_position = scroll_step
#     product_urls = set()  # Используем множество для хранения уникальных ссылок
#
#     while True:
#         next_button = WebDriverWait(driver, 20).until(
#             EC.element_to_be_clickable((By.XPATH, "//a[@class='d-inline-block' and @aria-label='Next']"))
#         )
#         # Scroll down by the current scroll step.
#         driver.execute_script(f"window.scrollTo(0, {current_position});")
#
#         # Wait for new elements to load.
#         time.sleep(2)  # Лучше использовать time.sleep для явного ожидания
#
#         # Find all product elements and extract their URLs.
#         product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
#         for link in product_elements:
#             product_urls.add(link.get_attribute('href'))
#
#         # Print the number of unique URLs collected so far.
#         print(f"Collected {len(product_urls)} unique links")
#
#         # Calculate new scroll height and compare with last scroll height.
#         #new_height = driver.execute_script("return document.body.scrollHeight")
#
#         # Break the loop if no new content is loaded.
#         if current_position == last_height:
#             break
#
#         current_position += scroll_step
#
#     print("Scrolling and data collection complete.")
#     next_button.click()
#     print("Navigated to the next page.")
#
#     driver.implicitly_wait(10)
#     return product_urls

def scrape_products(driver):
    """Извлекаем ссылки на продукты с текущей страницы."""

    # После завершения прокрутки извлекаем все ссылки
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    print(f"Got {len(product_elements)} items from the page")
    for num, link in enumerate(product_elements, start=1):
        print(f"{num}: {link.get_attribute('href')}")

def navigate_to_next_page(driver):
    """Переходит на следующую страницу, если кнопка 'Next' доступна."""
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@class='d-inline-block' and @aria-label='Next']"))
    )
    # Клик по найденному элементу
    next_button.click()


    print("Navigated to the next page.")


def scroll_until_next_button(driver):
    """Прокручивает страницу до тех пор, пока не станет видимым элемент 'Next', затем собирает ссылки и кликает на 'Next'."""

    product_urls = set()  # Используем множество для хранения уникальных ссылок
    scroll_step = 400
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Прокручиваем страницу на scroll_step пикселей
        driver.execute_script(f"window.scrollBy(0, {scroll_step});")
        time.sleep(2)  # Даем время на подгрузку новых элементов

        # Пытаемся найти кнопку "Next"
        try:
            next_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//a[@class='d-inline-block' and @aria-label='Next']"))
            )
            print("Next button found. Waiting for product scraping to complete.")
            # Кликаем по кнопке "Next", если она была найдена
            if next_button:
                next_button.click()
                print("Navigated to the next page.")
                time.sleep(3)  # Даем время странице загрузиться перед началом нового этапа
            break  # Если кнопка найдена, выходим из цикла прокрутки
        except:
            print("Next button not yet visible, continuing scrolling...")

        # Проверяем, изменилась ли высота страницы
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("Reached the bottom of the page, but 'Next' button not found.")
            break
        last_height = new_height

    # После завершения прокрутки и нахождения кнопки "Next", собираем ссылки
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a.thumb-link")
    for link in product_elements:
        product_urls.add(link.get_attribute('href'))

    print(f"Collected {len(product_urls)} unique product links before clicking 'Next'.")



    return product_urls