import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from parser.proxy_auth import proxy_auth
from parser.selenuim_tasks.tasks import close_first_modal_window, close_second_modal_window, \
    select_section_from_dropdown_menu, scrape_products, navigate_to_next_page, \
    scroll_down, scroll_to_pagination
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
        driver = webdriver.Chrome(options=chrome_options,keep_alive=True)
        return driver
    except Exception as e:
        print(f"Error occurred: {e}")



def main():

    driver = get_chromedriver(use_proxy=False,user_agent=True)
    try:
        driver.get(TARGET_URL)
        if driver.title == "Access Denied":
            raise Exception("Access denied. Try again later")

        close_first_modal_window(driver)
        close_second_modal_window(driver)
        time.sleep(2)
        select_section_from_dropdown_menu(driver)

        scroll_to_pagination(driver)
        scrape_products(driver)
        pagination = driver.find_element((By.XPATH, "//a[@class='d-inline-block' and @aria-label='Next']"))
        for page in pagination:
            page,get_
        print(driver.current_url)

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