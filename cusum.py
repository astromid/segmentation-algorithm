# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 23:09:58 2015

@author: Yan
"""

import numpy as np

#параметры авторегрессионных моделей
#{выкинуты числа, ответственные за влияние шума}
#phi0 = [0,  1.36,  -0.49]
#phi1 = [0,  1.02,  -0.40]
phi0 = [0, 0.7777, 0.0, 0.2310, -0.1882, 0.1078, -0.1709, 0.0579, -0.1004, 0.095, 0.0]
phi1 = [0, 1.5754, -1.9375, 1.8763, -1.5303, 1.1594, -0.9269, 0.5768, -0.4746, 0.1396, -0.1132]
#phi2 = [0,  0.82,  -0.49]
#phi3 = [0,  0,     -0.49]
#phi4 = [0, -0.82,  -0.49]
#phi = np.array([phi0,phi1,phi2,phi3,phi4])
phi = np.array([phi0,phi1])
#del phi0, phi1, phi2, phi3, phi4                             #они больше не нужны
del phi0, phi1

n = 10                                                       #порядок авторегрессии
m = 2                                                        #количество различных классов{моделей}

data = open('signal_simple_paper_cropped_3.txt', 'r')                      #не забыть, что первые 2 числа - рандом! индексы 0, 1
x = [float(line.strip()) for line in data]                  #считывание отсчетов из файла
data.close()

def g_t(g_t1, i, j, t):                                     #расчет кумулятивных сумм
#g_t1 - предыдущее значение g_t для данных i,j; переход i -> j, t - текущий отсчет
    summ_i = phi[i][0]
    summ_j = phi[j][0]
    for v in range(1,n+1):                                  #считаем суммы
        summ_i += phi[i][v]*x[t-v]
        summ_j += phi[j][v]*x[t-v]
    L = (x[t] - summ_i)**2 - (x[t] - summ_j)**2
    g = np.max([0, g_t1 + L])
    return g                                                #возвращаем рассчитанное значение
    
g_t0 = np.zeros((m,m))                                      #начальная матрица g_t
T = np.zeros((m,m))                                         #матрица граничных условий

for i in range(0,m):                                        #заполняем граничные условия
    for j in range(0,m):
        T[i][j] = 4000000

H = np.zeros(len(x))                                        #искомая сегментация
first_break_flag = False
segmentation = open('segmentation_cusum.txt', 'w')
for t in range(n, len(x)):                                  #главный цикл, начинаем с n т.к. 0,1 - рандом
#двойной цикл поиска первого момента разладки, потом - фиксированные переходы
    if(first_break_flag == False):
        for i in range(0,m):                                    #запускаем цепочку кумулятивных сумм
            for j in range(0,m):
                if(i == j):                                     #если i = j, идем дальше - это не нужно
                    continue
                g_t0[i][j] = g_t(g_t0[i][j], i, j, t)           #считаем кумулятивную сумму
                if(g_t0[i][j] >= T[i][j]):                      #если она превысила границу, мы нашли переход
                    H[t - 1] = i
                    H[t] = j
                    H_curr = j
                    first_break_flag = True
                    g_t0 = np.zeros((m,m))                      #обнуляем кумулятивные суммы
                    segmentation.write(str(t-n) + ' '+ str(i) + '\n')   #t-n - сдвиг из-за первых n рандомных знач.
                    segmentation.write(str(t-n) + ' '+ str(j) + '\n')
                    break
            if(first_break_flag == True):
                break
    else:                                                       #если первый переход уже найден:
        for j in range(0,m):
            if(H_curr == j):
                continue                                        #пропускаем проверку перехода на самого себя
            g_t0[H_curr][j] = g_t(g_t0[H_curr][j], H_curr, j, t) #считаем кумулятивную сумму
            if(g_t0[H_curr][j] >= T[H_curr][j]):
                H[t] = j
                g_t0 = np.zeros((m,m))                          #обнуляем кумулятивные суммы
                segmentation.write(str(t-n) + ' ' + str(H_curr) + '\n')
                segmentation.write(str(t-n) + ' ' + str(j) + '\n')
                H_curr = j
                break
            else:
                H[t] = H_curr
H = np.delete(H, [0,n])                                             #обрезаем первые n элементов
segmentation.write(str(t-2) + ' ' + str(H_curr) + '\n')
segmentation.close()
print('ALL DONE!')