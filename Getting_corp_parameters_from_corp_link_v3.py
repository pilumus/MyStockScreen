from selenium import webdriver
from bs4 import BeautifulSoup
from help_functions import ticker_splt, name_splt, market_cap_int
from growth_finder import growth_finder
from math import floor as f
import time, os, csv, math

geck_path = os.path.join("C:\\", "Users", "VASidorov", "YandexDisk", "наука", "Коды", "geckodriver.exe")
driver = webdriver.Firefox(executable_path=geck_path)

# Открываем файлы
# Чтение списка ссылок из файла
#Если short_corplinks_list.csv
csv_list = open("corplinks_list.csv", "r")
corplinks_list = csv.reader(csv_list, delimiter=",")
# Запись показателей
csv_corps = open("corp_parameters.csv", "w")
corp_list = csv.writer(csv_corps, delimiter=",")

# Записываем шапку таблицы
corp_list.writerow(["URL", "Corp Name", "Ticker",
                    "Market Cap", "P/E Ratio * 100", "EPS", "Dividend (Yield)", "Shares Outstanding", "Next Earnings Date",
                    "Revenue Y4", "Revenue Y3", "Revenue Y2", "Revenue Y1",
                    "Income Y4", "Income Y3", "Income Y2", "Income Y1",
                    "Assets Y4", "Assets Y3", "Assets Y2", "Assets Y1",
                    "Equity Y4", "Equity Y3", "Equity Y2", "Equity Y1",
                    "Revenue Growth", "Income Growth", "Assets Growth", "Equity Growth",
                    "Growth Corp?"])

# Перебираем ссылки с компаниями
for link in corplinks_list:
    if len(link) > 0:
        corp_parameters = []

        # Собираем данные с основной страницы и добавляем в лист
        driver.get(link[0])
        time.sleep(3)
        pageSource = driver.page_source

        soup = BeautifulSoup(pageSource, "html.parser")
        table = soup.find("div", class_="overviewDataTableWithTooltip")

        corp_parameters.append(link[0])

        name_ticker = soup.find("h1", class_="text-2xl font-semibold instrument-header_title__GTWDv mobile:mb-2").get_text()
        print(name_ticker)
        corp_parameters.append(name_splt(name_ticker))
        corp_parameters.append(ticker_splt(name_ticker))

        market_cap = table.find("span", text="Market Cap").parent.find("span", class_="float_lang_base_2").get_text()
        try:
            corp_parameters.append(market_cap_int(market_cap))
        except ValueError:
            print("{} MarketCap Value Error".format(corp_parameters[2]))
            corp_parameters.append(market_cap)

        p_e = table.find("span", text="P/E Ratio").parent.find("span", class_="float_lang_base_2").get_text()
        try:
            p_e = float(p_e) * 100
            p_e = int(p_e)
        except ValueError:
            pass

        corp_parameters.append(p_e)

        eps = table.find("span", text="EPS").parent.find("span", class_="float_lang_base_2").get_text()
        corp_parameters.append(eps)

        divs = table.find("span", text="Dividend (Yield)").parent.find("span", class_="float_lang_base_2").get_text()
        corp_parameters.append(divs)

        shares = table.find("span", text="Shares Outstanding").parent.find("span",
                                                                           class_="float_lang_base_2").get_text()
        corp_parameters.append(shares)

        next_earnings_date = table.find("span", text="Next Earnings Date").parent.find("span",
                                                                                       class_="float_lang_base_2").get_text()
        corp_parameters.append(next_earnings_date)

        # Собираем финансовые показатели со страницы фин. отчетности
        driver.get(link[0] + "-financial-summary")
        time.sleep(3)
        try:
            try:
                cheese = driver.find_element_by_class_name("toggleButton").click()
            except:
                print("No Annual click in {}".format(corp_parameters[2]))
            pageSource = driver.page_source

            soup = BeautifulSoup(pageSource, "html.parser")
            table = soup.find("div", id="rsdiv")

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

            # Проверяем показатели на рост
            if len(corp_parameters[9:25]) == 16:
                try:
                    corp_stats = []
                    corp_stats.append(corp_parameters[2])
                    # revenue
                    corp_parameters.append(math.floor(growth_finder(corp_parameters[9: 13])))
                    # income
                    corp_parameters.append(math.floor(growth_finder(corp_parameters[13: 17])))
                    # assets
                    corp_parameters.append(math.floor(growth_finder(corp_parameters[17: 21])))
                    # capital
                    corp_parameters.append(math.floor(growth_finder(corp_parameters[21: 25])))

                    if corp_parameters[25] > 0 and corp_parameters[26] > 0 and corp_parameters[27] > 0 and corp_parameters[28] > 0:
                        corp_parameters.append(True)
                    else:
                        corp_parameters.append(False)

                except TypeError:
                    corp_parameters.append("Type Error")
            else:
                corp_parameters.append("Not enough data")
                print("{} Not enough data".format(corp_parameters[2]))

        except AttributeError:
            print("{} Attribute Error".format(corp_parameters[2]))
            continue

        except:
            print("Unknown error with {}".format(corp_parameters[2]))
            continue

        finally:
            corp_list.writerow(corp_parameters)
            continue

csv_list.close()
csv_corps.close()

driver.quit()
print("Done")
