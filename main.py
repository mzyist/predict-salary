import os
from itertools import count
from statistics import mean

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


def predict_rub_salary_sj(vacancy):
    global vacancies_found
    headers = {
        'X-Api-App-Id': sj_api_token
    }
    expected_salaries = []
    for page in count(0):
        params = {
            'town': 4,
            'keyword': f'Программист {vacancy}',
            'period': 30,
            'page': page
        }
        response = requests.get(sj_api_url, headers=headers, params=params)
        response.raise_for_status()
        content = response.json().get('objects')
        for item in content:
            salary_from = item.get('payment_from')
            salary_to = item.get('payment_to')
            if not predict_salary(salary_from, salary_to):
                continue
            expected_salaries.append(predict_salary(salary_from, salary_to))
        is_more_pages = response.json()['more']
        vacancies_found = response.json().get('total')
        if not is_more_pages:
            break
    vacancies_processed = len(expected_salaries)
    average_salary = int(mean(expected_salaries))
    sj_salary_template = {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary
    }
    return sj_salary_template


def predict_rub_salary_hh(vacancy):
    page = 0
    payload = {
        'text': f'Программист {vacancy}',
        'area': 1,
        'only_with_salary': True,
        'page': page
    }
    response = requests.get(hh_api_url, params=payload)
    response.raise_for_status()
    pages_number = response.json()['pages']
    expected_salaries = []
    while page < pages_number:
        content = response.json().get('items')
        for item in content:
            salary = item.get('salary')
            salary_from = salary.get('from')
            salary_to = salary.get('to')
            currency = salary.get('currency')
            if currency == 'RUR':
                expected_salaries.append(predict_salary(
                    salary_from,
                    salary_to
                ))
            else:
                pass
        page += 1
    average_salary = int(mean(expected_salaries))
    vacancies_processed = len(expected_salaries)
    vacancies_found = response.json().get('found')
    hh_salary_template = {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed,
        'average_salary': average_salary
    }
    return hh_salary_template


def predict_salary(salary_from, salary_to):
    if salary_to == 0 or False and salary_from == 0 or False:
        return None
    else:
        if salary_to is None or salary_to == 0:
            return salary_from * 1.2
        elif salary_from is None or salary_from == 0:
            return salary_to * 0.8
        else:
            return (salary_from + salary_to) / 2


def display_table(table_data_dict, title):
    table_data = [
        [
            'Язык программирования',
            'Вакансий найдено',
            'Вакансий обработано',
            'Средняя зарплата'
        ]
    ]
    for lang in programming_languages:
        table_data.append(
            [
                lang,
                table_data_dict[lang]['vacancies_found'],
                table_data_dict[lang]['vacancies_processed'],
                table_data_dict[lang]['average_salary']
            ]
        )
    table = AsciiTable(table_data, title)
    print(table.table)


if __name__ == "__main__":
    load_dotenv()
    sj_api_url = 'https://api.superjob.ru/2.0/vacancies'
    hh_api_url = 'https://api.hh.ru/vacancies/'
    sj_api_token = os.getenv('SJ_TOKEN')
    programming_languages = [
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'Go'
    ]
    hh_salary_data = {}
    sj_salary_data = {}
    for vacancy in programming_languages:
        hh_salary_data[vacancy] = predict_rub_salary_hh(vacancy)
        sj_salary_data[vacancy] = predict_rub_salary_sj(vacancy)
    display_table(hh_salary_data, 'HeadHunter Moscow')
    display_table(sj_salary_data, 'SuperJob Moscow')
