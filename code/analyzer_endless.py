# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:58:35 2015

@author: Yan
"""

import numpy as np

repers = open('repers_endless.txt', 'w')                     #создание файла
repers.close()
segmentation = open('segmentation_endless.txt', 'w')
segmentation.close()
output = open('output_endless.txt', 'w')
output.close()

phi0 = [0,  1.36,  -0.49, 1.0]                              #параметры авторегрессионных моделей
phi1 = [0,  1.02,  -0.40, 1.0]                              #последнее число - параметр B, определяющий
phi2 = [0,  0.82,  -0.49, 1.0]                              #                      степень влияния шума
phi3 = [0,  0,     -0.49, 1.0]
phi4 = [0, -0.82,  -0.49, 1.0]
phi = np.array([phi0,phi1,phi2,phi3,phi4])
del phi0, phi1, phi2, phi3, phi4                             #они больше не нужны

n = 2                                                        #порядок авторегрессии
m = 5                                                        #количество различных классов{моделей}

q1 = [0.99,   0.0025, 0.0025, 0.0025, 0.0025]
q2 = [0.0025, 0.99,   0.0025, 0.0025, 0.0025]
q3 = [0.0025, 0.0025, 0.99,   0.0025, 0.0025]
q4 = [0.0025, 0.0025, 0.0025, 0.99,   0.0025]
q5 = [0.0025, 0.0025, 0.0025, 0.0025, 0.99]
Q = np.array([q1,q2,q3,q4,q5])                              #матрица вер-ти переходов
del q1, q2, q3, q4, q5                                      #они тоже больше не нужны

curr_t = -1                                                 #текущий номер
x = []                                                      #список для хранения отсчетов

##########################################################################################
############################Блок генератора модельных данных##############################
##########################################################################################

start_x = []                                                #список для стартовых значений

output = open('output_endless.txt', 'a')                
while(curr_t != n-1 ):                                      #начальное наполнение случайными данными
    q = np.random.randn()                                   #т.к. AR(n) основывается на n пред.значениях
    start_x.append(q)                                       #то же самое, но в массиве, не влияющем на x
    output.write(str(q) + '\n')                             #добавляем в файл вывода
    curr_t += 1
    del q

output.close()
#Bозможно, что начальное наполнение случайными данными внесет искажения в начале анализа данных, поэтому я
#создаю дополнительный массив, на котором основывается авторегрессия до момента заполнения x n значениями
curr_t = -1                                                 #сбрасываем счетчик после наполнения
h_curr = 0                                                  #начальный выбор модели

H_original = []                                             #сохраняем оригинальную цепь, нужно для дебага

def generate_number(h_curr, output):                        #функция генератора
    #для смены модели пропорционально вероятности, я решил брать рандомное число, принадлежащее [0,1],
    #разбить этот отрезок на сегменты, равные, собственно, вероятностям и смотреть, в какой сегмент
    #случайное число попало                                          
    factor = np.random.random()
    p_curr = 0
    global curr_t                                           #работаем с глобальным счетчиком отсчетов
    global H_original                                       #для сохранения оригинальной цепи
    curr_t += 1
    for h_next in range(0,m):
        p_curr += Q[h_curr][h_next]
        if(p_curr >= factor):
            if(h_curr != h_next):
                print('Model change: N', curr_t, h_curr, '-->', h_next)
                repers = open('repers_endless.txt', 'a')              #файл точек, где происходит смена модели
                repers.write(str(curr_t) + ' ' + str(h_curr) + '\n')        #конец предыдущего сегмента
                repers.write(str(curr_t) + ' ' + str(h_next) + '\n')        #начало следующего
                repers.close()
                h_curr = h_next
            break
    #цикл формирования отсчета AR(n)-процесса
    x_curr = phi[h_curr][0]
    for i in range(1,n+1):
        if(curr_t - i >= 0):                                                #проверка на отрицательный
            x_curr += phi[h_curr][i]*x[curr_t - i]                          #индекс
        else:
            x_curr += phi[h_curr][i]*start_x[curr_t - i]                    #используем стартовый массив
    x_curr += phi[h_curr][3]*np.random.randn()              #шум    
    #заменил random.random() на random.randn() - он имеет нормальное распределение, почему-то стало
                                                                                             #лучше
    x.append(x_curr)
    H_original.append(h_curr)
    output.write(str(x_curr) + '\n')
    print(x_curr,'h_curr =',h_curr)
    return h_curr                                           #возвращаем текущую модель
    
##########################################################################################
############################Блок анализатора данных#######################################
##########################################################################################

def beta(t, h_t1, h_t):                                     #ф-ция beta
    summ = 0                                                #сначала надо посчитать сумму, зав. от x
    for i in range(1,n+1):
        if(t - i >= 0):                                     #проверка на отрицательный индекс                   
            summ += x[t-i]*phi[h_t][i]
        else:
            summ += start_x[t-i]*phi[h_t][i]                #используем массив start_x
    res = (1/(2*phi[h_t][3]))*(x[t] - phi[h_t][0] - summ)**2 - np.log(Q[h_t1][h_t]) #по формуле из статьи
    return res

def d_t(d_t1):                                              #рекуррентный расчет d_t
    res = []
    k_t = []
    for i in range(0,m):                                    #перебор по моделям
        curr_j = []                                         #посчитать для всех j и выбрать min
        for j in range(0,m):                                #перебор по выбору предыдущего
            curr_j.append(d_t1[j] + beta(curr_t,j,i))       #расчет вектора всех значений, среди которых
        res.append(np.min(curr_j))                          #ищется минимум
        k_t.append(np.argmin(curr_j))                       #вектор k_t
    return res, k_t                                         #возвращаем рассчитанные вектора

def g_t(g_t1, k_t):                                         #рекуррентный расчет g_t
    res = []
    for i in range(0,m):
        res.append(g_t1[k_t[i]])
    return res

##########################################################################################
########################Главный цикл выполнения программы#################################
##########################################################################################

u = -1
u_prev = -1   
t_special = 0
K = []                                                      #матрица K
K.append([0,0,0,0,0])                                       #т.к новые столбцы в K добавляются с первого номера
H = []                                                      #искомая сегментация                                              
#начальный вектор d_t0
d_t0 = [-np.log(0.99),-np.log(0.0025),-np.log(0.0025),-np.log(0.0025),-np.log(0.0025)]
g_t0 = []

for i in range(0,m):                                        #формирование вектора g_t0
    g_t0.append(i)
h_t_11 = g_t0                                               #вектор (11) из статьи, не придумал, как его назвать

output = open('output_endless.txt', 'a')                    #добавляем в файл вывода
segmentation = open('segmentation_endless.txt', 'a')        #сегментации

for i in range(0,2000):                                     #3000 - тест, в конце перейти на while(True)
    h_curr = generate_number(h_curr, output)                #передача текущей модели в генератор
    d_t0, k_t_curr = d_t(d_t0)                              #получаем k_t(i) и d_t(i)
    K.append(k_t_curr)                                      #добавляем рассчитанный столбец в матрицу K
    if(curr_t == 0):                                        #для первого отсчета t_special и u уже определены
            print('First count, missing cycle.')
            continue
    g_t0 = g_t(g_t0, k_t_curr)                              #рекуррентный пересчет g_t
    sp_moment_flag = True
    
    for j in range(1,m):                                    #проверка на выполнение условия (16)
        if(g_t0[j] != g_t0[0]):
            sp_moment_flag = False                          #момент точно не особый, выходим из цикла
            break
    if(sp_moment_flag == True):                             #что делать, если момент особый
        print('SPECIAL MOMENT REGISTERED! CURR_T = ' + str(curr_t))
        #if(curr_t == 0):                                    #для первого отсчета t_special и u уже определены
        #    print('First count, missing cycle.')
        #    continue
        #debug_summ += 1
        #t_special = curr_t
        h_t_2 = h_t_11                                      #начальный вектор для расчетов h_s(i)
        u_prev = u                                          #предыдущая граница
        #for j in range(1,curr_t-u_prev-2):                     #вычисляем h_s(i) для отсчетов curr_t-1,...,0
        for j in range(1,len(K)):                               #по всем доступным столбцам в K, но подозрительно..
            h_t_1 = []                                          #вектор h_s(i), вычисляемый на новом шаге
            new_u_flag = True                                   #флаг, что найдена новая граница u_t
            for v in range(0,m):
                h_t_1.append(K[j][h_t_2[v]])

            for v in range(1,m):
                if(h_t_1[v] != h_t_1[0]):
                    new_u_flag = False                      #точно не новая граница u_t, выходим из цикла
                    break
            if(new_u_flag == False):
                h_t_2 = h_t_1                               #ищем новую границу дальше
            else:
                t_special = curr_t
                u = curr_t - j                              #новая граница найдена, выходим из цикла
                print('NEW U FOUND: ' + str(u))
                h_u = h_t_1[0]                              #начальное условие для расчета сегментации
                break
            
        H_curr = []                                         #текущий рассчитанный кусок сегментации
        segm_summ = 0                                       #debug
        
        for j in reversed(range(1,u-u_prev+1)):
            h_t_prev = K[j][h_u]                            #классификация эл-та
            H_curr.append(h_t_prev)                         #добавление в массив, которые потом склеится с H
            segm_summ += 1
            h_u = h_t_prev                                  #для рекуррентного пересчета h
        print('Segmentations added: n = ' + str(segm_summ))
        H_curr.reverse()                                    #т.к. сегментация была в обратном порядке
        
        if((len(H) == 0) & (len(H_curr) != 0)):             #запись результата в файл
            segmentation.write(str(0) + ' ' + str(H_curr[0]) + '\n')
            H_flag = H_curr[0]
        for t in range(0,len(H_curr)):
            if(H_curr[t] != H_flag):
                segmentation.write(str(len(H) + t) + ' ' + str(H_flag) + '\n')
                segmentation.write(str(len(H) + t) + ' ' + str(H_curr[t]) + '\n')               
                H_flag = H_curr[t]
        H += H_curr                                         #окончательный построенный отрезок сегментации
        k_deleted = 0                                       #debug mode on
        for j in reversed(range(1,u-u_prev+1)):               #удаляем с конца, чтобы не сбивалась нумерация
            K.pop(j)                                        #сбрасываем ненужные более столбцы
            k_deleted += 1
        print(str(k_deleted) + ' were deleted!')
        g_t0 = h_t_11                                       #т.к. особый момент времени, заново берем g0
output.close()

repers = open('repers_endless.txt', 'a')
repers.write(str(curr_t) + ' ' + str(h_curr) + '\n')        #замыкающая точка в файле(на какой модели остановка)
repers.close()

segmentation.write(str(u) + ' ' + str(H[len(H) - 1]) + '\n') #замыкающая точка в файле(на какой модели остановка)
segmentation.close()
