from selenium import webdriver
import zipfile
import time
import os

from selenium.webdriver.common.by import By

PROXY_HOST = '45.130.126.204' # rotating proxy or host
PROXY_PORT = 8000 # proxy port
PROXY_USER = 'tsDLZZ' # username
PROXY_PASS = 'nsn4Ga' # password
TEST_IP_URL = 'https://atomurl.net/myip/'
TARGET_URL = 'https://www.saksoff5th.com/'

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = """
var config = {
        mode: "fixed_servers",
        rules: {
        singleProxy: {
            scheme: "http",
            host: "%s",
            port: parseInt(%s)
        },
        bypassList: ["localhost"]
        }
    };

chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

function callbackFn(details) {
    return {
        authCredentials: {
            username: "%s",
            password: "%s"
        }
    };
}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
);
""" % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)


def get_chromedriver(use_proxy=False, user_agent=None):
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        plugin_file = 'proxy_auth_plugin.zip'

        with zipfile.ZipFile(plugin_file, 'w') as zp:
            zp.writestr('manifest.json', manifest_json)
            zp.writestr('background.js', background_js)

        chrome_options.add_extension(plugin_file)

    if user_agent:
        chrome_options.add_argument(f'--user-agent={user_agent}')

    driver = webdriver.Chrome(options=chrome_options)

    return driver


def main():
    driver = get_chromedriver(use_proxy=False, user_agent='Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    driver.get(TARGET_URL)
    print(driver.window_handles)
    driver.implicitly_wait(10)
    i = driver.switch_to.active_element
    i.click()
    element = driver.find_element(By.ID,"2534374302023689")
    time.sleep(3)
    element.click()
    driver.implicitly_wait(10)
    print(driver.window_handles)
    driver.quit()

##selenium.common.exceptions.ElementClickInterceptedException:
# Message: element click intercepted:
# Element <a href="/c/men" id="2534374302023689" class="nav-link dropdown-toggle" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" tabindex="0">...</a> is not clickable at point (336, 155).
# Other element would receive the click: <div class="ui-widget-overlay ui-front bfx-wm-dialog-overlay"></div>
if __name__ == '__main__':
    main()