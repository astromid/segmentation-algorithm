# -*- coding: utf-8 -*-
"""
Created on Thu Apr 23 20:31:32 2015

@author: Yan
"""

import subprocess
import numpy as np

def get_statistics():    
    subprocess.call('python analyzer_endless.py')                              #запускаем скрипты в нужной
    print('Iteration...Burobin completed.')
    subprocess.call('python cusum.py')                                         #очередности
    print('Iteration...CUSUM completed.')
    
    data = open('repers_endless.txt', 'r')                                     #расшифровываем оригинальную цепь
    original_text = [line.strip() for line in data]
    original = [s.split(' ') for s in original_text]
    original = np.array(original)
    data.close()
    del original_text
    original_segm = []
    t_prev = 0
    for i_orig in range(0,len(original)):                                      #строим оригинальную цепь
        for t in range(t_prev,int(original[i_orig][0])):
            original_segm.append(int(original[i_orig][1]))
        t_prev = int(original[i_orig][0])
    original_segm.append(int(original[i_orig][1]))
    del original
    
    data = open('segmentation_endless.txt', 'r')                               #сегментацию по Буробину
    burobin_text = [line.strip() for line in data]
    burobin = [s.split(' ') for s in burobin_text]
    burobin = np.array(burobin)
    data.close()
    del burobin_text
    burobin_segm = []
    t_prev = 1
    for i_burob in range(0,len(burobin)):                                      #строим сегментацию по Буробину
        for t in range(t_prev,int(burobin[i_burob][0])):
            burobin_segm.append(int(burobin[i_burob][1]))
        t_prev = int(burobin[i_burob][0])
    burobin_segm.append(int(burobin[i_burob][1]))
    del burobin
    
    data = open('segmentation_cusum.txt', 'r')                                 #сегментацию CUSUM
    cusum_text = [line.strip() for line in data]
    cusum = [s.split(' ') for s in cusum_text]
    cusum = np.array(cusum)
    data.close()
    del cusum_text
    cusum_segm = []
    t_prev = 1
    for i_cusum in range(0,len(cusum)):                                        #строим сегментацию CUSUM
        for t in range(t_prev,int(cusum[i_cusum][0])):
            cusum_segm.append(int(cusum[i_cusum][1]))
        t_prev = int(cusum[i_cusum][0])
    cusum_segm.append(int(cusum[i_cusum][1]))
    del cusum
    
    q_burobin = 0
    q_cusum = 0
    for t in range(0,len(burobin_segm)):                                       #считаем коэфф. качества
        if(burobin_segm[t] == original_segm[t]):
            q_burobin += 1
        if(cusum_segm[t] == original_segm[t]):
            q_cusum += 1
    q_burobin = q_burobin/t
    q_cusum = q_cusum/t
    
    return q_burobin, q_cusum
 
q_burobin = 0
q_cusum = 0   

for i in range(0, 20):                                                         #главный цикл
    q_burobin_curr, q_cusum_curr = get_statistics()
    q_burobin += q_burobin_curr
    q_cusum += q_cusum_curr
    print('Iteration ' + str(i) + ' complete.')

q_burobin = q_burobin/(i+1)                                                    #итоговые коэффициенты
q_cusum = q_cusum/(i+1)