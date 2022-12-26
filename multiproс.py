import multiprocessing
import cProfile
import os
import pandas as pd
import vacancies_parsing
import concurrent.futures as con_fut


class Statistic:
    def __init__(self, file: str, profession: str):
        """
        Инициализация объекта

        :param file: str
            путь к файлу с данными
        :param profession: str
            профессия, по которой будет составляться аналитика
        """
        self.file = file
        self.profession = profession
        self.years_salary = {}
        self.years_count = {}
        self.years_salary_vac = {}
        self.years_count_vac = {}
        self.area_salary = {}
        self.area_count = {}

    def get_stat(self):
        self.get_stat_by_year_multi_on()
        self.get_stat_by_city()

    def get_stat_by_year(self, file_csv):
        """
        Сосавляет статистику по году
        :param file_csv: str
            файл с данными за год
        :return: (str, [int, int, int, int])
            (год, [средняя зп, всего вакансий, средняя зп для профессии, вакансий по профессии])
        """

        df = pd.read_csv(file_csv)
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["published_at"] = df["published_at"].apply(lambda s: int(s[:4]))
        df_vac = df[df["name"].str.contains(self.profession)]

        return df["published_at"].values[0], [int(df["salary"].mean()), len(df),
                                              int(df_vac["salary"].mean() if len(df_vac) != 0 else 0), len(df_vac)]

    def get_stat_by_city(self):
        """
        Статистика по городам
        """
        df = pd.read_csv(self.file)
        total = len(df)
        df["salary"] = df[["salary_from", "salary_to"]].mean(axis=1)
        df["count"] = df.groupby("area_name")["area_name"].transform("count")
        df = df[df["count"] > total * 0.01]
        df = df.groupby("area_name", as_index=False)
        df = df[["salary", "count"]].mean().sort_values("salary", ascending=False)
        df["salary"] = df["salary"].apply(lambda s: int(s))

        self.area_salary = dict(zip(df.head(10)["area_name"], df.head(10)["salary"]))

        df = df.sort_values("count", ascending=False)
        df["count"] = round(df["count"] / total, 4)

        self.area_count = dict(zip(df.head(10)["area_name"], df.head(10)["count"]))

    def get_stat_by_year_multi_off(self):
        """
        Собирает статистику по годам, без мультипроцессорности
        """

        res = []
        for csv_file in os.listdir("Csvs"):
            with open(os.path.join("Csvs", csv_file), "r") as file_csv:
                res.append(self.get_stat_by_year(file_csv.name))

        for year, data_stat in res:
            self.years_salary[year] = data_stat[0]
            self.years_count[year] = data_stat[1]
            self.years_salary_vac[year] = data_stat[2]
            self.years_count_vac[year] = data_stat[3]

    def get_stat_by_year_multi_on(self):
        """
        Собирает статистику по годам, с использованием мультипроцессорности
        """
        csv_file = [rf"Csvs\{file_name}" for file_name in os.listdir("Csvs")]
        pool = multiprocessing.Pool(4)
        res = pool.starmap(self.get_stat_by_year, [(file,) for file in csv_file])
        pool.close()

        for year, data_stat in res:
            self.years_salary[year] = data_stat[0]
            self.years_count[year] = data_stat[1]
            self.years_salary_vac[year] = data_stat[2]
            self.years_count_vac[year] = data_stat[3]

    def get_stat_by_year_concurrent(self):
        """
        Собирает статистику по годам, с использованием модуля concurrent
        """
        csv_file = [rf"Csvs\{file_name}" for file_name in os.listdir("Csvs")]
        with con_fut.ProcessPoolExecutor(max_workers=4) as executor:
            res = executor.map(self.get_stat_by_year, csv_file)
        res = list(res)

        for year, data_stat in res:
            self.years_salary[year] = data_stat[0]
            self.years_count[year] = data_stat[1]
            self.years_salary_vac[year] = data_stat[2]
            self.years_count_vac[year] = data_stat[3]

    def print_stat(self):
        print(f"Динамика уровня зарплат по годам: {self.years_salary}")
        print(f"Динамика количества вакансий по годам: {self.years_count}")
        print(f"Динамика уровня зарплат по годам для выбранной профессии: {self.years_salary_vac}")
        print(f"Динамика количества вакансий по годам для выбранной профессии: {self.years_count_vac}")
        print(f"Уровень зарплат по городам (в порядке убывания): {self.area_salary}")
        print(f"Доля вакансий по городам (в порядке убывания): {self.area_count}")


if __name__ == '__main__':
    #file = input("Введите название файла: ")
    file_path = "Data/vacancies_by_year.csv"
    #profession = input("Введите название профессии: ")
    prof = "Аналитик"
    #vacancies_parsing.parse_csv_by_year(file_path)
    stat = Statistic(file_path, prof)
    stat.get_stat()
    stat.print_stat()
    #cProfile.run("stat.get_stat_by_year_multi_on()", sort="cumtime")
    #cProfile.run("stat.get_stat_by_year_multi_off()", sort="cumtime")
    #cProfile.run("stat.get_stat_by_year_concurrent()", sort="cumtime")
