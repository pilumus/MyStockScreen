import statistics

def growth_finder(massive):
    try:
        #Проверяет, есть ли в массиве отрицательные числа
        result = True
        for digits in massive:
            if float(digits) < 0:
                result = False
    except ValueError:
        return "ValueError1 {}".format(digits)

    #Считает среднее арифметическое роста показателя
    try:
        diff_list = []
        if result == True:
            for digit in massive[0:len(massive)-1]:
                n = massive.index(digit)
                diff = float(digit) - float(massive[n + 1])
                diff_list.append(diff)
        else:
            return False

        result = statistics.mean(diff_list)
        return result
    except ValueError:
        return "ValueError2 {}".format(digit)
