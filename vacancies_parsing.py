import pandas as pd

pd.set_option("display.max_columns", False)
pd.set_option("expand_frame_repr", False)


def parse_csv_by_year(file="Data\\vacancies_by_year.csv"):
    """
    Группирует данные во входном файле по годам(разделяет на более мелкие)
    :param file: str
    """
    df = pd.read_csv(file)
    df["year"] = df["published_at"].apply(lambda s: s[:4])
    df = df.groupby("year")
    for year, data in df:
        data[["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"]].to_csv(
            rf"Csvs\year_{year}.csv", index=False)


parse_csv_by_year()
