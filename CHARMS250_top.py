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

brd = BoardCfg()


if True:
    #CHRAMS Reset
    brd.charms_reset()
    #I2C operation format
    #brd.charms_i2c_wr(CH=0x00, REG_Addr=0x00, REG_Val=0x00)
    #Reg_Val_rd = brd.charms_i2c_rd(CH=0x00, REG_Addr=0x00)
    
    #sdf=1
    #brd.charms_i2c_wr(0x00,0x00, 0x01) 
    #sdd=1
    #brd.charms_i2c_wr(0x00,0x00, 0x02) 
    
##changed to interal refernce 
    #Internal Referenc3
    CH = 0xFF 
    REG_Addr = 0x09
    Reg_Val_wr = 0x00
    brd.charms_i2c_wr(CH=CH,REG_Addr=REG_Addr, REG_Val=Reg_Val_wr) 
    Reg_Val_rd = brd.charms_i2c_rd(CH=CH,REG_Addr=REG_Addr) 
    print ("Reg_Val_rd = %x"%Reg_Val_rd)
##


    #sdf=1
    #brd.charms_i2c_wr(0x00,0x00, 0x01) 
    #sdd=1
    #brd.charms_i2c_wr(0x00,0x00, 0x02) 
    #
    #brd.charms_i2c_wr(0x00,0x01, 0x30) 
    brd.charms_i2c_wr(0x00,0x01, 0x20) 
   
##changed to interal refernce 
#    CH = 0x00 
#    REG_Addr = 0x02
#    Reg_Val_wr = 0x04
#    brd.charms_i2c_wr(CH=CH,REG_Addr=REG_Addr, REG_Val=Reg_Val_wr) 
#    Reg_Val_rd = brd.charms_i2c_rd(CH=CH,REG_Addr=REG_Addr) 
#    print ("Reg_Val_rd = %x"%Reg_Val_rd)
    
#


