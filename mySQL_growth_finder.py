from links_db_writing import create_connection_mysql_db
from mysql.connector import Error
from config import db_config
from growth_finder import asc_growth_finder

connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                        db_config["mysql"]["user"],
                                        db_config["mysql"]["pass"],
                                        "corp_db")

try:
    cursor = connection.cursor()

    corp_id = 1
    select_links_by_country = '''
        SELECT fs.year, fs.revenue, fs.income, fs.assets, fs.equity
        FROM fs_reg AS fs
        WHERE corp_id = {}
        ORDER BY fs.year;
        '''.format(corp_id)
    cursor.execute(select_links_by_country)
    query_result = cursor.fetchall()

    # Считаем средние по каждому показателю отчетности, добавляем в список.
    # Показатели находятся в колонках 1-5
    means = []
    for fs_param in range(1, 5):
        params = []
        for fs in query_result:
            params.append(fs[fs_param])
        means.append (asc_growth_finder(params))

    growth = "Y"
    for mean in means:
        if mean < 0:
            growth = "N"git

    print(growth)


except Error as error:
    print(error)
finally:
    cursor.close()
    connection.close()