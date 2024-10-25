import time

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from parser.proxy_auth import proxy_auth
from parser.tasks.bs4_tasks import parse_product_data
from parser.tasks.db_scripts import init_db, save_to_sqlite_db, check_sqlite_db
from parser.tasks.selenium_tasks import close_first_modal_window, close_second_modal_window, \
    select_section_from_dropdown_menu, scrape_product_links,  \
    scroll_to_pagination, get_pages
from parser.settings import TARGET_URL, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS, USER_AGENT, DB_PATH


def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        plugin_file = proxy_auth(
            host=PROXY_HOST,
            port=PROXY_PORT,
            user=PROXY_USER,
            password=PROXY_PASS
        )
        chrome_options.add_extension(plugin_file)
    #chrome_options.add_extension('--headless==new')

    if user_agent:
        chrome_options.add_argument(f'--user-agent={USER_AGENT}')
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error occurred: {e}")

def preparations_in_browser(driver):
    close_first_modal_window(driver)
    close_second_modal_window(driver)
    time.sleep(1)
    select_section_from_dropdown_menu(driver)
    print(f"The page {driver.current_url} is ready for parsing!")


def fetch_products(driver,product_urls):
    products = []
    for v in product_urls.values():
        # Opening a new tab with the product url
        driver.switch_to.new_window('tab')
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)

        driver.get(url=v)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "product-secondary-section")))

        # Obtaining page's HTML
        page_source = driver.page_source
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        # Extracting products data
        product = parse_product_data(page_source=page_source)
        products.append(product)
        print(f"Added {product} to the list")

    print(f"Got {len(products)} products in the dictionary")
    return products


def main():
    max_retries = 5
    attempts = 0

    while attempts < max_retries:
        try:
            # Инициализация базы данных и драйвера браузера
            init_db(db=DB_PATH)
            driver = get_chromedriver(user_agent=True)

            # Записываем время начала выполнения скрипта
            start_time = time.time()

            # Переход на целевой URL
            driver.get(TARGET_URL)
            if driver.title == "Access Denied":
                raise Exception("Access denied. Try again later")

            attempts = 0

            # Подготовительные действия
            preparations_in_browser(driver)

            # Извлечение ссылок на страницы и добавление первой страницы
            pages_urls = get_pages(driver)
            pages_urls[0] = driver.current_url


            # Цикл по страницам
            for page in pages_urls:
                if page != driver.current_url:
                    driver.get(page)
                    # Ждем, пока URL обновится на нужный
                    WebDriverWait(driver, 10).until(
                        lambda d: d.current_url == page
                    )
                    print(f"Navigated to: {driver.current_url}")

                    scroll_to_pagination(driver)

                # Извлекаем ссылки на продукты и данные о них
                product_urls = scrape_product_links(driver)
                products = fetch_products(driver=driver, product_urls=product_urls)

                # Сохраняем данные о продуктах в базу данных
                save_to_sqlite_db(db=DB_PATH, data=products)

            # Выводим время выполнения скрипта
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Script execution time: {elapsed_time:.2f} seconds")

            # Проверка всех записей в таблице "products"
            check_sqlite_db(db=DB_PATH)
            break  # Если все прошло успешно, выходим из цикла

        except WebDriverException as e:
            attempts += 1
            print(f"Couldn't establish internet connection. Retrying... ({attempts} attempt).")
            if attempts == max_retries:
                print("Reached maximum number of attempts to connect to the server.")
                raise ConnectionError("Unable to establish a connection after multiple attempts.")
            else:
                # Если не достигли максимального количества попыток, перезапускаем драйвер
                driver.delete_all_cookies()
                time.sleep(30)  # Ждем немного перед новой попыткой

        except Exception as e:
            print(f"Exception of type {type(e)} occurred: {e}")
            break

        finally:
            # Закрываем браузер, если он был открыт
            if 'driver' in locals():
                driver.quit()
# def main():
#     start_time = time.time()
#
#     init_db(db=DB_PATH)
#     driver = get_chromedriver(user_agent=True)
#
#     max_retries = 5
#     attempts = 0
#
#     while attempts < max_retries:
#         try:
#             driver.get(TARGET_URL)
#             if driver.title == "Access Denied":
#                 raise Exception("Access denied. Try again later")
#
#             preparations_in_browser(driver)
#
#             pages_urls = get_pages(driver)
#             pages_urls[0] = driver.current_url
#
#             for page in pages_urls:
#                 if page != driver.current_url:
#                     driver.get(page)
#                     # Ждем, пока URL обновится на нужный
#                     WebDriverWait(driver, 10).until(
#                         lambda d: d.current_url == page
#                     )
#                     print(f"Navigated to: {driver.current_url}")
#
#                     scroll_to_pagination(driver)
#
#                 #Extracting products urls and data
#                 product_urls = scrape_product_links(driver)
#                 products = fetch_products(driver=driver,product_urls=product_urls)
#                 #Saving the products from the current page to the DB
#                 save_to_sqlite_db(
#                     db=DB_PATH,
#                     data=products)
#
#             # Displaying the script's execution time
#             end_time = time.time()
#             elapsed_time = end_time - start_time
#             print(f"Script execution time: {elapsed_time:.2f} seconds")
#             # Checking all the records in the "products" table
#             check_sqlite_db(db=DB_PATH)
#
#         except WebDriverException as e:
#             attempts += 1
#             print(f"Couldn't establish internet connection. Retrying... ({attempts} attempt).")
#             if attempts == max_retries:
#                 raise ConnectionError("Reached maximum number of attempts to connect to the server.")
#
#
#         except Exception as e:
#             print(f"Exception of type {type(e)} occurred: {e}") # Catching the type of the exception
#             break
#
#         finally:
#             driver.quit()


if __name__ == '__main__':
    main()