import os
from itertools import count
from statistics import mean

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

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


def predict_rub_salary_sj(vacancy, token):
    headers = {
        'X-Api-App-Id': token
    }
    expected_salaries = []
    for page in count(0):
        params = {
            'town': 4,
            'keyword': f'Программист {vacancy}',
            'period': 30,
            'page': page
        }
        response = requests.get('https://api.superjob.ru/2.0/vacancies', headers=headers, params=params)
        response.raise_for_status()
        content = response.json()
        objects = content.get('objects')
        for item in objects:
            salary_from = item.get('payment_from')
            salary_to = item.get('payment_to')
            if not predict_salary(salary_from, salary_to):
                continue
            expected_salaries.append(predict_salary(salary_from, salary_to))
        is_more_pages = content['more']
        vacancies_found = content.get('total')
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
    response = requests.get('https://api.hh.ru/vacancies/', params=payload)
    response.raise_for_status()
    content = response.json()
    pages_number = content['pages']
    expected_salaries = []
    while page < pages_number:
        items = content.get('items')
        for item in items:
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
    if not salary_to and not salary_from:
        return None
    else:
        if not salary_to:
            return salary_from * 1.2
        elif not salary_from:
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


def main():
    load_dotenv()
    sj_api_token = os.getenv('SJ_TOKEN')
    hh_salary_data = {}
    sj_salary_data = {}
    for lang in programming_languages:
        hh_salary_data[lang] = predict_rub_salary_hh(lang)
        sj_salary_data[lang] = predict_rub_salary_sj(lang, sj_api_token)
    display_table(hh_salary_data, 'HeadHunter Moscow')
    display_table(sj_salary_data, 'SuperJob Moscow')


if __name__ == "__main__":
    main()
