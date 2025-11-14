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
from raw_data_decoder import raw_conv
from fft_chn import chn_fft_psd

import pickle

fn = 'D:/CHARMS250/data/BoardA11_ChipSN01_P2_RT/Noise_after_reset.bin'
fn = 'D:/CHARMS250/data/BoardA11_ChipSN01_P2_RT/Noise_after_reset_Cal_to_SG.bin'
fn = 'D:/CHARMS250/data/BoardA11_ChipSN01_P2_RT/Noise_BL_200.bin'
fn = 'D:/CHARMS250/data/BoardA11_ChipSN01_P2_RT/Noise_BL_200_smn.bin'
fn = 'D:/CHARMS250/data/BoardA11_ChipSN01_P2_RT/DIFF.bin'
fn = 'D:/CHARMS250/data/BoardA11_ChipSN01_P2_RT/pls20mV.bin'
with open (fn, 'rb') as fp:
    rawdata = pickle.load(fp)
    chns = raw_conv(rawdata)[0]
fig = plt.figure(figsize=(8,6))
print (len(chns))
#for i in range(len(chns)):
#for i in range(8,16,1):
for i in [9]:
#for i in range(0,8,1):
    #x = np.arange(1000) + (i*0.125)
    x = np.arange(200) 
    y = chns[i][00:200]
    print (np.max(chns[i][100:150]) - np.mean(chns[i][70:100])) 

    #plt.plot(chns[i][0:10000], label="CH%d"%i, marker='.')
    #plt.scatter(x, y, label="CH%d"%i, marker='.')
    plt.plot(x, y, label="CH%d"%i, marker='.')



#interlaved = [item for sublist in zip(chns[8], chns[9], chns[10],chns[11], chns[12],chns[13], chns[14],chns[15]) for item in sublist]
#interlaved = [item for sublist in zip(chns[0], chns[1], chns[2],chns[3], chns[4],chns[5], chns[6],chns[7]) for item in sublist]

#x = np.arange(8000) *0.125 
#plt.plot(x, np.array(interlaved[0:8000]), label="interleaved")

#for i in range(16):
#    print (i, len(chns[i]), np.mean(chns[i]), np.std(chns[i]))
plt.legend()
plt.show()
plt.grid()
plt.close()
#fig = plt.figure(figsize=(12,4))
#f, p = chn_fft_psd(chns[9], fs = 2000000.0, fft_s = 5000, avg_cycle = 50)
#plt.plot(f,p)
#plt.grid()
#plt.show()
#plt.close()

