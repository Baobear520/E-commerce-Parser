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


def page_down(driver):
    driver.execute_script('''
                            const scrollStep = 200; // Размер шага прокрутки (в пикселях)
                            const scrollInterval = 100; // Интервал между шагами (в миллисекундах)

                            const scrollHeight = document.documentElement.scrollHeight;
                            let currentPosition = 0;
                            const interval = setInterval(() => {
                                window.scrollBy(0, scrollStep);
                                currentPosition += scrollStep;

                                if (currentPosition >= scrollHeight) {
                                    clearInterval(interval);
                                }
                            }, scrollInterval);
                        ''')

