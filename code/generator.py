import numpy as np
#from time import sleep
#import sys
#import argparse

#def createParser():
#    parser = argparse.ArgumentParser()
#    parser.add_argument('-N', '--number', default = '5000')


N = 3000                                                    #количество отсчетов
#dt = 0.05                                                   #задержка по времени
phi1 = [0,  1.36,  -0.49, 0.36]                              #параметры авторегрессионных моделей
phi2 = [0,  1.02,  -0.40, 0.63]                              #последнее число - параметр B, определяющий
phi3 = [0,  0.82,  -0.49, 0.73]                              #                      степень влияния шума
phi4 = [0,  0,     -0.49, 0.87]
phi5 = [0, -0.82,  -0.49, 0.73]
phi = np.array([phi1,phi2,phi3,phi4,phi5])

q1 = [0.99,   0.0025, 0.0025, 0.0025, 0.0025]
q2 = [0.0025, 0.99,   0.0025, 0.0025, 0.0025]
q3 = [0.0025, 0.0025, 0.99,   0.0025, 0.0025]
q4 = [0.0025, 0.0025, 0.0025, 0.99,   0.0025]
q5 = [0.0025, 0.0025, 0.0025, 0.0025, 0.99]
Q = np.array([q1,q2,q3,q4,q5])                               #матрица вер-ти переходов
x = np.zeros(N+2)

output = open('output.txt', 'w')                             #файл данных
repers = open('repers.txt', 'w')                             #файл точек, где происходит смена модели

h_t = 0
#для смены модели пропорционально вероятности, я решил брать рандомное число, принадлежащее [0,1],
#разбить этот отрезок на сегменты, равные, собственно, вероятностям и смотреть, в какой сегмент
#случайное число попало.
for i in range(2,N+2):                                          
    factor = np.random.random()
    p_curr = 0
    for j in range(0,5):
        p_curr += Q[h_t][j]
        if(p_curr > factor):
            if(h_t != j):
                print("Model has been changed to ",j)
                #repers.write('N:' + str(i-2) + ' Model:' + str(j) + '\n')
                repers.write(str(i-2) + ' ' + str(h_t) + '\n')
                repers.write(str(i-2) + ' ' + str(j) + '\n')
                h_t = j
            break
    #сама формула AR(2)-процесса
    x[i] = phi[h_t][0] + phi[h_t][1]*x[i-1] + phi[h_t][2]*x[i-2] + phi[h_t][3]*np.random.random()
    #заменил random.random() на random.randn() - он имеет нормальное распределение, почему-то стало
                                                                                             #лучше
    output.write(str(x[i])+'\n')
    print(str(x[i]) + ' h_t = ' + str(h_t))
    #sleep(dt)
repers.write(str(N) + ' ' + str(h_t))
repers.close()
output.close()