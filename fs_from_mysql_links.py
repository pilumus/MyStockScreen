import mysql.connector
from mysql.connector import Error
from selenium import webdriver
from bs4 import BeautifulSoup
from config import db_config
from math import floor as f
from help_functions import fs_year_prep
import time, os

geck_path = os.path.join("C:\\", "Users", "VASidorov", "YandexDisk", "наука", "Коды", "geckodriver.exe")
driver = webdriver.Firefox(executable_path=geck_path)


def create_connection_mysql_db(db_host, user_name, user_password, db_name=None):
    connection_db = None
    try:
        connection_db = mysql.connector.connect(
            host=db_host,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Подключение к MySQL успешно выполнено")
    except Error as db_connection_error:
        print("Возникла ошибка: ", db_connection_error)
    return connection_db


connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                        db_config["mysql"]["user"],
                                        db_config["mysql"]["pass"],
                                        "corp_db")

try:
    cursor = connection.cursor()
    select_links_by_country = '''
        SELECT corp_id, url FROM corp_links
        LIMIT 5;
        '''
    cursor.execute(select_links_by_country)
    query_result = cursor.fetchall()

    for link in query_result:
        corp_parameters = []

        driver.get(link[1] + "-financial-summary")
        time.sleep(3)

        try:
            cheese = driver.find_element_by_class_name("toggleButton").click()
        except:
            print("No Annual click in {}".format(link[1]))
        time.sleep(2)
        pageSource = driver.page_source

        soup = BeautifulSoup(pageSource, "html.parser")
        table = soup.find("div", id="rsdiv")


        for th in table.find("th", text="Period Ending:").parent.findAll("th", class_=""):
            th = th.get_text()
            corp_parameters.append(th)

        for td in table.find("td", text="Total Revenue").parent.findAll("td", class_=""):
            td = td.get_text()
            td = f(float(td))
            corp_parameters.append(td)

        for td in table.find("td", text="Net Income").parent.findAll("td", class_=""):
            td = td.get_text()
            td = f(float(td))
            corp_parameters.append(td)

        for td in table.find("td", text="Total Assets").parent.findAll("td", class_=""):
            td = td.get_text()
            td = f(float(td))
            corp_parameters.append(td)

        for td in table.find("td", text="Total Equity").parent.findAll("td", class_=""):
            td = td.get_text()
            td = f(float(td))
            corp_parameters.append(td)

        corp_statements = fs_year_prep(corp_parameters)

        for statement in corp_statements:

            update_fs_reg_with_fs_year ='''
                INSERT INTO fs_reg 
                (corp_id, year, revenue, income, assets, equity)
                VALUES
                ("{}", "{}", "{}", "{}", "{}", "{}");'''.format(link[0], *statement)

            print(update_fs_reg_with_fs_year)

            # cursor.execute(update_fs_reg_with_fs_year)
            # connection.commit()

except Error as error:
    print(error)

finally:
    cursor.close()
    connection.close()
    driver.quit()