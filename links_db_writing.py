import mysql.connector, csv
from mysql.connector import Error
from config import db_config


#
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

# cursor = connection.cursor()
# create_db_sql_query = 'CREATE DATABASE {};'.format("corp_db")
# cursor.execute(create_db_sql_query)
# cursor.close()
# connection.close()

try:
    # создание таблицы (Не забудь запятую после названия колонки)
    cursor = connection.cursor()
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS corp_links (
    url_id INT AUTO_INCREMENT,
    url VARCHAR(255) NOT NULL,
    market_country VARCHAR (20),
    PRIMARY KEY (url_id)
    );'''
    cursor.execute(create_table_query)
    connection.commit()

    csv_list = open("corplinks_list.csv", "r")
    corplinks_list = csv.reader(csv_list, delimiter=",")

    for link in corplinks_list:
        if len(link) > 0:
            cursor = connection.cursor()
            insert_corp_links_table_query = '''
                    INSERT INTO corp_links (url, market_country)
                    VALUES
                    ("{}", "USA");'''.format(link[0])
            # print(insert_corp_links_table_query)
            cursor.execute(insert_corp_links_table_query)
            # connection.next_result()
            connection.commit()

    # вставка данных в таблицу

    #
    # # изблечение данных из бд
    # select_users_female_query = '''
    #     SELECT name, age, nationality FROM users WHERE gender = 'female';
    #     '''
    # cursor.execute(select_users_female_query)
    # query_result = cursor.fetchall()
    # for user in query_result:
    #     print(user)

# except Error as error:
#     print(error)
finally:
    csv_list.close()
    cursor.close()
    connection.close()