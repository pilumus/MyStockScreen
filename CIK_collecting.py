from selenium import webdriver
from bs4 import BeautifulSoup
import time, os

from links_db_writing import create_connection_mysql_db
from mysql.connector import Error
from config import db_config

#Возвращает ticker компании из таблицы corp_links, с заданным лимитом, по умолчанию лимита нет.
def corp_ticker_selection(limit_num=0):

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
            SELECT ticker FROM corp_links {};
            '''.format(limit)
        cursor.execute(select_links)
        query_result = cursor.fetchall()

    except Error as error:
        return error

    finally:
        connection.close()
        cursor.close()

    return query_result


#Принимает список тикеров и возвращает массив данных с сайта sec.report
def sec_report_collector(ticker_list):

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

            h2 = soup.find('h2').get_text()
            cik = h2.split(' ')
            sec_report.append(cik[2])

            sic = soup.find("td", text="SIC").find_next_sibling()
            sic = sic.get_text()
            sec_report.append(sic)


            sector = soup.find("td", text="Sector").find_next_sibling()
            sector = sector.get_text()
            sec_report.append(sector)

            industry = soup.find("td", text="Industry").find_next_sibling()
            industry = industry.get_text()
            sec_report.append(industry)

            desc = soup.find("div", class_="panel-body").find("p").find_next_sibling()
            desc = desc.get_text()
            sec_report.append(desc)

            sec_reports.append(sec_report)
            time.sleep(3)

    finally:
        driver.quit()

    return sec_reports
