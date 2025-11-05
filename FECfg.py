# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:47:52 2019

@author: JunbinZhang
"""
from udp import UDP
from bit_op import Bit_Op
from fe_reg import FE_REG
from fe_defined import fe_defined
import time

import sys


# import os
# import sys

class FECfg:
    def __init__(self):
        self.bitop = Bit_Op()
        self.udp = UDP()
#        self.fpga_reg = FPGA_REG()
        self.fe_reg = FE_REG()
        self.fe_def = fe_defined()
#        self.fe_def.ver = "P3"
#        self.fe_def.fe_ver_sel()
        # ---parameter settings as a default----#
        # ---------FE_channel------------------#
        self.sts = [self.fe_def.Input['Direct_Input']] * 16
        self.snc = [self.fe_def.Baseline['900mV']] * 16
        self.sg = [self.fe_def.Gain['14mV/fC']] * 16
        self.st = [self.fe_def.Peaktime['2us']] * 16
        self.smn = [self.fe_def.Mon['off']] * 16
        self.sbf = [self.fe_def.Buffer['off']] * 16
        # ---------FE global----------------#
        self.sgp = self.fe_def.SGP['Enabled']
        self.sdd = self.fe_def.SDD['Disabled']
        self.sdacsw = self.fe_def.Pulse['Disable']
        self.sdc = self.fe_def.Coupled['DC']
        self.slkh = (self.fe_def.Leakage['500pA'] & 0x2) >> 1
        self.s16 = self.fe_def.S16['Disconnect']
        self.stb = self.fe_def.Monitor['Analog']
        self.slk = self.fe_def.Leakage['500pA'] & 0x1
        self.sdac = 0x5
        # -------------------------------------#

    def fe_chn_input(self, modes):
        for i in range(len(modes)):
            if modes[i] == 'Direct_Input':
                self.sts[i] = self.fe_def.Input['Direct_Input']
            else:
                self.sts[i] = self.fe_def.Input['Test_Input']

    def fe_chn_baseline(self, modes):
        for i in range(len(modes)):
            if modes[i] == "900mV":
                self.snc[i] = self.fe_def.Baseline['900mV']
            else:
                self.snc[i] = self.fe_def.Baseline['200mV']

    def fe_chn_gain(self, gains):
        for i in range(len(gains)):
            if gains[i] == "4.7mV/fC":
                self.sg[i] = self.fe_def.Gain['4.7mV/fC']
            elif gains[i] == "7.8mV/fC":
                self.sg[i] = self.fe_def.Gain['7.8mV/fC']
            elif gains[i] == "14mV/fC":
                self.sg[i] = self.fe_def.Gain['14mV/fC']
            else:
                self.sg[i] = self.fe_def.Gain['25mV/fC']

    def fe_chn_peaktime(self, modes):
        for i in range(len(modes)):
            if modes[i] == "1us":
                self.st[i] = self.fe_def.Peaktime['1us']
            elif modes[i] == "0.5us":
                self.st[i] = self.fe_def.Peaktime['0.5us']
            elif modes[i] == "2us":
                self.st[i] = self.fe_def.Peaktime['2us']
            else:
                self.st[i] = self.fe_def.Peaktime['3us']

    def fe_chn_monitor(self, modes):
        for i in range(len(modes)):
            if modes[i] == "off":
                self.smn[i] = self.fe_def.Mon['off']
            else:
                self.smn[i] = self.fe_def.Mon['on']

    def fe_chn_buffer(self, modes):
        for i in range(len(modes)):
            if modes[i] == "off":
                self.sbf[i] = self.fe_def.Buffer['off']
            else:
                self.sbf[i] = self.fe_def.Buffer['on']

# ---------FE global register settings---------#
    def fe_pulse_src(self, mode):
        if mode == "Disable":
            self.sdacsw = self.fe_def.Pulse['Disable']
        elif mode == "External":
            self.sdacsw = self.fe_def.Pulse['External']
        elif mode == "Internal":
            self.sdacsw = self.fe_def.Pulse['Internal']
        else:
            self.sdacsw = self.fe_def.Pulse['ExtM']

    def fe_Coupled(self, mode):
        if mode == "DC":
            self.sdc = self.fe_def.Coupled['DC']
        else:
            self.sdc = self.fe_def.Coupled['AC']

    def fe_Leakage(self, mode):
        if mode == "500pA":
            self.slkh = (self.fe_def.Leakage['500pA'] & 0x2) >> 1
            self.slk = self.fe_def.Leakage['500pA'] & 0x1
        elif mode == "100pA":
            self.slkh = (self.fe_def.Leakage['100pA'] & 0x2) >> 1
            self.slk = self.fe_def.Leakage['100pA'] & 0x1
        elif mode == "5nA":
            self.slkh = (self.fe_def.Leakage['5nA'] & 0x2) >> 1
            self.slk = self.fe_def.Leakage['5nA'] & 0x1
        else:
            self.slkh = (self.fe_def.Leakage['1nA'] & 0x2) >> 1
            self.slk = self.fe_def.Leakage['1nA'] & 0x1

    def fe_monitor_type(self, mode):
        if mode == "Analog":
            self.stb = self.fe_def.Monitor['Analog']
        elif mode == "Temp":
            self.stb = self.fe_def.Monitor['Temp']
        else:
            self.stb = self.fe_def.Monitor['Bandgap']

    def fe_sdac(self, dac):
        self.sdac = dac

    def fe_sdd_type(self, mode):
        if ("P4" in self.fe_def) or ("P5" in self.fe_def):
            if mode == "Disabled":
                self.sdd = self.fe_def.SDD['Disabled']
            else:
                self.sdd = self.fe_def.SDD['Enabled']
        else:
            self.sdd = self.fe_def.SDD['Disabled']
        # -----------------------------------------------#

    def fe_sgp_type(self, mode):
        if "P5" in self.fe_def:
            if mode == "Disabled":
                self.sgp = self.fe_def.SGP['Disabled']
            else:
                self.sgp = self.fe_def.SGP['Enabled']
        else:
            self.sgp = self.fe_def.SGP['Enabled']

    def fe_spi_config(self):
        # write twice in order to get the feedback
        # generate data.
        for chn in range(16):
            self.fe_reg.FE_CHN[chn].fe_chn_reg(self.sts[chn], self.snc[chn], self.sg[chn], self.st[chn], self.smn[chn],
                                               self.sbf[chn])  # change parameter here
        self.fe_reg.FE_GLOBAL.fe_glbl_reg(self.sdc, self.slkh, self.s16, self.stb, self.slk, self.sdac, self.sdacsw, self.sdd)

        fe_spi_data = self.fe_reg.spi_data()
        time.sleep(0.001)
        for times in range(2):
            for i in range(len(fe_spi_data)):
                # load data
                self.udp.write_mask_checked(0x200 + i, 0xffffffff, fe_spi_data[i])
                time.sleep(0.001)
            # write SPI
            self.udp.write_mask_checked(8, 0x01, 1)
            time.sleep(0.05)
            self.udp.write_mask_checked(8, 0x01, 0)
        else:  # Check if there are something wrong and get the feedback
            spi_data_fb = []
            time.sleep(0.05)  # need a delay here too fast
            for i in range(len(fe_spi_data)):
                spi_data_fb.append(self.udp.read_mask(0x250 + i, mask=0xffffffff))
                time.sleep(0.001)
            # print(spi_data_fb)
            p = [i for i, j in enumerate(zip(spi_data_fb, fe_spi_data)) if all(j[0] != k for k in j[1:])]
            if not p:
                # print('FE SPI configuration success') #feadback is equels to the original
                time.sleep(0.001)
            else:
                print('FE SPI configuration failed!')
                #break
                #continue
        time.sleep(0.001)

    def fe_pulse_config(self, mode):
        # -------------register 0x12------------------------#
        # bit0 FPGA_TP_EN, set to enable FPGA calibration DAC
        # bit1 ASIC_TP_EN, set to enable ASIC calibration, pulse will be sent to ASIC ck pin
        # bit2 INT_TP_EN, set to enable internal pulse generator,period set by register 5
        # bit3 DAC_SELECT, select analog pulse source, 0= FM on board DAC;1=Analog pulse from the WIB
        # bit4 EXT_TP_EN, set to allow test pulses to be received by external timing control interface,register 5 delay & amplitude can be used.
        if (mode == "External"):
            # self.udp.write_reg(0xc,0x39)
            self.udp.write_reg(0xc, 0)
            time.sleep(0.001)
            self.udp.write_mask_checked(reg=0x0c, mask=0x8, data=1)  # select analog pulse source(FPGA-DAC or ASIC-DAC)
            time.sleep(0.001)
            self.udp.write_mask_checked(reg=0x0c, mask=0x1, data=1)  # select FPGA-DAC enable
            time.sleep(0.001)
            self.udp.write_mask_checked(reg=0x0c, mask=0x4, data=1)  # select Internal DAC (on board)

        elif (mode == "Internal"):
            # self.udp.write_reg(0xc,0x56)
            self.udp.write_reg(0xc, 0)
            time.sleep(0.001)
            self.udp.write_mask_checked(reg=0x0c, mask=0x8, data=1)  # select analog pulse source(FPGA-DAC or ASIC-DAC)
            time.sleep(0.001)
            self.udp.write_mask_checked(reg=0x0c, mask=0x2, data=1)  # select ASIC-DAC enable
            time.sleep(0.001)
            self.udp.write_mask_checked(reg=0x0c, mask=0x4, data=1)  # select Internal DAC (on board)
        else:  # No pulse, RMS mode
            self.udp.write_reg(0xc, 0x0)
        # Pulse paramter settings


    def fe_pulse_param(self, delay, period, width):
        # -------------register 0x05------------------------#
        # bit15:8, TEST_PULSE_DELAY,Controls test pulse sample shift by 10ns step, 0=0, 1=10ns, 2= 20ns ...
        # bit31:16,TEST_PULSE_PERIOD, set to control test pulse period(dependent on ADC SAMPLE RATE) 0=500ns, 01=1us, 02=1.5us
        # Note: Amplitude here affects FPGA dac only, delay and period affect FPGA_DAC and ASIC_DAC both 1lsb = 1.8V/64 = 0.028125
        self.udp.write_mask_checked(reg=0x0e, mask=0xff00, data=delay)
        self.udp.write_mask_checked(reg=0x0e, mask=0xffff0000, data=period)
        self.udp.write_mask_checked(reg=0x0d, mask=0xffffffff, data=width)

    def fe_fpga_dac(self, amp):
        # bit5:0, TEST_PULSE_AMPLITUDE, set to control 5 bit DAC for test pulse, 0=disable,1=DAC LSB 2=2LSB ....
        self.udp.write_mask_checked(reg=0x0e, mask=0x003f, data=amp)
