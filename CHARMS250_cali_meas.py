#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 17 16:54:11 2019

@author: shanshangao
"""
# This file takes care of the full configuration of ColdADC. 
# Input: reference, SDC enable, calibration weights (new or old), sampling rate.
# Set sampling rate, power supply configuration (different between BJT and CMOS references), configure ADC itself.


from BoardCfg import BoardCfg
import time
import sys
import os
import pickle

brd = BoardCfg()

# From ADC configuration file (adc_config.py): temperature and directory name
rawdir = "D:/CHARMS250/data/Ext_Cali/"
# Input options from batch file: reference, SDC enable, weights selection, system sample rate
# ADC Sample Rate = 16   ->
# 16 Ms/s sample rate of internal ADC, 2 MHz sample rate of full system ADC (not fully reliable operation)

# ADC Sample Rate = 4    ->
# 4 Ms/s sample rate of internal ADC, 500 kHz sample rate of full system ADC (reliable operation)

adc_cfg_flg = "ADC" in sys.argv[1]
if adc_cfg_flg: #
    #flg_bjt_r = "BJT" in sys.argv[1]  # BJR reference flag
    flg_bjt_r = False #'CMOS'
    #adc_sdc_en = "ON" in sys.argv[2]  # "SDC_ON"
    adc_sdc_en = False # "SDC_OFF"
    #adc_db_en = "ON" in sys.argv[3]  # "DB_ON")
    adc_db_en = False #"ON" in sys.argv[3]  # "DB_ON")
    
    #adc_sha_en = "Single" in sys.argv[4]  # "SHA_Single_Ended
    adc_sha_en = True #"Single" in sys.argv[4]  # "SHA_Single_Ended
    #adc_sha_en = False #"Single" in sys.argv[4]  # "SHA_Single_Ended
    
    
    #adc_sample_rate = sys.argv[5]  # 4 Ms/s internal ADC sample rate flag
    adc_sample_rate = "16"
    #adc_direct_en = (sys.argv[6] == "ADCinput")  # 4 Ms/s internal ADC sample rate flag
    adc_direct_en = False #(sys.argv[6] == "ADCinput")  # 4 Ms/s internal ADC sample rate flag
    # clk10m_syn_en = (sys.argv[5] == "SYNC10M" ) #10MHz sync out
    brd.udp.write_reg_checked(0x05, 0)
    # reg5[0]: 0->-16Ms/s, 1--> 4Ms/s
    # reg5[1]: 0->-10MHz sync out enable,  1--> disable
    # reg5[4]: 0--> 2MHz & 64MHz enable, 1 --> disable
    if "4" in adc_sample_rate:
        brd.sample_rate_set(sr=4)
    else:
        brd.sample_rate_set(sr=16)
    
    
    ref = "BJT" if flg_bjt_r else "CMOS"
    reffp = "bjt.bjt"if flg_bjt_r else "cmos.cmos"
    sdc = "ON" if adc_sdc_en else "OFF"
    db = "ON" if adc_db_en else "OFF"
    sha = "Single-Ended" if adc_sha_en else "Diff"
    
    brd.brd_adc_init(ref=ref, sdc=sdc, db=db, sha=sha)
    brd.adc.adc_write(page=1, addr=0x81,data=0x03)
#    brd.adc.adc_write(page=1, addr=0x89,data=0x28) #ADC direct input

    #if not os.path.isfile(ref_set_dir + reffp):
    #    brd.ref_set_find(ref_set_dir + reffp)

    #brd.brd_adc_init(ref=ref, sdc=sdc, db=db, sha=sha)
    #brd.ref_set(fp=ref_set_dir + reffp)


if True:
    #CHRAMS Reset
    brd.charms_reset()
    
    #sdf=1
    brd.charms_i2c_wr(0x00,0x00, 0x00) 
    #sdd=1
    #brd.charms_i2c_wr(0x00,0x00, 0x02) 
    
    #Internal Referenc3
    brd.charms_i2c_wr(0xff,0x09, 0x80) #changed to interal refernce 
    brd.charms_i2c_rd(0xff,0x09) 
    #BL=200
    brd.charms_i2c_wr(0x00,0x02, 0x04) 
    #brd.charms_i2c_rd(0x00,0x02) 

    
    #brd.charms_i2c_wr(0x00,0x00, 0x04) #SMN enabled
    #brd.charms_i2c_wr(0x00,0x00, 0x00) #SMN disabled
    brd.charms_i2c_wr(0x00,0x00, 0x05) #SMN enabled

    brd.charms_i2c_wr(0x00,0x03, 0x02) 
    #brd.charms_i2c_wr(0x00,0x03, 0x04) 
    
#    #test cal pulse enabled
    brd.charms_i2c_wr(0x00,0x01, 0x38) 
    #brd.charms_i2c_wr(0x00,0x03, 0x04) 
#
#    fn = rawdir + f"pls60mV.bin"
#    if os.path.exists(fn):
#        print (f'{fn} exists, change the file name')
#        fname = input ("Please rename : ")
#        fn = rawdir + fname + ".bin"
#    else:
#        pass
#    chns = brd.get_adcdata(PktNum=100000, saveraw=True, fn=fn)
#

if False:
    brd.charms_i2c_wr(0x00,0x02, 0x04) 
    for tp in (0,1,2,3):
        for gain in (0,1,2,3):
            brd.charms_reset()
            #Internal Referenc3
            brd.charms_i2c_wr(0xff,0x09, 0x80) #changed to interal refernce 
            brd.charms_i2c_rd(0xff,0x09) 
            #BL=200
            #brd.charms_i2c_wr(0x00,0x02, 0x04) 
            #brd.charms_i2c_rd(0x00,0x02) 

            brd.charms_i2c_wr(0x00,0x03, (tp|(gain<<2))&0xff) 
            time.sleep(1)
            fn = rawdir + f"Ext_Cali20mV_BL900mV_tp{tp}_gain{gain}.bin"
            if os.path.exists(fn):
                print (f'{fn} exists, change the file name')
                fname = input ("Please rename : ")
                fn = rawdir + fname + ".bin"
            else:
                pass
            chns = brd.get_adcdata(PktNum=100000, saveraw=True, fn=fn)

if False:#Bbias_cst
    while True:
        for x in range(127):
            if x == 0:
                brd.charms_reset()
                brd.charms_i2c_wr(0xff,0x03, 0x50) #SMN enabled
                time.sleep(0.001)
            else:
                brd.charms_i2c_wr(0xff,0x03, x-1) #SMN enabled
                time.sleep(0.001)
            brd.charms_i2c_wr(0xff,0x03, x) #SMN enabled
            time.sleep(0.01)

