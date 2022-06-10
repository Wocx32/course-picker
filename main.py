import pickle
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By

import config


driver_path = './geckodriver'
url = 'https://empower.fccollege.edu.pk/fusebox.cfm'

def get_source(url) -> str:
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

    drop.select_by_value('202122')

    driver.find_element(By.NAME, 'GetWindow').click()

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'add'))).click()
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'button'))).click()

    form = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'form1')))
    # count = 0

    for i in form.find_elements(By.TAG_NAME, 'tr'):
        children = i.find_elements(By.TAG_NAME, 'td')
        if len(children) >= 36 and children[2].text == 'Credit':
            print(len(children))
            print([child.text for child in children])
            # print(children[5].text, children[6].text, children[7].text)
            print('\n')
            # count += 1
        # children = i.find_elements(By.TAG_NAME, 'td')
        # if len(children) > 17:
        #     print(children[5].text, children[6].text, children[7].text)
            

    # driver.quit()
    # return source

get_source(url)

# with open('course-data.pickle', 'rb') as file:
#     data = pickle.load(file)


# for i in data:
#     if 'CSCS 201' in i['name']:
#         print(i['name'], i['seats'])