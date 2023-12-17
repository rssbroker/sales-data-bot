import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException


def get_url(website_url, email, password):
    received_url = ''
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    driver = webdriver.Chrome(
        "/usr/lib/chromium-browser/chromedriver", chrome_options=options
    )
    driver.get(website_url)
    time.sleep(2)
    try:
        member_button = driver.find_element(By.LINK_TEXT, "Member Login")
    except NoSuchElementException:
        received_url = driver.page_source
    else:
        member_button.click()
        time.sleep(2)
        driver.find_element(
            By.XPATH, "//*[@id='email']").send_keys(email)
        driver.find_element(
            By.XPATH, "//*[@id='password']").send_keys(password)
        driver.find_element(
            By.XPATH, "/html/body/div[7]/div[2]/div/div[3]/button").click()
        time.sleep(2)
        received_url = driver.page_source
    finally:
        driver.quit()
        return received_url
