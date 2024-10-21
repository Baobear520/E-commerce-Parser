from selenium import webdriver


from parser.proxy_auth import proxy_auth
from parser.selenuim_tasks.tasks import close_first_modal_window, close_second_modal_window, \
    select_section_from_dropdown_menu
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

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def main():
    driver = get_chromedriver(use_proxy=False, user_agent=True)
    driver.get(TARGET_URL)

    close_first_modal_window(driver)
    close_second_modal_window(driver)

    select_section_from_dropdown_menu(driver)

    # Implicitly wait until the page fully loads
    driver.implicitly_wait(15)

    driver.quit()

if __name__ == '__main__':
    main()