import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from parser.proxy_auth import proxy_auth
from parser.tasks.bs4_tasks import parse_product_data
from parser.tasks.db_scripts import init_db, save_to_sqlite_db, check_sqlite_db
from parser.tasks.other_tasks import save_to_json, save_to_html, save_to_db
from parser.tasks.selenium_tasks import close_first_modal_window, close_second_modal_window, \
    select_section_from_dropdown_menu, scrape_product_links,  \
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

def preparations(driver):
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
    init_db()
    driver = get_chromedriver(user_agent=True)
    try:
        driver.get(TARGET_URL)
        if driver.title == "Access Denied":
            raise Exception("Access denied. Try again later")

        preparations(driver)
        pagination = scroll_to_pagination(driver)

        pages_urls = get_pages(pagination)
        # if pages_urls:
        #     save_to_json(
        #         data=pages_urls,
        #         file_name="pages_urls.json"
        #     )
        product_urls = scrape_product_links(driver)
        # if product_urls:
        #     save_to_json(
        #     data=product_urls,
        #     file_name="product_urls.json"
        # )
        #Test values
        # product_urls = {
        #     "1": "https://www.saksoff5th.com/product/colmar-repunk-channel-quilted-puffer-jacket-0400021682790.html?dwvar_0400021682790_color=BOTTLE_COFFEE_GREEN",
        #     "2": "https://www.saksoff5th.com/product/gucci-57mm-aviator-sunglasses-0400021994128.html?dwvar_0400021994128_color=BLACK",
        #     "3": "https://www.saksoff5th.com/product/purple-brand-high-rise-slim-fit-jeans-0400019660945.html?dwvar_0400019660945_color=VINTAGE",
        # }

        products = fetch_products(driver=driver,product_urls=product_urls)
        #save_to_db(products=products)
        save_to_sqlite_db(products=products)
        check_sqlite_db()

    except Exception as e:
        print(type(e))

    finally:
        driver.quit()


if __name__ == '__main__':
    main()