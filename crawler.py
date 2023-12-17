import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def get_url(website_url, email, password):
    chrome_version = '114.0.5735.90'
    received_url = ''
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--profile-directory=Default')
    options.add_argument('--user-data-dir=~/.config/google-chrome')
    options.add_argument("--remote-debugging-port=9222")
    chrome_binary_path = '/opt/render/project/.render/chrome/opt/google/chrome'
    options.binary_location = chrome_binary_path
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager(driver_version=chrome_version).install()), options=options)
    
    try:
        driver.get(website_url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for the Member Login link to be present
        member_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Member Login")))
        
        # If the login link is present, perform login
        member_button.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='email']"))).send_keys(email)
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='password']"))).send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[2]/div/div[3]/button"))).click()
        
        # Wait for the page to load after login
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='some-class']")))
        
        # Get the URL after login
        received_url = driver.page_source
    
    except NoSuchElementException:
        received_url = driver.page_source
    
    finally:
        driver.quit()
        return received_url
