import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from parser.proxy_auth import proxy_auth
from parser.selenuim_tasks.tasks import close_first_modal_window, close_second_modal_window, \
    select_section_from_dropdown_menu, page_down
from parser.settings import TARGET_URL, PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS, USER_AGENT, TEST_IP_URL


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

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def main():

    driver = get_chromedriver(use_proxy=False,user_agent=True)

    driver.get(TARGET_URL)

    close_first_modal_window(driver)
    close_second_modal_window(driver)
    time.sleep(3)
    select_section_from_dropdown_menu(driver)
    time.sleep(3)

    # Ждем, пока элемент с классом 'row_product_grid' станет доступен
    try:
        product_grid = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'row product-grid')]"))
        )
        time.sleep(3)
        #Scroll down the page
        page_down(driver)
        time.sleep(15)

        list_of_element_classes = product_grid.find_elements(By.XPATH,"//div[contains(@class, 'col-6 col-sm-4 col-xl-3 product-tile-wrapper')]")
        print(f"Got {len(list_of_element_classes)} items from the page")

        for num, element in enumerate(list_of_element_classes,start=1):
            target_class = element.find_element(By.CLASS_NAME, "image-container")
            thumb_link_classes = target_class.find_elements(By.CLASS_NAME, "thumb-link")

            for link in thumb_link_classes:
                print(f"{num}: {link.get_attribute('href')}")

        next_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "p.page-item.d-flex.next > a"))
        )
        next_button.click()
        time.sleep(10)
    finally:
        driver.quit()

if __name__ == '__main__':
    main()