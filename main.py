import pickle
import time
from io import StringIO
from lxml import etree
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By

import config


driver_path = './geckodriver'
url = 'https://empower.fccollege.edu.pk/fusebox.cfm'

def register(url, term, courses) -> str:
    options = Options()
    # options.headless = True

    
    driver = webdriver.Firefox(options=options, executable_path=driver_path)

    driver.get(url)

    username = driver.find_element(By.XPATH, '//*[@id="empower_usrn"]')
    password = driver.find_element(By.XPATH, '//*[@id="empower_pswd"]')
    form = driver.find_element(By.NAME, 'LogInToEmpower')

    username.send_keys(config.username)
    password.send_keys(config.password)
    form.submit()

    
    student_records = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'top_menu_strc')))
    student_records.click()
    time.sleep(1)

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'WEBSRG49'))).click()


    catalog = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'cata_id')))
    # catalog = driver.find_element_by_name('cata_id')

    drop = Select(catalog)

    drop.select_by_value(term)

    driver.find_element(By.NAME, 'GetWindow').click()

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'add'))).click()
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'button'))).click()

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'form1')))
    # count = 0
    
    registered = []

    source = driver.page_source
    
    htmlparser = etree.HTMLParser()
    tree = etree.parse(StringIO(source), htmlparser)
    root = tree.getroot()
    tr = root.xpath("//tr")
    
    def clean_join(*content):
        return ' '.join([c.text.strip() for c in content])

    for i in tr:
        if len(i) >= 19:
            # print(i[4].text, i[5].text, i[6].text)
            # print(i[0][0].get("name"))
            current_course = clean_join(i[4], i[5], i[6])
            if current_course in courses:

                checkbox = driver.find_element(By.NAME, i[0][0].get("name"))
                driver.execute_script("arguments[0].click();", checkbox)
                registered.append(current_course)
                courses.remove(current_course)
                if len(courses) == 0:
                    break

    submit = driver.find_element(By.NAME, 'submit')
    driver.execute_script("arguments[0].click();", submit)
    

    time.sleep(3)
    submit2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'submit')))
    driver.execute_script("arguments[0].click();", submit2)

    try:
        pending = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.NAME, 'ack')))
    
        while len(pending) != 0:
            pending[0].click()
            pending = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.NAME, 'ack')))
    
    except:
        pass


courses = ['ENGL 110 A', 'EDUC 110 B']

register(url, '202122', courses)