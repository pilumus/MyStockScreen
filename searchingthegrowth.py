import csv, math
from growth_finder import growth_finder

csv_corps = open("corp_parameters.csv", "r")
corps_financial = csv.reader(csv_corps, delimiter=",")

for corp in corps_financial:
    if len(corp)>0:
        if len(corp[9:25]) == 16:
            if "URL" in corp[0]:
                pass
            else:
                try:
                    corp_stats = []
                    corp_stats.append(corp[2])
                    #revenue
                    corp_stats.append(math.floor(growth_finder(corp[9: 13])))
                    #income
                    corp_stats.append(math.floor(growth_finder(corp[13: 17])))
                    #assets
                    corp_stats.append(math.floor(growth_finder(corp[17: 21])))
                    #capital
                    corp_stats.append(math.floor(growth_finder(corp[21: 25])))


                    if corp_stats[1] and corp_stats[2] and corp_stats[3] and corp_stats[4] > 0:
                        corp_stats.append(True)
                    else:
                        corp_stats.append(False)

                    print(corp_stats)

                except TypeError:
                    print ("{} Type Error".format(corp_stats))
        else:
            print("{} Not enough data".format(corp[2]))

