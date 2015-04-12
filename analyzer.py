import numpy as np

phi1 = [0,  1.36,  -0.49, 0.36]                              #параметры авторегрессионных моделей
phi2 = [0,  1.02,  -0.40, 0.63]                              #последнее число - параметр B, определяющий
phi3 = [0,  0.82,  -0.49, 0.73]                              #                      степень влияния шума
phi4 = [0,  0,     -0.49, 0.87]
phi5 = [0, -0.82,  -0.49, 0.73]
phi = np.array([phi1,phi2,phi3,phi4,phi5])
n = 2                                                       #порядок AR-процесса
m = 5

q1 = [0.99,   0.0025, 0.0025, 0.0025, 0.0025]
q2 = [0.0025, 0.99,   0.0025, 0.0025, 0.0025]
q3 = [0.0025, 0.0025, 0.99,   0.0025, 0.0025]
q4 = [0.0025, 0.0025, 0.0025, 0.99,   0.0025]
q5 = [0.0025, 0.0025, 0.0025, 0.0025, 0.99]
Q = np.array([q1,q2,q3,q4,q5])                              #матрица вер-ти переходов

data = open('output.txt', 'r')
x = [float(line.strip()) for line in data]                  #считывание отсчетов из файла
x = np.array(x)
N = np.size(x)

def beta(t, h_t1, h_t):                                     #ф-ция beta
    summ = 0                                                #сначала надо посчитать сумму, зав. от x
    for i in range(1,n+1):                                    
        if (t >= 2) :                                       #проверка на отрицательный индекс        
            summ += x[t-i]*phi[h_t][i]
    res = (1/(2*phi[h_t][3]))*(x[t] - phi[h_t][0] - summ)**2 - np.log(Q[h_t1][h_t])  #по формуле из статьи
    return res

#рекуррентный расчет векторов d_t                                          
#в написанном мной генераторе вероятность начальных данных - 0.99 для 0 класса и 0.0025 для остальных
#d_t1 - предыдущий вектор, d_t - следующий
#начальный вектор d0
d_t1 = [-np.log(0.99),-np.log(0.0025),-np.log(0.0025),-np.log(0.0025),-np.log(0.0025)]
d_t = np.zeros(m)
K = np.zeros((m,N))                                               #таблица К[m,N]

#тройной цикл это не хорошо и это место, наверное, можно оптимизировать, но для проверки
#работоспособности на данных небольшого размера можно пока оставить
for t in range(0,N):                                              #цикл по времени
    for h_t in range(0,m):                                        #по выбору h(0....m=4)
    #здесь фиксируется строчка матрицы K(значение h), для которого ищется минимум при
    #различных подстановках предыдущего h0
        curr = np.zeros(m)
        for h0 in range(0,m):                                     #перебор по h0 для поиска минимума
            #здесь считаются значения d_t[i] для разных выборов h0
            curr[h0] = d_t1[h0] + beta(t,h0,h_t)
        d_t[h_t] = np.min(curr)                                   #минимум для i по выбору h0
        K[h_t][t] = np.argmin(curr)                               #запись в K
        d_t1 = d_t                                                #переходим к следующему  
                      
H = np.zeros(N)                                                   #оптимальная сегментация
H[N-1] = np.argmin(d_t)                                           #последний эл-т сегментации
for t in reversed(range(1, N)):
    H[t - 1] = K[H[t]][t]
    
output = open('segmentation.txt', 'w')                            #файл для вывода
H_curr = H[0]
#output.write('N:' + str(0) + ' Model:' + str(int(H_curr)) + '\n')
output.write(str(0) + ' ' + str(int(H_curr)) + '\n')
for t in range(0, N):
    if(H[t] != H_curr):
        #output.write('N:' + str(t) + ' Model:' + str(int(H[t])) + '\n')
        output.write(str(t) + ' ' + str(int(H[t-1])) + '\n')
        output.write(str(t) + ' ' + str(int(H[t])) + '\n')
        H_curr = H[t]
output.write(str(N) + ' ' + str(int(H[N-1])) + '\n')
output.close()