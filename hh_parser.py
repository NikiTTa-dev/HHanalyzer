import requests
import pandas as pd


def json_convert(json):
    """
    Производит парсинг json в список значений
    :param json: dict
    :return: [str]
    """
    salary_from = None
    salary_to = None
    salary_currency = None
    area_name = None

    if json['salary'] is not None:
        salary_from = json['salary']['from']
        salary_to = json['salary']['to']
        salary_currency = json['salary']['currency']

    if json['area'] is not None:
        area_name = json['area']['name']

    return [json['name'], str(salary_from), str(salary_to), salary_currency, area_name, json['published_at']]


def get_vacancies():
    """
    Загружает выкансии с сайта сохраняет их в CSV
    """
    df = pd.DataFrame(columns=['name', 'salary_from', 'salary_to', 'salary_currency', 'area_name', 'published_at'])
    for hour in range(0, 24, 6):
        url = f'https://api.hh.ru/vacancies?specialization=1&date_from=2022-12-08T{("0" + str(hour))[-2:]}:00:00' \
              f'&date_to=2022-12-' \
              f'{("0" + str(8 + ((hour + 6) // 24)))[-2:]}T{("0" + str((hour + 6) % 24))[-2:]}:00:00'
        response = requests.get(url)

        if response.status_code != 200:
            print('Error')
            response = requests.get(url)

        result = response.json()

        for page_num in range(result['pages']):
            url = url + f'&page={page_num}'
            page_response = requests.get(url)

            if page_response.status_code != 200:
                print('Error')
                page_response = requests.get(url)

            for vacancy in page_response.json()['items']:
                df.loc[len(df.index)] = json_convert(vacancy)

    df.to_csv('hh_vacancies.csv', index=False)


get_vacancies()
