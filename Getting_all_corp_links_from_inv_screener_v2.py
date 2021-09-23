from selenium import webdriver
from bs4 import BeautifulSoup
import time, os, csv

geck_path = os.path.join("C:\\", "Users", "VASidorov", "YandexDisk", "наука", "Коды", "geckodriver.exe")

driver = webdriver.Firefox(executable_path=geck_path)

#RUS - 56
#USA - 5
main_link ="https://www.investing.com/stock-screener/?sp=country::5|sector::a|industry::a|equityType::a%3Ceq_market_cap;"
url_1 = "https://www.investing.com"

csv_list = open("demo_corplinks_list.csv", "w")
row = csv.writer(csv_list, delimiter=",")

try:
    for n in range(1, 8):
        n = str(n)
        link = main_link+n
        driver.get(link)
        time.sleep(3)
        pageSource = driver.page_source

        soup = BeautifulSoup(pageSource, "html.parser")
        table = soup.find("table", class_="resultsStockScreenerTbl").tbody

        for tr in table.findAll("tr"):
            OTC = False
            for td in tr.findAll("td"):
                if "OTC Markets" in td.get_text():
                    OTC = True
            if OTC == False:
                url_2 = tr.find("a").get("href")
                url = url_1+url_2
                l = []
                l.append(url)
                row.writerow(l)
finally:
    driver.quit()

csv_list.close()
print("Done")

