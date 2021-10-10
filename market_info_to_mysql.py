from links_db_writing import create_connection_mysql_db
from mysql.connector import Error
from config import db_config
from selenium import webdriver
from bs4 import BeautifulSoup
from help_functions import ticker_splt, name_splt, market_cap_int, na_check, shares_convert, date_convert, div_perc_split
from datetime import datetime
import time, os

#Возвращает id и url компании из таблицы corp_links, с заданным лимитом, по умолчанию лимита нет.
def corp_links_selection(limit_num=0):

    connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                            db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"],
                                            "corp_db")
    if limit_num == 0:
        limit = ''
    else:
        limit = 'LIMIT {}'.format(limit_num)

    try:
        cursor = connection.cursor()
        select_links = '''
            SELECT corp_id, url FROM corp_links {};
            '''.format(limit)
        cursor.execute(select_links)
        query_result = cursor.fetchall()

    except Error as error:
        return error

    finally:
        connection.close()
        cursor.close()

    return query_result

#Принимает список id и url, возвращает список рыночной информации
def market_info_collecting(query_result):
    try:
        geck_path = os.path.join("C:\\", "Users", "VASidorov", "YandexDisk", "наука", "Коды", "geckodriver.exe")
        driver = webdriver.Firefox(executable_path=geck_path)

        market_info_list =[]
        for link in query_result:
            market_info = []

            # Собираем данные с основной страницы и добавляем в лист
            driver.get(link[1])
            time.sleep(3)
            pageSource = driver.page_source

            # А это - создание экземпляра класса Beautiful Soup
            soup = BeautifulSoup(pageSource, "html.parser")
            # делаем переменную table, чтобы сократить время и ресурсы на итерацию
            table = soup.find("div", class_="instrument-page_instrument-page__2xiQP relative")

            market_info.append(link[0])

            # Эти 2 показателя в таблицу corp_links
            name_ticker = table.find("h1", class_="text-2xl font-semibold instrument-header_title__GTWDv mobile:mb-2").get_text()
            market_info.append(name_splt(name_ticker))
            market_info.append(ticker_splt(name_ticker))

            #Дата и время сбора инфы query_date

            market_info.append(datetime.strptime(time.asctime(), '%a %b  %d %X %Y'))

            # Показатели ниже в market_info
            market_cap = table.find("dt", text="Market Cap").parent.find("span", class_="key-info_dd-numeric__2cYjc").get_text()
            market_info.append(market_cap_int(market_cap))

            pe_ratio = table.find("dt", text="P/E Ratio").parent.find("span", class_="key-info_dd-numeric__2cYjc").get_text()
            market_info.append(na_check(pe_ratio))

            eps = table.find("dt", text="EPS").parent.find("span", class_="key-info_dd-numeric__2cYjc").get_text()
            market_info.append(na_check(eps))

            div_nominal = table.find("dt", text="Dividend (Yield)").parent.find("div", class_="flex").get_text()
            div_nominal = div_nominal.split('(')
            market_info.append(na_check(div_nominal[0]))

            div_percent = table.find("dt", text="Dividend (Yield)").parent.find("div", class_="ml-1").get_text()
            div_percent = div_perc_split(div_percent)
            market_info.append(na_check(div_percent))

            shares = table.find("dt", text="Shares Outstanding").parent.find("span",
                                                                               class_="key-info_dd-numeric__2cYjc").get_text()
            market_info.append(shares_convert(shares))

            next_earnings_date = table.find("dt", text="Next Earnings Date").parent.find("a").get_text()
            if "N/A" in next_earnings_date:
                market_info.append(na_check(next_earnings_date))
            else:
                next_earnings_date = date_convert(next_earnings_date)
                next_earnings_date = str(next_earnings_date)
                next_earnings_date = next_earnings_date.split(' ')
                market_info.append("'" + next_earnings_date[0] + "'")

            market_info_list.append(market_info)

    finally:
        driver.quit()

    return market_info_list

#Принимает список рыночной информации, обновляет таблицу corp_links названием и тикером
def db_write_nameticker(market_info_collection):

    connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                            db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"],
                                            "corp_db")
    cursor = connection.cursor()
    try:
        for market_info in market_info_collection:

            nameticker_inserter = '''
            UPDATE corp_links
            SET
            corp_name = "{}",
            ticker = "{}"
            WHERE corp_id = {};
            '''.format(market_info[1], market_info[2], market_info[0])

            cursor.execute(nameticker_inserter)
            connection.commit()

    except Error as error:
        return error

#Принимает список рыночной информации, добавляет записи регистра market_info
def db_write_market_info(market_info_collection):

    connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                            db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"],
                                            "corp_db")
    cursor = connection.cursor()
    try:
        for market_info in market_info_collection:

            market_info_inserter = '''
            INSERT INTO market_info
            (corp_id, query_date, market_cap, pe_ratio, eps, div_nominal, div_percent, shares_outstanding, next_earnings_date)
            VALUES
            ("{}", "{}", {}, {}, {}, {}, {}, {}, {});
            '''.format(market_info[0], *market_info[3:11])

            cursor.execute(market_info_inserter)
            connection.commit()

    except Error as error:
        return error


links = corp_links_selection(5)

mi_list = market_info_collecting(links)

x = db_write_market_info(mi_list)
print(x)