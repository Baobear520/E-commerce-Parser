import time

from selenium import webdriver

from parser.proxy_auth import proxy_auth
from parser.tasks.bs4_tasks import parse_product_data
from parser.tasks.other_tasks import save_to_json, save_to_html
from parser.tasks.selenium_tasks import close_first_modal_window, close_second_modal_window, \
    select_section_from_dropdown_menu, scrape_products,  \
    scroll_to_pagination, get_pages
from parser.settings import TARGET_URL, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS, USER_AGENT


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

    if user_agent:
        chrome_options.add_argument(f'--user-agent={USER_AGENT}')
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error occurred: {e}")



def main():

    driver = get_chromedriver(user_agent=True)
    try:
        driver.get(TARGET_URL)
        if driver.title == "Access Denied":
            raise Exception("Access denied. Try again later")

        close_first_modal_window(driver)
        close_second_modal_window(driver)
        time.sleep(1)

        select_section_from_dropdown_menu(driver)

        pagination = scroll_to_pagination(driver)
        pages_urls = get_pages(pagination)
        save_to_json(
            data=pages_urls,
            file_name="pages_urls.json"
        )
        product_urls = scrape_products(driver)
        save_to_json(
            data=product_urls,
            file_name="product_urls.json"
        )
        driver.switch_to.new_window('tab')
        time.sleep(3)
        url = product_urls.get(1)
        driver.get(url=url)
        time.sleep(3)
        page_source = str(driver.page_source)
        save_to_html(page_source=page_source, file_name="test_product.html")

    except Exception as e:
        print(f"{e}")

    finally:
        driver.quit()


        # while True:  # Цикл для перехода по страницам
        #     wait_for_all_products_to_load(driver)
        #     scrape_products(driver)
        #     if not navigate_to_next_page(driver):
        #         print("No more pages available.")
        #         break




if __name__ == '__main__':
    main()