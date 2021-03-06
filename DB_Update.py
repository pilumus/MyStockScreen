import mysql.connector, csv
from mysql.connector import Error
from config import db_config

def create_connection_mysql_db(db_host, user_name, user_password, db_name = None):
    connection_db = None
    try:
        connection_db = mysql.connector.connect(
            host = db_host,
            user = user_name,
            passwd = user_password,
            database = db_name
        )
        print("Подключение к MySQL успешно выполнено")
    except Error as db_connection_error:
        print("Возникла ошибка: ", db_connection_error)
    return connection_db

connection = create_connection_mysql_db(db_config["mysql"]["host"],
                                        db_config["mysql"]["user"],
                                        db_config["mysql"]["pass"],
                                        "corp_db")
#Ищет в базе ссылки с номером cid, вытаскивает их и кладет в столбец cid

try:
    cursor = connection.cursor()
    select_links_by_country = '''
        SELECT url FROM corp_links WHERE url LIKE '%?cid=%';
        '''
    cursor.execute(select_links_by_country)
    query_result = cursor.fetchall()
    for link in query_result:
        link_cid = link[0].split("?cid=")
        cid_num = (int(link_cid[1]), int(link_cid[1]))
        update_corp_links_with_cid = '''
        UPDATE corp_links
        SET cid = {}
        WHERE url LIKE '%{}';
        '''.format(*cid_num)
        cursor.execute(update_corp_links_with_cid)
        connection.commit()

except Error as error:
    print(error)
finally:
    cursor.close()
    connection.close()
    print("Done")