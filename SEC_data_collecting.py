import time
import os

from selenium import webdriver
from bs4 import BeautifulSoup
from mysql.connector import Error

from links_db_writing import create_connection_mysql_db
from config import db_config



def corp_ticker_selection(limit_num=0):

    # Возвращает ticker компании из таблицы corp_links, с заданным лимитом, по умолчанию лимита нет.


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
            SELECT ticker FROM corp_links
            WHERE market_country = "USA"
            {};
            '''.format(limit)
        cursor.execute(select_links)
        query_result = cursor.fetchall()

    except Error as error:
        return error

    finally:
        connection.close()
        cursor.close()

    return query_result


def sec_report_collector(ticker_list):

    # Принимает список тикеров и возвращает массив данных с сайта sec.report


    geck_path = os.path.join("C:\\", "Users", "VASidorov", "YandexDisk", "наука", "Коды", "geckodriver.exe")
    driver = webdriver.Firefox(executable_path=geck_path)

    try:
        sec_reports = []
        for ticker in ticker_list:

            sec_report = []
            sec_report.append(ticker[0])

            driver.get('https://sec.report/Ticker/{}'.format(ticker[0]))
            pageSource = driver.page_source
            soup = BeautifulSoup(pageSource, "html.parser")

            #Central Index Key
            h2 = soup.find('h2').get_text()
            cik = h2.split(' ')
            sec_report.append(cik[2])

            #Standard Industrial Classification
            sic = soup.find("td", text="SIC").find_next_sibling()
            sic = sic.get_text()
            sec_report.append(sic)


            sector = soup.find("td", text="Sector").find_next_sibling()
            sector = sector.get_text()
            sec_report.append(sector)

            industry = soup.find("td", text="Industry").find_next_sibling()
            industry = industry.get_text()
            sec_report.append(industry)

            corp_desc = soup.find("div", class_="panel-body").find("p").find_next_sibling()
            corp_desc = corp_desc.get_text()
            sec_report.append(corp_desc)

            sec_reports.append(sec_report)
            time.sleep(3)

    finally:
        driver.quit()

    return sec_reports


def sec_report_writer(sec_reports):
    # Принимает: массив данных с сайта sec.report.
    # Записывает в таблицу corp_links.

    connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                            db_config["mysql"]["user"],
                                            db_config["mysql"]["pass"],
                                            "corp_db")
    try:
        cursor = connection.cursor()

        for sec_report in sec_reports:
            sec_report_to_corp_links_writer = '''
            UPDATE corp_links
            SET
            sec_cik = "{}",
            sik = "{}",
            sector = "{}",
            industry = "{}",
            corp_desc = "{}"
            WHERE ticker = "{}";
            '''.format(*sec_report[1:7],sec_report[0])

            cursor.execute(sec_report_to_corp_links_writer)
            connection.commit()

    except Error as error:
        return error