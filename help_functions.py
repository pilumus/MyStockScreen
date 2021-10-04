#Разделяют тикер и название компании из строки с инвестинга

def ticker_splt(n_t):
    n_t_list = n_t.split("(")
    tickerlist = n_t_list[1].split(")")
    ticker = tickerlist[0]

    return ticker

def name_splt(name_ticker):
    n_t_list = name_ticker.split("(")

    corp_name =""
    corp_name_list = []

    for letter in n_t_list[0]:
        corp_name_list.append(letter)

    corp_name_list.pop()

    for list_letter in corp_name_list:
        corp_name = corp_name+list_letter

    return corp_name

#Удаляет number букв с конца строки
def del_right_letters(string, number):
    corp_name =""
    corp_name_list = []

    for letter in string:
        corp_name_list.append(letter)

    for corp_name_list_deleting in range(0, number):
        corp_name_list.pop()

    for list_letter in corp_name_list:
        corp_name = corp_name+list_letter

    return corp_name

#Выражает капитализацию в миллионах $
def market_cap_int(market_cap_str):
    if "T" in market_cap_str:
        mc_int = del_right_letters(market_cap_str, 1)
        mc_int = float(mc_int)
        mc_int = mc_int*1000000
        mc_int = int(mc_int)

    if "B" in market_cap_str:
        mc_int = del_right_letters(market_cap_str, 1)
        mc_int = float(mc_int)
        mc_int = mc_int*1000
        mc_int = int(mc_int)

    if "M" in market_cap_str:
        mc_int = del_right_letters(market_cap_str, 3)
        mc_int = int(mc_int)

    else:
        return market_cap_str
        
    return mc_int


# Перебираем полученные параметры и готовим список строк для записи в регистр
# На вход список сырых параметров, на выход список списков

def fs_year_prep(corp_parameters):

    if len(corp_parameters) == 20:
        j_max = 4
    elif len(corp_parameters) == 15:
        j_max = 3

    corp_statements = []

    for j in range(0, j_max):
        i = j
        fs_year = []
        for cycle in range(0, 5):
            fs_year.append(corp_parameters[i])
            i = i + 4

        corp_statements.append(fs_year)

    return corp_statements