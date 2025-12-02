# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 00:00:54 2019

@author: protoDUNE
"""

import numpy as np
import os
from sys import exit
import os.path
import math
import time
import statsmodels.api as sm

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import matplotlib.mlab as mlab



def linear_fit(x, y):
    error_fit = False 
    try:
        results = sm.OLS(y,sm.add_constant(x)).fit()
    except ValueError:
        error_fit = True 
    if ( error_fit == False ):
        error_gain = False 
        try:
            slope = results.params[1]
        except IndexError:
            slope = 0
            error_gain = True
        try:
            constant = results.params[0]
        except IndexError:
            constant = 0
    else:
        slope = 0
        constant = 0
        error_gain = True

    y_fit = np.array(x)*slope + constant
    delta_y = abs(y - y_fit)
    inl = delta_y / (max(y)-min(y))
    peakinl = max(inl)
    return slope, constant, peakinl, error_gain

if True: # fitting group 2
    x = [10,20,30,40,50,60,70,80,90,100]
    y = [199,345,496,645,790,938,1090,1240,1390,1540]
    
    #x= np.array(x)*0.213
    x= np.array(x)*1.203
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='r')
    plt.plot(x, x*slope + constant, color='r', label= f'RT, Ext_Cal=1.203pF, 14mV/fC, 250ns, Gain={slope:.2f} mV/fC')



    x = [50,100,150,200,250,300,350,400,500,600,]
    y = [180,311,447,576,707,840,970,1110,1380,1500]
    x= np.array(x)*0.213
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='b')
    plt.plot(x, x*slope + constant, color='b', label= f'LN2, Cali_Cap=0.213pF, 14mV/fC, Gain={slope:.2f} mV/fC')

    
    plt.xlabel("Injected Charge / fC")
    plt.ylabel("Amplitude / mV ")
    plt.xlim((0,150))
    plt.ylim((0,1800))
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()



if False: # fitting group 2
    x = [50,100,150,200,250,300,350,400,274]
    y = [184,325,467,609,741,884,1020,1160,810]
    
    x= np.array(x)*0.213
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='r')
    plt.plot(x, x*slope + constant, color='r', label= f'RT, 1us, Cali_Cap=0.213pF, Gain={slope:.2f} mV/fC')

    x = [50,100,150,200,250,300,350,400,500,600,]
    y = [193,335,481,620,756,896,1040,1180,1430,1490]
    x= np.array(x)*0.213
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='b')
    plt.plot(x, x*slope + constant, color='b', label= f'LN2, Cali_Cap=0.213pF, Gain={slope:.2f} mV/fC')

    
    plt.xlabel("Injected Charge / fC")
    plt.ylabel("Amplitude / mV ")
    plt.xlim((0,150))
    plt.ylim((0,1800))
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()




if False: # fitting group 2
    x = [10,20,30,40,50,60,70,80,90,100]
    y = [202, 360,518,676,833,991,1150,1300,1470,1580]
    x= np.array(x)*1.203
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='r')
    plt.plot(x, x*slope + constant, color='r', label= f'RT, 14mV/fC, 1us, Gain={slope:.2f} mV/fC')
    
    x = [10,20,30,40,50,60,70,80,90,100]
    y = [199,345,496,645,790,938,1090,1240,1390,1540]
    
    #x= np.array(x)*0.213
    x= np.array(x)*1.203
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='m')
    plt.plot(x, x*slope + constant, color='m', label= f'RT, 14mV/fC, 250ns, Gain={slope:.2f} mV/fC')
    

    x = [10,20,30,40,50]
    y = [186,344,503,661,818]
    x= np.array(x)*1.203
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='g')
    plt.plot(x, x*slope + constant, color='g', label= f'RT, 14mV/fC, 1us, BL900mV, Gain={slope:.2f} mV/fC')

    
    plt.xlabel("Injected Charge / fC")
    plt.ylabel("Amplitude / mV ")
    plt.xlim((0,150))
    plt.ylim((0,1800))
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()



if False: # fitting group 1
    x = [10,20,30,40,50,60,70,80,90,100]
    y = [202, 360,518,676,833,991,1150,1300,1470,1580]
    x= np.array(x)*1.203
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='r')
    plt.plot(x, x*slope + constant, color='r', label= f'RT, Ext_Ccap=1.203pF, Gain={slope:.2f} mV/fC')
    
    x = [50,100,150,200,250,300,350,400,274]
    y = [184,325,467,609,741,884,1020,1160,810]
    
    x= np.array(x)*0.213
    ress = linear_fit(x[0:6],y[0:6])
    slope = ress[0]
    constant = ress[1]
    
    plt.scatter(x,y, color='m')
    #plt.plot(x, x*slope + constant, color='r', label= f'RT, Gain={slope:.2f} mV/(mV*Ccali)')
    plt.plot(x, x*slope + constant, color='m', label= f'RT, Cali_Cap=0.213pF, Gain={slope:.2f} mV/fC')
    
    
    plt.xlabel("Injected Charge / fC")
    plt.ylabel("Amplitude / mV ")
    plt.xlim((0,150))
    plt.ylim((0,1800))
    plt.legend()
    plt.grid()
    plt.show()
    plt.close()
    
