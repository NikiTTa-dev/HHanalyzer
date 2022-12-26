import pandas as pd
import requests

pd.set_option("display.max_columns", False)
pd.set_option("expand_frame_repr", False)


def get_currencies_from_csv(file="Data\\vacancies_dif_currencies.csv"):
    """
    Определяет частые валюты и даты от первой до последней вакансии
    :param file: str
    :return: (str[], str[])
        (валюты[], даты[])
    """
    df = pd.read_csv(file)
    df["published_at"] = ["/".join(x[:7].split("-")) for x in df["published_at"]]
    dates = set()
    for date in pd.unique(df["published_at"]):
        dates.add(date)
    dates = ["/".join(reversed(d.split("/"))) for d in sorted(dates)]

    df = df.groupby("salary_currency")
    currency_list = []
    for currency, data in df:
        if len(data) > 5000 and currency != "RUR":
            currency_list.append(currency)

    return currency_list, dates


def get_dates(first_date, second_date):
    """
    Составляет список дат от первой до последней
    :param first_date: str
    :param second_date: str
    :return: str[]
    """
    res = []
    for year in range(int(first_date[:4]), int(second_date[:4]) + 1):
        num = 1
        if str(year) == first_date[:4]:
            num = int(first_date[-2:])
        for month in range(num, 13):
            if len(str(month)) == 2:
                res.append(f"{month}/{year}")
            else:
                res.append(f"0{month}/{year}")
            if str(year) == second_date[:4] and (str(month) == second_date[-2:] or f"0{month}" == second_date[-2:]):
                break
    return res


def get_currencies_diff():
    """
    по данным ЦБ РФ составляет csv файл по месяцам и курсам валют
    """
    # currency, dates = get_currencies_and_dates()
    currency = ['BYR', 'USD', 'EUR', 'KZT', 'UAH']
    dates = get_dates("2003-01", "2022-12")
    res_df = pd.DataFrame(columns=['Date'] + currency)
    for date in dates:
        response = requests.get(f"https://www.cbr.ru/scripts/XML_daily.asp?date_req=01/{date}")
        df_cur = pd.read_xml(response.text)
        lst = ["-".join(reversed(date.split("/")))]
        for cur in currency:
            if cur == 'BYR':
                record_cur = df_cur.loc[df_cur["CharCode"].isin(['BYN', cur])]
            else:
                record_cur = df_cur.loc[df_cur["CharCode"] == cur]
            lst.append(float(record_cur["Value"].values[0].replace(',', '.')) / float(record_cur["Nominal"].values[0]))

        res_df.loc[len(res_df.index)] = lst

    res_df.to_csv("currencies.csv", index=False)
    print(res_df.head())


get_currencies_diff()