#                poft = 0
#                for j in range(period):
#                    if ((chns[0][j]&0x10000) & 0x10000) > 0:
#                        poft = j
#                        if poft <50:
#                            poft = 200+poft-50
#                        else:
#                            poft = poft-50
#                        break
#            
#                chns_info = []
#                for chnno in range(len(chns)):
#                    for i in range(0,avg_n):
#                        if i == 0:
#                            avg_chns = (np.array(chns[chnno][poft+200*i:poft+200+200*i])&0xffff)
#                        else:
#                            avg_chns = avg_chns + (np.array(chns[chnno][poft+200*i:poft+200+200*i])&0xffff)
#                    avg_chns = avg_chns//avg_n
#                    chn_pkp = np.max(avg_chns)
#                    chn_pkn = np.min(avg_chns)
#                    chn_ped = (avg_chns[0])  
#                    chn_ploc = np.where( avg_chns == chn_pkp )[0][0]
#                    if (mode16bit):
#                        chns_info.append([asic_dac, chn_pkp, chn_pkn, chn_ped, avg_chns[chn_ploc-20:chn_ploc+80]])
#                    else:
#                        chns_info.append([asic_dac, chn_pkp//16, chn_pkn//16, chn_ped//16, avg_chns[chn_ploc-20:chn_ploc+80]//16])
#                     
#                asic_info.append(chns_info)
#            else:
#                pass
#   # print(chns_info[0], chns_info[1])
#    return asic_info
#
#def linear_fit(x, y):
#    error_fit = False 
#    try:
#        results = sm.OLS(y,sm.add_constant(x)).fit()
#    except ValueError:
#        error_fit = True 
#    if ( error_fit == False ):
#        error_gain = False 
#        try:
#            slope = results.params[1]
#        except IndexError:
#            slope = 0
#            error_gain = True
#        try:
#            constant = results.params[0]
#        except IndexError:
#            constant = 0
#    else:
#        slope = 0
#        constant = 0
#        error_gain = True
#
#    y_fit = np.array(x)*slope + constant
#    delta_y = abs(y - y_fit)
#    inl = delta_y / (max(y)-min(y))
#    peakinl = max(inl)
#    return slope, constant, peakinl, error_gain
#
#def Chn_Ana(asic_cali, chnno = 0, cap=1.85E-13, sg="14mV"):
#    #if ("47mV") in sg:
#    #    fcs = 20
#    #    dac_mv = 18.5*0.001
#    #elif ("78mV") in fpic:
#    #    fcs =  20
#    #    dac_mv = 14.3*0.001
#    #elif ("14mV") in fpic:
#    #    fcs = 20
#    #    dac_mv = 8.06 *0.001
#    #elif ("25mV") in fpic:
#    #    fcs = 20
#    #    dac_mv = 4.56 *0.001
#    #else:
#    #    fcs = 20 
#        
#    if (BL == "200mV"):
#        fcs = 80/8
#    else:
#        fcs = 40/8
#        
#    dac_mv = 8.06 *0.001/1
#
#    dacs = []
#    ps = []
#    ns = []
#    peds = []
#    wfs  =[]
#    for t in asic_cali:
#        dacs.append(t[chnno][0])
#        ps.append(t[chnno][1])
#        ns.append(t[chnno][2])
#        peds.append(t[chnno][3])
#        wfs.append(t[chnno][4])
#     
#    print(dacs, ps)   
#    enc_per_v = cap / (1.602E-19)
#    enc_daclsb = dac_mv * enc_per_v
#    print(enc_daclsb, dac_mv, enc_per_v)
#    encs = np.array(dacs)*enc_daclsb
#    pos = np.where(encs >= 6250*fcs)[0][0]
#    print(pos)
#    fit_results = linear_fit(ps[:pos], encs[:pos] )
#    oft = fit_results[0]*peds[0] + fit_results[1]
#    encs = np.array(encs) - oft
#    print(ps, encs/6250) 
#    return encs, ps, ns, peds, wfs, fit_results
#
#def Chn_Plot(asic_cali, chnno = 0, mode16bit=True, fpic = "gain.png"):
#    if (mode16bit):
#        fs = 65535
#        adc_bits = "ADC16bit"
#    else:
#        fs = 4095
#        adc_bits = "ADC12bit"
#        
#    p = Chn_Ana(asic_cali, chnno = chnno, sg=fpic)  
##    print (len((p[4])))
##    print (len((p[4])[0]))
##    print (len((p[4])[0][0]))
##    exit()
#        
#    fig = plt.figure(figsize=(12,4))
#    #plt.title("Gain Measurment of Channel %d"%chnno)
#    ax1 = fig.add_subplot(131)
#    ax2 = fig.add_subplot(132)
#    ax3 = fig.add_subplot(133)
#    sps = 20
#    #for wf in p[4][5:10]:
#
#    for wf in p[4]:
#        if (len(wf) == 100):
#            max_pos = np.where(wf == np.max(wf))[0][0]
#            ax1.plot(np.arange(sps)*0.5, wf[max_pos-10: max_pos+10])
#            min_pos = np.where(wf == np.min(wf))[0][0]
#            ax2.plot(np.arange(sps)*0.5, wf[max_pos+40: max_pos+60])
#    ax3.scatter(np.array(p[1]), np.array(p[0])/6250, marker = '.', color = 'b')
#    ax3.scatter(np.array(p[2]), -np.array(p[0])/6250, marker = '.', color = 'r')
#    ax3.scatter ([p[3][0]], [0], marker = "s")
#    x = np.linspace(0, fs)
#    y = (x-p[3][0])*p[5][0]
#    ax3.plot( x, y/6250, color ='m', label= "Gain = %d (e-/LSB)\n INL = %.2f%%"%(p[5][0], p[5][2]*100))
#    ax3.legend()
#
#    ax1.set_title("Waveforms Overlap of CH%d"%chnno)
#    ax2.set_title("Waveforms Overlap of CH%d"%chnno)
#    ax3.set_title("Linear Fit of CH%d"%chnno)
#
#    ax1.set_xlabel("Time / $\mu$s")
#    ax2.set_xlabel("Time / $\mu$s")
#    ax3.set_xlabel("ADC counts / bin")
#
#    ax1.set_ylabel("ADC counts / bin")
#    ax2.set_ylabel("ADC counts / bin")
#    ax3.set_ylabel("Charge / fC")
#    
#
#    ax1.set_xlim((0,10))
#    ax2.set_xlim((0,10))
#    ax3.set_xlim((-100,fs))
#   
#    ax1.set_ylim((0,fs))
#    ax2.set_ylim((0,fs))
#    ax3.set_ylim((-100,150))
#
#    ax1.grid(True)
#    ax2.grid(True)
#    ax3.grid(True)
#    plt.tight_layout()
#    plt.savefig( fpic + adc_bits + "_ch%d.png"%chnno)
#    plt.close()
#
#    return p
#
##mode16bit = False
#mode16bit = True
#BL = "200mV"
#SEDC = "SDD_OFF"
#SEBUF = "BUF_OFF"
#
##testnos = list(range(1,5)) + list(range(11, 15)) + list(range(21, 25)) + list(range(31, 35))
#tps = ["05us", "10us", "20us", "30us"]
##tps = ["05us"]
#
##testnos =  list(range(21, 25)) D:\LArASIC_P5A\ENC\BoardS2_ChipP2DIE01_P5AFEDIE03_03_LN_sdc_off_ldo_500nA
##for testno in testnos:
#for tp in tps:
#    #testno_str = "Test%02d"%testno
#    testno_str = ""
#    #f_dir = "D:/ColdADC_P2/BoardS2_ChipP2DIE01_FE_150pF_dewar_LN/gainmeas_acq_Cap/"
#    #f_dir = "D:/LArFE_P2/BoardS1_ChipP2DIE01_FE_P2C3701_150pF_LN/gainmeas_acq_Cap/"
#    #f_dir = "D:/LArFE_P3/BoardS2_ChipP2DIE01_FE_FE_P3_150pF_run2_RT/gainmeas_acq_Cap/"
#    #f_dir = "D:/LArFE_P3/BoardS2_ChipP2DIE01_FE_FE_P3_150pF_run2_LN/gainmeas_acq_Cap/"
#    #f_dir = "D:/LArASIC_P5A1/BoardS2_ChipP2DIE01_P5FEDIE01_LN/gainmeas_acq_Cap_150pF/"
#    #f_dir = "D:/LArASIC_P5/BoardS2_ChipP2DIE01_P5FEDIE02_LN/gainmeas_acq_Cap_150pF/"
#    #f_dir = "D:/LArFE_P4/BoardA1S1_ChipP2DIE01_FE_P4DIE07_150pF_RT/gainmeas_acq_Cap/"
#    #f_dir = "D:/LArFE_P4/BoardA1S1_ChipP2DIE01_FE_P4DIE07_150pF_run02_RT/gainmeas_acq_Cap/"
#    #f_dir = "D:/LArFE_P4/BoardA1S1_ChipP2DIE01_FE_P4DIE07_150pF_LN/gainmeas_acq_Cap/"
#    f_dir = "D:/LArASIC_P5/ENC/BoardS2_ChipP2CHIP40_P5FEDIE03_LN_sdc_off_ldo_500nA/gainmeas_acq_Cap_0pf/"
#    fr_dir = f_dir + "results/"
#    if (os.path.exists(fr_dir)):
#        pass
#    else:
#        try:
#            os.makedirs(fr_dir)
#        except OSError:
#            print ("Error to create folder ")
#            exit()
#    
#    period = 200
#    avg_n = 50
#    fs = file_list(runpath=f_dir)
#    data_fs = []
#    for f in fs:
#        gain = "14mVfC"
#        if (f.find(tp)>=0) and (f.find(".bin")>0) and (f.find(BL)>0) and (f.find(gain)>0) and (f.find(SEDC)>0) and (f.find(SEBUF)>0):
#            tp = f[f.find("us")-2 : f.find("us")+2]
#            sg = f[f.find("mVfC")-2 : f.find("mVfC")+4]
#            dacv = int(f[f.find("asicdac")+7 : f.find("asicdac")+9])
#            if (dacv < 80 ):
#                print (f)
#                data_fs.append(f)
#            #if dacv>=3:
#            #    print (f)
#            #    data_fs.append(f)
#    
#    asic_cali = Asic_Cali(data_fs, mode16bit = mode16bit )
#
#    fpic = fr_dir + data_fs[0][:f.find("asicdac")]
#    chn_gains = []
#    chn_inls = []
#    for i in range(16):
#    #for i in range(1):
#        p= Chn_Plot(asic_cali, chnno = i, mode16bit = mode16bit , fpic= fpic )
#        #p = Chn_Ana(asic_cali, chnno = i, sg=sg)
#        chn_gains.append((p[5][0]))
#        chn_inls.append(p[5][2])
#
#    if (mode16bit):
#        adc_bits = "ADC16bit"
#    else:
#        adc_bits = "ADC12bit"
##    if "47" in sg:
##        sg = "78mVfC"
##    elif "78" in sg:
##        sg = "47mVfC"
#    csv_fn = fr_dir + testno_str + tp + sg + adc_bits + "BL%s"%BL + SEDC + SEBUF + ".csv"
#
#    with open(csv_fn, "w") as cfp:
#        cfp.write(",".join(str(i) for i in chn_gains) +  "," + "\n")
#        cfp.write(",".join(str(i) for i in chn_inls) +  "," + "\n")
#    
#    print (chn_gains)
#    print (csv_fn)
#
#
