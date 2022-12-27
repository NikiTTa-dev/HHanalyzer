import csv
import pandas as pd


def concat_salary(vacancies_count, file="Data\\vacancies_dif_currencies.csv"):
    currency_rates = pd.read_csv("currencies.csv")
    with open(file, "r", encoding="utf_8_sig") as file_read:
        with open("processed_vacancies.csv", "w", encoding="utf_8", newline='') as file_write:
            reader = csv.reader(file_read)
            writer = csv.writer(file_write)
            writer.writerow(["name", "salary", "area_name", "published_at"])
            reader.__next__()
            for i, x in enumerate(reader):
                salary = get_salary(x[1], x[2], x[3], x[5], currency_rates)
                writer.writerow([x[0], salary, x[4], x[5]])
                if i == vacancies_count - 1:
                    break

            
def get_salary(salary_from, salary_to, currency, date, currency_rates):
    salary = float(salary_from) if salary_from != "" else 0
    salary += float(salary_to) if salary_to != "" else 0
    k = 1
    if currency != "RUR" and currency in currency_rates.columns:
        k = currency_rates[currency_rates["Date"] == date[:7]][currency].values[0]
    return "" if salary == 0 or currency not in currency_rates.columns else float(round(salary * k))
