# import beautifulsoup
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from config import driver_path

def get_source(url, semester) -> str:
    options = Options()
    options.headless = True

    
    driver = webdriver.Firefox(options=options, executable_path=driver_path)
    # driver = webdriver.Firefox(options=options, executable_path='/home/rusian/programming/project-common-room/geckodriver')
    
    driver.get(url)

    term = driver.find_element_by_xpath('//*[@id="empower_global_term_id"]')
    drop = Select(term)

    drop.select_by_value(semester)


    button = driver.find_element_by_xpath('//*[@id="search"]')
    button.click()
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, "courses")))
    source = driver.page_source

    driver.quit()
    return source

