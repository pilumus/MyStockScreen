from links_db_writing import create_connection_mysql_db
from mysql.connector import Error
from config import db_config
from selenium import webdriver
from bs4 import BeautifulSoup
from help_functions import ticker_splt, name_splt, market_cap_int, na_check, shares_convert, date_convert, div_perc_split
from datetime import datetime
import time, os




geck_path = os.path.join("C:\\", "Users", "VASidorov", "YandexDisk", "наука", "Коды", "geckodriver.exe")
driver = webdriver.Firefox(executable_path=geck_path)

connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                        db_config["mysql"]["user"],
                                        db_config["mysql"]["pass"],
                                        "corp_db")

try:
    cursor = connection.cursor()
    select_links = '''
        SELECT corp_id, url FROM corp_links
        LIMIT 5;
        '''
    cursor.execute(select_links)
    query_result = cursor.fetchall()

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

        # Преобразовать в дату
        next_earnings_date = table.find("dt", text="Next Earnings Date").parent.find("a").get_text()
        market_info.append(date_convert(next_earnings_date))

        print(market_info)

except Error as error:
    print(error)

finally:
    cursor.close()
    connection.close()
    driver.quit()