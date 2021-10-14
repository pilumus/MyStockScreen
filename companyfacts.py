import json

from config import driver

def cik_parameters_list_from_sec(cik_list, key_list):
    """
    Принимает:
     - список CIK: Central Index Key
     - key_list: список показателей отчетности- ключей к словарям. key_list должен содержать
       показатели в нужном порядке.

    Возвращает:
     - таблицу cik / parameters, где parameters - список из ключа и данных словаря из json-файла, ключами к которым служат
    нужные показатели отчетности из key_list.
    """

    dr = driver
    try:
        cik_parameters_list = []
        for cik in cik_list:
            cik_parameters = []
            cik_parameters.append(cik)
            url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
            dr.get(url)
            text_tag = dr.find_element_by_id("json").text
            json_data = json.loads(text_tag)

            for key in key_list:
                parameter = []
                parameter_data = json_data['facts']['us-gaap'][key]
                parameter.append(key)
                parameter.append(parameter_data)
                cik_parameters.append(parameter)


            cik_parameters_list.append(cik_parameters)

    finally:
        dr.close()

    return cik_parameters_list

def unpack_fs_from_cik_parameters_list(cik_parameters_list,
                           balance_sheet_keys,
                           operating_keys, revenue_keys):
    """
    Вытаскивает из списка параметра и его данных показатель, дату отчета и сумму

    Принимает:
     - cik_parameters_list: Список CIK и списков ключ - данные
     - list показателей(key) balance sheet: Ключи с паттерном словаря, как у Assets, Equity
     - list показателей(key) operating: Ключи с паттерном словаря, как у Revenue, Net Income
     - revenue_keys: исторический и актуальный показатель выручки

    Возвращает:
     - таблицу cik / key-date-value
    """

    for corp_data in cik_parameters_list:
        cik_key_date_value_list = []
        cik_key_date_value_list.append(corp_data[0])

        for parameter in corp_data[1:len(corp_data)+1]:

            if parameter[0] in balance_sheet_keys:
                key_date_value_list = []
                USD = (parameter[1])['units']['USD']
                for num in USD:
                    if num['fp'] == 'FY' \
                    and num['form'] == '10-K' \
                    and 'frame' not in num \
                    and str(num['fy']) in num['end']:

                        key_date_value = []
                        key_date_value.append(parameter[0])
                        key_date_value.append(num['end'])
                        key_date_value.append(num['val'])
                        key_date_value_list.append(key_date_value)

                cik_key_date_value_list.append(key_date_value_list)

            if parameter[0] in operating_keys:
                key_date_value_list = []
                USD = (parameter[1])['units']['USD']
                for num in USD:
                    if 'frame' in num and not 'Q' in num['frame']:

                        key_date_value = []

                        if parameter[0] in revenue_keys:
                            key_date_value.append("Revenue")
                        else:
                            key_date_value.append(parameter[0])

                        key_date_value.append(num['end'])
                        key_date_value.append(num['val'])
                        key_date_value_list.append(key_date_value)

                cik_key_date_value_list.append(key_date_value_list)

    return cik_key_date_value_list

balance_sheet_keys = ['Assets',
                      'StockholdersEquity']

operating_keys = ['SalesRevenueNet',
                  'RevenueFromContractWithCustomerExcludingAssessedTax',
                  'NetIncomeLoss']

revenue_keys = ['SalesRevenueNet', 'RevenueFromContractWithCustomerExcludingAssessedTax']

keys = operating_keys + balance_sheet_keys
cik = ["0001018724"]
cik_parameters_list = cik_parameters_list_from_sec(cik, keys)

result = unpack_fs_from_cik_parameters_list(cik_parameters_list,
                                            balance_sheet_keys,
                                            operating_keys,
                                            revenue_keys)



