from links_db_writing import create_connection_mysql_db
from mysql.connector import Error
from config import db_config
from growth_finder import asc_growth_finder

connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                        db_config["mysql"]["user"],
                                        db_config["mysql"]["pass"],
                                        "corp_db")
    #TODO Пока работает вне зависимости от признака отчетности - квартальная или годовая.
    # В будущем нужно будет добавить признак Q или Y в регистр с отчетностями. Особенно если пойдут смешанные отчеты, тогда сломается
try:
    cursor = connection.cursor()

    select_corps_without_fs = '''
    SELECT corp_id, url FROM corp_links
    WHERE EXISTS
    (SELECT corp_id FROM fs_reg
    WHERE corp_links.corp_id = fs_reg.corp_id
    GROUP BY fs_reg.corp_id);
    '''
    cursor.execute(select_corps_without_fs)
    corps = cursor.fetchall()

    for corp in corps:
        corp_id = corp[0]
        select_fs_by_corp = '''
            SELECT fs.year, fs.revenue, fs.income, fs.assets, fs.equity
            FROM fs_reg AS fs
            WHERE corp_id = {}
            ORDER BY fs.year;
            '''.format(corp_id)
        cursor.execute(select_fs_by_corp)
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
                growth = "N"

        print(corp[1], growth)


except Error as error:
    print(error)
finally:
    cursor.close()
    connection.close()