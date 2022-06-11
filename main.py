import pickle
import time
from io import StringIO
from lxml import etree
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By

import config

try:
    driver_path = config.driver_path
except:
    driver_path = 'geckodriver.exe'


url = 'https://empower.fccollege.edu.pk/fusebox.cfm'


def create_db(term):
    from database import create_database

    print('Creating database please wait... (This may take a minute or two)')

    create_database(term)

    print('Database created!')


def check_course_clash(course1, course2):
        course1_days = ''.join(course1['days'])
        course2_days = ''.join(course2['days'])

        if course1_days in course2_days or course2_days in course1_days:
            if course1['start_time'] <= course2['start_time'] <= course1['end_time'] or course1['start_time'] <= course2['end_time'] <= course1['end_time']:
                return True
        return False


def check_clash(term, input_courses, recreate_database=False):
    if recreate_database:
        create_db(term)

    try:
        with open(f'course-data-{term}.pickle', 'rb') as file:
            data = pickle.load(file)
    except:
        create_db(term)

        with open(f'course-data-{term}.pickle', 'rb') as file:
            data = pickle.load(file)

    input_courses = [x.strip().upper() for x in input_courses]

    courses = []

    for i in data:
        if i['name'] in input_courses:
            if i['lab']:
                i['name'] = i['name'] + ' Lab'
                courses.append(i)
                continue
            courses.append(i)

    detected = []

    track_detected = False

    for i in courses:
        for j in courses:
            if i['name'] != j['name'] and check_course_clash(i, j):
                for k in detected:
                    if i['name'] in k and j['name'] in k:
                        track_detected = True
                        break
                    track_detected = False
                
                if not track_detected:
                    detected.append((i['name'], j['name']))
                    print(i['name'], 'clashes with', j['name'])
                track_detected = False

    if detected:
        return True
    
    return False


def register(url, term, course_catalog, courses, recreate_database=False) -> str:

    if check_clash(term, courses, recreate_database):
        print('Please fix the clash and try again')
        return False

    options = Options()
    options.headless = True

    
    driver = webdriver.Firefox(options=options, service=Service(driver_path))

    driver.get(url)

    username = driver.find_element(By.XPATH, '//*[@id="empower_usrn"]')
    password = driver.find_element(By.XPATH, '//*[@id="empower_pswd"]')
    form = driver.find_element(By.NAME, 'LogInToEmpower')

    username.send_keys(config.username)
    password.send_keys(config.password)
    print('\nLogging in...\n')
    form.submit()
    print('Logged in!\n')

    
    student_records = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'top_menu_strc')))
    student_records.click()
    time.sleep(1)

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.ID, 'WEBSRG49'))).click()


    catalog = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'cata_id')))


    drop = Select(catalog)

    drop.select_by_value(course_catalog)

    print('Selecting catalog...\n')
    driver.find_element(By.NAME, 'GetWindow').click()

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'add'))).click()
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'button'))).click()

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.NAME, 'form1')))
    print('Selecting courses...\n')
    
    registered = []
    courses = [x.strip().upper() for x in courses] 

    source = driver.page_source
    
    htmlparser = etree.HTMLParser()
    tree = etree.parse(StringIO(source), htmlparser)
    root = tree.getroot()
    tr = root.xpath("//tr")
    
    def clean_join(*content):
        return ' '.join([c.text.strip() for c in content])

    for i in tr:
        if len(i) >= 19:
            current_course = clean_join(i[4], i[5], i[6])
            if current_course in courses:

                checkbox = driver.find_element(By.NAME, i[0][0].get("name"))
                driver.execute_script("arguments[0].click();", checkbox)
                registered.append(current_course)
                courses.remove(current_course)
                if len(courses) == 0:
                    break

    submit = driver.find_element(By.NAME, 'submit')
    print('Submitting...\n')
    driver.execute_script("arguments[0].click();", submit)
    

    time.sleep(3)
    submit2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.NAME, 'submit')))
    print('Done!')

    info = driver.find_element(By.CSS_SELECTOR, '#ptl-content > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(1) > th:nth-child(1) > h3:nth-child(1)').text
    skip = False
    if '0 Pending' in info:
        skip = True
    driver.execute_script("arguments[0].click();", submit2)

    if not skip:
        print('Acknowledging...\n')
        try:
            pending = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.NAME, 'ack')))
        
            while len(pending) != 0:
                pending[0].click()
                pending.pop(0)
                if len(pending) == 0:
                    break
                pending = WebDriverWait(driver, 30).until(EC.visibility_of_all_elements_located((By.NAME, 'ack')))
    
        except:
         pass

    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#ptl-content > table:nth-child(5)'))).screenshot('courses.png')
    print('Finished!\n')

    driver.quit()

    return True


courses = input('Enter courses and comma separate them (eg. envr 240 a, geog 101 a): ').split(',')
semester = input('Enter semester (eg. 2022 Summer): ')
is_pharmacy = input('Department of Pharmacy? (y/n): ')

year, semester_name = semester.split()


if semester_name.lower() == 'summer':
    semester_initials = 'SU'
    catalog = f'{int(year)-1}{year[2:]}'

elif semester_name.lower() == 'fall':
    semester_initials = 'FA'
    catalog = f'{year}{int(year[2:])+1}'

elif semester_name.lower() == 'winter':
    semester_initials = 'WN'
    print('Winter is not supported yet')
    exit()

elif semester_name.lower() == 'spring':
    semester_initials = 'SP'
    print('Spring is not supported yet')
    exit()


if is_pharmacy.lower() == 'y':
    term = f'PH{year[2:]}{semester_initials}'
    catalog = 'PH' + catalog[2:]
else:
    term = f'{year}{semester_initials}'


result = register(url, term, catalog, courses)

if result:
    print('Successfully registered! (You may want to check if some courses have not been registered, pre req not met or credit limit reached)')
else:
    print('Failed to register!')