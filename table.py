import csv
import re
import datetime
from prettytable import PrettyTable, ALL


class Salary:
    """
    Класс для описания зарплаты

    Attributes
    ----------
    currency_translation: str
        словарь языкового перевода денежных единиц

    currency_to_rub: str
        словарь перевода из валюты в рубли

    salary_from: str
        нижняя граница оклада

    salary_to: str
        верхняя граница оклада

    salary_gross: str
        до/после вычета налогов

    salary_currency: str
        валюта

    """
    currency_translation = {
        "AZN": "Манаты",
        "BYR": "Белорусские рубли",
        "EUR": "Евро",
        "GEL": "Грузинский лари",
        "KGS": "Киргизский сом",
        "KZT": "Тенге",
        "RUR": "Рубли",
        "UAH": "Гривны",
        "USD": "Доллары",
        "UZS": "Узбекский сум"
    }

    currency_to_rub = {
        "Манаты": 35.68,
        "Белорусские рубли": 23.91,
        "Евро": 59.90,
        "Грузинский лари": 21.74,
        "Киргизский сом": 0.76,
        "Тенге": 0.13,
        "Рубли": 1,
        "Гривны": 1.64,
        "Доллары": 60.66,
        "Узбекский сум": 0.0055
    }

    def __init__(self, salary_from: str, salary_to: str, salary_gross: str, salary_currency: str):
        """
        Инициализация обьекта
        :param salary_from: str
            нижняя граница зп
        :param salary_to: str
            верхняя граница зп
        :param salary_gross: str
            до/после вычета налогов
        :param salary_currency: str
            валюта
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = self.currency_translation[salary_currency]

    def print(self):
        """
        Приводит строку к выводу для печати
        :return: str
            отформатированная строка
        """
        return f"{'{0:,}'.format(int(float(self.salary_from))).replace(',', ' ')} -" \
               f" {'{0:,}'.format(int(float(self.salary_to))).replace(',', ' ')} ({self.salary_currency})" \
               f" ({'Без вычета' if self.salary_gross.lower() == 'true' else 'С вычетом'} налогов)"

    def average(self):
        """
        Считает среднее значение оклада
        :return: int
            среднее значение оклада: (нижняя граница оклада + верхняя граница оклада) / 2
        """
        return (int("".join(self.salary_from.split())) + int("".join(self.salary_to.split()))) // 2

    def to_compare(self):
        """
        Приводит строку к формату для сравнения
        :return: float
            Значение для сравнения
        """
        return ((int(float("".join(self.salary_from.split()))) + int(float("".join(self.salary_to.split())))) // 2) * \
            self.currency_to_rub[self.salary_currency]


class Vacancy:
    """
    Класс для описания вакансии

    Atributes
    ---------
    name : str
        название професии
    description : str
        описание
    key_skills : str[]
         навыки
    experience_id : str
        опыт работы
    premium : str
        премиум вакансия
    employer_name : str
        название компания
    salary : Salary
        зарплата
    area_name : str
        название региона
    published_at : str
        дата публикации
    experience_translated : dict
        словарь языкового перевода опыта работы
    experience_values : dict
        словать перевода опыта к значениям
    """

    experience_translated = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет"
    }

    experience_values = {
        "Нет опыта": 0,
        "От 1 года до 3 лет": 1,
        "От 3 до 6 лет": 2,
        "Более 6 лет": 3
    }

    def __init__(self, object_vacancy):
        """
        Инициализация объекта
        :param object_vacancy: dict
            словарь вакансии
        """

        self.name = object_vacancy['name'][0]
        self.description = object_vacancy['description'][0]
        self.key_skills = object_vacancy['key_skills']
        self.experience_id = self.experience_translated[object_vacancy['experience_id'][0]]
        self.premium = "Да" if object_vacancy['premium'][0].lower() == "true" else "Нет"
        self.employer_name = object_vacancy['employer_name'][0]
        self.salary = Salary(object_vacancy['salary_from'][0], object_vacancy['salary_to'][0],
                             object_vacancy['salary_gross'][0], object_vacancy['salary_currency'][0])
        self.area_name = object_vacancy['area_name'][0]
        self.published_at = ".".join(reversed(object_vacancy['published_at'][0][:10].split("-")))
            #datetime.datetime.strptime(object_vacancy['published_at'][0], '%Y-%m-%dT%H:%M:%S%z')

    def to_compare(self):
        """
        Приведение к виду для сравнения
        :return: int
            значение для сравнения
        """
        return self.experience_values[self.experience_id]


class DataSet:
    """
    Вакансии и название файла

    Atributes
    ---------
    file_name : str
        имя/полный путь файла
    vacancies_object : Vacancy[]
        список вакансий
    """
    def __init__(self, file_name: str, vacancies_objects: list):
        """
        инициализация объекта
        :param file_name: str
            имя файла
        :param vacancies_objects:
            список вакансий
        """
        self.file_name = file_name
        self.vacancies_objects = vacancies_objects

    def fill_vacancies(self):
        """
        читает csv файл и фильтрует его от html тегов,
        записывает итоговый результат в vacancies_objects
        """
        vacancies, list_naming = self.read_csv()
        self.vacancies_objects = self.csv_filer(vacancies, list_naming)

    def read_csv(self):
        """
        Считывает данные с csv файла
        :return: (str[], str[])
            значения(сами вакансии), заглавия(параметры)
        """
        list_naming = []
        vacancies = []
        with open(self.file_name, encoding='utf-8-sig') as file:
            file_reader = csv.reader(file, delimiter=",")
            flag = True
            for row in file_reader:
                if flag:
                    flag = not flag
                    list_naming = row
                else:
                    if "" in row or len(row) != len(list_naming):
                        continue
                    vacancies.append(row)
        if len(list_naming) == 0:
            print('Пустой файл')
            exit()
        if len(vacancies) == 0:
            print('Нет данных')
            exit()
        return vacancies, list_naming

    def csv_filer(self, vacs, list_naming):
        """
        Удаляет html теги и лишние пробелы из вакансий
        :param vacs: str
            вакансии
        :param list_naming: bool
            наименование
        :return: str
            преобразованные вакансии
        """
        vacancies = list()
        for row in vacs:
            current = {}
            for i in range(len(row)):
                current[list_naming[i]] = row[i].split('\n')
                for j in range(len(current[list_naming[i]])):
                    current[list_naming[i]][j] = " ".join(
                        re.sub(re.compile('<.*?>'), '', current[list_naming[i]][j]).split())
            vacancies.append(Vacancy(current))
        return vacancies


class InputConect:
    """
    Класс ввода и вывода

    Attributes
    ----------
    translated_fields: dict
        словарь языкового перевода полей
    table: PrettyTable
        таблица вакансий
    columns: str
        требуемые столбцы таблицы
    rows_count: str
        требуемый диапазон строк
    is_reversed_sort: str
        обратная сортировка(да/нет)
    sort_by: str
        требуемый параметр сортировки
    filter_by: str
        требуемый параметр фильтрации
    f_name: str
        имя файла
    """
    translated_fields = {
        "№": "№",
        "name": "Название",
        "description": "Описание",
        "key_skills": "Навыки",
        "experience_id": "Опыт работы",
        "premium": "Премиум-вакансия",
        "employer_name": "Компания",
        "salary": "Оклад",
        "area_name": "Название региона",
        "published_at": "Дата публикации вакансии",
        "t": "Идентификатор валюты оклада"
    }

    def __init__(self):
        """
        Инициализация объекта
        """
        self.table = None
        self.columns = None
        self.rows_count = None
        self.is_reversed_sort = None
        self.sort_by = None
        self.filter_by = None
        self.f_name = None

    def start_input(self):
        """
        Начало пользовательского ввода
        """
        self.f_name = input('Введите название файла: ')
        self.filter_by = input('Введите параметр фильтрации: ')
        self.sort_by = input('Введите параметр сортировки: ')
        self.is_reversed_sort = input('Обратный порядок сортировки (Да / Нет): ')
        self.rows_count = input('Введите диапазон вывода: ')
        self.columns = input('Введите требуемые столбцы: ')
        self.table = PrettyTable()
        self.table.field_names = (list(self.translated_fields.values())[0:10])

        if self.filter_by != '':
            if ": " not in self.filter_by:
                print('Формат ввода некорректен')
                exit()
            field_name = self.filter_by.split(': ')[0]
            if field_name not in self.translated_fields.values():
                print('Параметр поиска некорректен')
                exit()
        if self.sort_by != '' and \
                self.sort_by not in self.translated_fields.values():
            print('Параметр сортировки некорректен')
            exit()
        if self.is_reversed_sort != '' and \
                self.is_reversed_sort != 'Нет' and \
                self.is_reversed_sort != 'Да':
            print('Порядок сортировки задан некорректно')
            exit()

    def filter_vacancies(self, vacancies: list):
        """
        Фильтрация вакансий по параметру фильтрации
        :param vacancies: list
            список вакансий
        :return: list
            отфильтрованный список вакансий
        """
        result = list()
        if self.filter_by != '':
            for vacancy in vacancies:
                field_name = self.filter_by.split(': ')[0]
                value = self.filter_by.split(': ')[1]
                if field_name == "Название":
                    if value != vacancy.name:
                        continue
                elif field_name == 'Оклад':
                    value = int(value)
                    salary_from = int("".join(vacancy.salary.salary_from.split()))
                    salary_to = int("".join(vacancy.salary.salary_to.split()))
                    if value < salary_from or value > salary_to:
                        continue
                elif field_name == 'Идентификатор валюты оклада':
                    if vacancy.salary.salary_currency != value:
                        continue
                elif field_name == "Дата публикации вакансии":
                    if value != (".".join(reversed(str(vacancy.published_at.date()).split('-')))):
                        continue
                else:
                    flag = False
                    values = value.strip().split(', ')
                    for v in values:
                        field_name_translated = list(self.translated_fields.keys())[
                            list(self.translated_fields.values()).index(field_name)]
                        if v not in getattr(vacancy, field_name_translated):
                            flag = True
                            break
                    if flag:
                        continue
                result.append(vacancy)
        else:
            result = vacancies

        return result

    def sort_vacancies(self, vacancies: list):
        """
        Сортировка вакансий по требуемому параметру сортировки
        :param vacancies: list
            список вакансий
        :return: list
            отсортированный список вакансий
        """
        self.is_reversed_sort = True if self.is_reversed_sort == "Да" else False
        if self.sort_by == '':
            return vacancies
        if self.sort_by == 'Навыки':
            return sorted(vacancies, key=lambda x: len(x.key_skills), reverse=self.is_reversed_sort)
        elif self.sort_by == 'Оклад':
            return sorted(vacancies, key=lambda x: x.salary.to_compare(), reverse=self.is_reversed_sort)
        elif self.sort_by == 'Дата публикации вакансии':
            return sorted(vacancies, key=lambda x: x.published_at, reverse=self.is_reversed_sort)
        elif self.sort_by == 'Опыт работы':
            return sorted(vacancies, key=lambda x: x.to_compare(), reverse=self.is_reversed_sort)
        else:
            key = list(self.translated_fields.keys())[list(self.translated_fields.values()).index(self.sort_by)]
            return sorted(vacancies, key=lambda x: getattr(x, key), reverse=self.is_reversed_sort)

    def add_vacancies_to_table(self, vacancies: list):
        """
        Добавление вакансий в таблицу
        :param vacancies: list
            список ваканский
        """
        index = 1
        for vacancy in vacancies:
            current = []
            for key in list(self.translated_fields.keys())[1:10]:
                value = getattr(vacancy, key)
                adding = value
                if type(value) == datetime.datetime:
                    adding = (".".join(reversed(str(value.date()).split('-'))))
                elif type(value) == list:
                    adding = ("\n".join(value))
                elif type(value) == Salary:
                    adding = value.print()
                if type(value) != Salary and len(adding) > 100:
                    adding = adding[0:100] + "..."
                current.append(adding)
            self.table.add_row([index] + current)
            index += 1

    def print_table(self):
        """
        Печать таблицы
        """
        self.table.max_width = 20
        self.table.hrules = ALL
        self.table.align = 'l'

        table_range = self.rows_count.split()
        inputed_columns = [line for line in self.columns.split(", ") if line.strip() != '']
        columns = ["№"] + inputed_columns

        start_index = int(table_range[0]) - 1 if len(table_range) >= 1 else 0
        end_index = int(table_range[1]) - 1 if len(table_range) > 1 else len(self.table.rows)
        columns = self.table.field_names if len(columns) == 1 else columns

        if len(self.table.get_string().split('\n')) > 3:
            print(self.table.get_string(start=start_index, end=end_index, fields=columns))
        else:
            print('Ничего не найдено')


def get_table():
    """
    Собирает данные из csv файла, фильтрует и сортирует по заданным параметрам и печатает итоговую таблицу
    """
    inputer = InputConect()
    inputer.start_input()
    dataset = DataSet(inputer.f_name, list())
    dataset.fill_vacancies()
    filtered_vacs = inputer.filter_vacancies(dataset.vacancies_objects)
    sorted_vacs = inputer.sort_vacancies(filtered_vacs)
    inputer.add_vacancies_to_table(sorted_vacs)
    inputer.print_table()
