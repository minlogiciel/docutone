#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 20:16:01 2018
This scripts is meant to read a stream containing the measure of heat channels
and ionization channels.
@author:
"""


import re
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize as op
import scipy.signal as sgl
from tqdm import trange, tqdm
import math
import sys, codecs




sampling = 1000.
window_w = 1.
gain = 1.
num_load = int(2e5)

adu = 67.4e-9
adu_cut = 17000 * adu

"""
read the file and the log and binary files
"""
folder_path = '/home/joel/Documents/Stage/RED_stream_core/Data/ri11g001'

run_name = os.path.basename(folder_path)
log_path = os.path.join(folder_path, run_name+'_log')
data_path = os.path.join(folder_path, run_name+'_000')

plt.close('all')

"""
Extracts useful information from the log file.
creates an offset because the binary file has a text beginning and the data starts after the offset so it is used
to start reading the correct data
"""


########## Extract information from header of binary File ##########
PathRun = '/home/joel/Documents/Stage/RED_stream_core/Data/ri11g001' #Directory with data
Run = 'ri11g001'



amplitude_file = '/home/joel/Documents/Stage/Analysis_ri11g001/ri11g001_0_TriggerStep4_SpectrumAmplitude.txt'
amplitude_ion  = '/home/joel/Documents/Stage/Analysis_ri11g001/ri11g001_ion_trigger.txt'

split_index = PathRun.rfind('/') #Find last '/' to extract run name

Path = PathRun[:split_index]
Run = PathRun[split_index+1:]


Gain = 0
Octet_offset = 0
total_octet = 0
partitionNum = 0

fe = 0
ListChannel = []
NumberChal = 0
voie = 0

dt = 1.
Dt = 1000 ##Portion of the stream to plot [s]
eps = 2e3
freq = 1000



########## Extract partition info from _log file ##########
def extractLogInfo(filename):
    #f = codecs.open(filename, 'r')
    f = open(filename)
    for line in f :
        if 'Creation' in line and 'streams/' in line:
            split_index2 = line.rfind('_')
            partitionNum = line[split_index2:split_index2+4]
        elif 'donnees' in line and 'commencent' in line:
            value_Line_octet = re.findall('octet (\d+)', line)
            Octet_offset = int(value_Line_octet[0])     #octet where binary data start
            
        elif 'octets' in line:
            value_Line_scale =  re.findall('(\d+) octets', line)
            total_octet = int(value_Line_scale[0])      #octet total of the acquistion
        ##Channel gain
        elif 'chalA' in line:
            if 'neant' in line or '|demodulation' in line :
                value_Line_GainA = re.findall('-(\d+\.\d+)', line)
                Gain = float(value_Line_GainA[0]) * 1e-9 / 2
    f.close()


''' Extract info from header binary file '''
def extactHeaderInfo(filename) :
    NumberChal = 0
    ListChannel = []
    f = open(filename)
    
    for line in f:
        if 'd2A :' in line:
            value = re.findall('= (\d+)', line)
            freqD2 = float(value[0]) #Frequency D2
            
        elif 'd3A :' in line:
            value_Line_freqD3 = re.findall('= (\d+)', line)
            freqD3 = float(value_Line_freqD3[0]) #Frequency D3
                
        elif '* Voie' in line:
            NumberChal = NumberChal + 1 #Number of channels read
                
            split_index3 = line.find('"')
            if '"' in str(line[split_index3+1:split_index3+7]):
                ListChannel.append(str(line[split_index3+1:split_index3+6]))
            else:
                ListChannel.append(str(line[split_index3+1:split_index3+7]))
                
        elif '* Donnees' in line:
            break #Stop before binary part
        
    f.close()
    fe = freqD3
            

########## Load data from binary part ##########
def loading_data_from_binaire(filename) : 
    
    length_l0 = (total_octet - Octet_offset)/2/ListChannel[0] #total length of the acquistion
    
    l0 = np.memmap(filename,
               dtype='int16', mode='r',
               offset=Octet_offset,
               shape=(int(length_l0*0.999), ListChannel[0]))

    #TWEAK
    l0 = l0.astype('float64')

    

    l1 = l0[:,voie] * Gain
    T1 = np.arange(0,(len(l1))/fe,1./fe) 
    
    return T1, l0


########## Data to treat ##########
       
    

#dt = input(' *  Size of time division of the stream (time window [s]): ')
#Fig1 = plt.figure("Fig1")
#plt.title('Signal within [0-1000] sec')
#plt.xlabel('Time [s]')
#plt.ylabel('Amplitude [V]')
#plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
#plt.plot(T1[0:int(Dt*fe)], l1[0:int(Dt*fe)])
#plt.grid()
#    
#plt.show(block=False)

def plots(l0):
    chan_num = l0.shape[-1]
    fig, ax = plt.subplots(chan_num, sharex=True, num='myfig')
    
    T1 = np.arange(0,(l0.shape[0])/fe,1./fe) 
    for i, a in enumerate(ax):
        if i == 0:
            a.plot(T1[0:int(Dt*fe)], l0[0:int(Dt*fe), i]*Gain)
            continue
        a.plot(T1[0:int(Dt*fe)], l0[0:int(Dt*fe), i])
    
    

    ion_tuple = (l0[ : ,1], l0[ : ,2], l0[ : ,3])    
    ion_alt_tuple = [var_change_funk(ion_tuple, k)
                        for k in range(len(ion_tuple))]
    ion_alt_tuple += (sum_of_abs(ion_alt_tuple),)
    
    return ion_alt_tuple



"""
Apply the change of variables, and compute the sum.
"""
def sum_of_abs(var_list):
    return np.sum(np.abs(var_list), axis=0)
        
def var_change_funk(var_tuple, rank):
    var_list = list(var_tuple)
    var_alt = (2./3)*var_list.pop(rank) - (1./3)*np.sum(var_list, axis=0)
    return var_alt

    
"""
High-pass filtering applied to the ionization channels, and correlation
between the template and the data stream.
"""
def filtering_ionization(ion_alt_tuple):
    
    """
    Template of an ionization signal.
    """
    template_width = 1. #s
    template_points = template_width*1000
    template = np.ones(int(template_points))
    template[:int(template_points/2)] = 0
       

    freq_cut = 2. #Hz
    order = 2
    freq_nyq = freq/2
    
    freq_cut_norm = freq_cut/freq_nyq
    b, a = sgl.butter(order, freq_cut_norm, btype='highpass')
    zi = sgl.lfilter_zi(b, a)
    
    ion_tot = ion_alt_tuple[-1]
    ion_fil_tuple = sgl.lfilter(b, a, ion_tot, zi=zi*ion_tot[0])[0]
    
    template_fil= sgl.lfilter(b, a, template, zi=zi*template[0])[0]
    
    corr = np.correlate(ion_fil_tuple, template_fil, mode='same')
    corr = abs(corr)
    return corr


def custom_roll(array, a):
    rolled = np.roll(array, a)
    if a>0:
        rolled[:a] = array[0]
    elif a<0:
        rolled[a:] = array[-1]
    return rolled

def maxima_passing_trigger(Y, eps):
    
    index_rise = list(
        np.where(np.logical_and(Y<eps, custom_roll(Y, -1)>eps))[0]
    )
    index_fall = list(
        np.where(np.logical_and(Y<eps, custom_roll(Y, +1)>eps))[0]
    )
    
    if index_rise==[] and index_fall==[]:
        raise Exception("Threshold 'eps' couldn't be attained.")
    if index_rise==[] and index_fall!=[]:
        index_rise.append(0)
    if index_rise!=[] and index_fall==[]:
        index_fall.append(None)
    if index_fall[-1]<index_rise[-1] and index_fall[-1]!= None:
        index_fall.append(None)
    if index_rise[0]>=index_fall[0] and index_fall[-1]!= None:
        index_rise.insert(0, 0)
        
# ###DEBUG PLOTS
#    plt.figure()
#    plt.plot(Y)
#    plt.axhline(eps, color='k', zorder=10)
#    for i in index_rise:
#        plt.axvline(i, color='g')
#    for i in index_fall:
#        plt.axvline(i, color='orange')
#    plt.yscale('log')
#
    index_max = map(lambda r,f: np.argmax(Y[r:f])+r, index_rise, index_fall)
    
    return index_max



def triggering(x_list, y_list, eps, freq_cut):
    """
    Triggering of the pulses of the stream.
    Return the triggering indexes.
    """
    index = maxima_passing_trigger(y_list, eps)
    
    y_pulse = np.array([y_list[i] for i in index])
    x_pulse = np.array([x_list[i] for i in index])
    
    i_out = []
    lock_window = 2./freq_cut
    
    for i in range(len(x_pulse)-1):
        if x_pulse[i+1]-x_pulse[i] < lock_window:
            if y_pulse[i+1] > y_pulse[i]:
                i_out.append(i)
            else:
                i_out.append(i+1)
    
    index_trig = np.delete(index, i_out)
    
    return index_trig


def save(filename, T1, corr, l0) :
    
    index_pulse = triggering(T1, corr, eps, 2.)

    time=[]
    Data=[]
    
    for i in index_pulse:
        Amp_A0 = l0[i+1,1]-l0[i-1,1]
        Amp_B0 = l0[i+1,2]-l0[i-1,2]
        Amp_C0 = l0[i+1,3]-l0[i-1,3]
        
        time.append(i/1000.)
        if abs(Amp_A0) > 10 and abs(Amp_C0) > 10 and abs(Amp_B0) < 100 :
            assert (abs(Amp_A0) + abs(Amp_C0))/2 > 0
       
            Data.append([abs(Amp_A0), time[i]])
        
    np.savetxt(filename, Data)


def loadData(filename) :

    data  = np.loadtxt(filename) 
    
    X=[]
    Y=[]
    prev_x = 0
    for i in range (len(data)):
        if  data[i][0] > 100 :
            x = data[i][0]
            y = data[i][1]
            if round(x)%4 != 3:
                if (x - prev_x) > 0.5:
                    X.append(x)
                    Y.append(y)

    return X, Y

def showInfo(total_time):
    ########## Introduction to the measurement ##########    
    

    print ('\n * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
    print (' *  Run ', Run, ', Number of channels ', NumberChal, ' ; Sampling frequency, fe = ',fe, 'Hz')
    print (' *  Total time = ',total_time, 'sec (', total_time/3600.,'hrs )')
    print (' *  Selected channel: ', ListChannel[0])
    print (' *  Gain = ', Gain * 1e9, 'nV/ADU')
    print (' *  Octet offset = ', Octet_offset)
    print (' *  Size of time division of the stream (time window [s]): ',dt)


def display(X, Y, T, A) :
 
    
    plt.figure(num='ionisation')
    plt.plot(T, A, '.')
    plt.show()

    
    plt.figure(num='chaleur')
    plt.plot(X, Y,'.')
    plt.show()
    '''
    plot chaleur en fonction de l'ionisation
    '''
    A_fin=[]
    C_fin=[]
    for i in range (len(X)):
        for j in range (len(T)):
            if round(X[i][0]) == round(T[j][0]):## je vérifie que les evenements ont eu lieu en même temps
                A_fin.append(A[j])
                C_fin.append(Y[i])

    plt.figure(num='espoir')
    plt.plot(A_fin,C_fin,'.') 
    plt.show()
    

  
def main() :
    
    RunLogfile = PathRun + '/'+ Run + '_log'
    extractLogInfo(RunLogfile)
    
    PartitionFile =  PathRun + '/' +  Run + str(partitionNum)
    extactHeaderInfo(PartitionFile)
    
    T1, l0 = loading_data_from_binaire(PartitionFile)
    
    total_time = len(l0)/fe
    showInfo(total_time)
    
    ion_alt_tuple = plots(l0)
    
    corr = filtering_ionization(ion_alt_tuple)
    
    save(amplitude_ion, T1, corr, l0)
    
    X, Y = loadData(amplitude_file)
    T, A = loadData(amplitude_ion) 
    
    display(X, Y, T, A)


  
if __name__ == '__main__':

    main()
    
    
    
    