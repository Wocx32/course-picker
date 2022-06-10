import pickle
import datetime
from bs4 import BeautifulSoup
from scrape import get_source


url = 'https://empower.fccollege.edu.pk/fusebox.cfm?fuseaction=CourseCatalog'


def get_page_source(term):
    source = get_source(url, term)
    soup = BeautifulSoup(source, 'html.parser')

    return soup.find('div', id='courses')


def convert_time(time_string):
    return datetime.datetime.strptime(time_string, '%H:%M')

def get_data(content):
    return ' '.join(content.get_text().strip().replace('\t', '').replace('\n', '').split())

def get_name(content):
    return ' '.join(content.get_text().strip().replace('\t', '').split('\n')[0].split())

def parse_classroom(string):
    s = string.get_text().strip()

    if 'TBD' in s:
        return {'building:': 'TBD', 'classroom': 'TBD'}

    if s[0] == 'S':
        return {'building': 'SBLOCK', 'classroom': s[6:]}

    if s[0] == 'E':
        return {'building': 'EBLOCK', 'classroom': s[6:]}

    if s[0] == 'L':
        return {'building': 'LUCAS', 'classroom': 'LUCAS'}

    if s == 'MCENTE01':
        return {'building': 'MCENTE', 'classroom': '01'}


def parse_schedule(string):
    s = string.split()
    
    time_from = s[-3]
    time_till = s[-1]

    days = s[1:-3]

    if len(days) == 1:
        days = list(days[0])

    start_time = convert_time(time_from)
    end_time = convert_time(time_till)

    if end_time < start_time:
        start_time, end_time = end_time, start_time

    return {'start_time': start_time, 'end_time': end_time, 'days': days}


def get_info(courses):

    data = []

    prev_course = None

    for j in courses.contents[5:-3:2]:

        if j and (len(j.contents) >= 19 or len(j.contents) == 13):

            schedule = get_data(j.contents[9])
            if not schedule.split()[-1][0].isdigit():
                continue


            data_dict = {
                "name": get_name(j.contents[3]),
                "lab": False,
                "seats": None
            }

            if len(j.contents) == 19:
                data_dict['seats'] = int(get_data(j.contents[15]))

            data_dict.update(parse_classroom(j.contents[7]))

            data_dict.update(parse_schedule(schedule))

            data.append(data_dict)

            prev_course = get_name(j.contents[3])
        
        elif j and (len(j.contents) == 15 or len(j.contents) == 9):

            schedule = get_data(j.contents[5])

            data_dict = {
                "name": prev_course,
                "lab": True,
                "seats": None
            }

            if len(j.contents) == 15:
                data_dict['seats'] = int(get_data(j.contents[11]))

            else:
                data_dict['seats'] = int(get_data(j.contents[8]))

            data_dict.update(parse_classroom(j.contents[3]))

            data_dict.update(parse_schedule(schedule))

            data.append(data_dict)


    return data


def convert_to_datetime(timestamp):
    return datetime.datetime.strptime(timestamp, '%H:%M')

def create_database(term):
    data = get_info(get_page_source(term))

    with open('course-data.pickle', 'wb') as file:
        pickle.dump(data, file)

if __name__ == '__main__':
    print('Creating database...')
    create_database('2022FA')
    print('Database created!')