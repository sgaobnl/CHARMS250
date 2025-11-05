# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 10:31:31 2018

@author: JunbinZhang
"""
class fe_defined:
    def __init__(self):
        self.ver = "P5"
        #-----------FE channel parameter----------#
        self.Input={'Direct_Input':0,'Test_Input':1}
        self.Baseline={'900mV':0,'200mV':1}
        self.Gain={'4.7mV/fC':0,'7.8mV/fC':1,'14mV/fC':2,'25mV/fC':3}
        self.Peaktime={'1us':0,'0.5us':1,'3us':2,'2us':3}
        self.Buffer={'off':0,'on':1}
        self.Mon={'off':0,'on':1}
        #----------FE global parameter------------#
        self.SGP = {"Enabled":0, "Disabled":1}
        self.SDD = {"Disabled":0, "Enabled":1}
        self.Coupled={'DC':0,'AC':1}
        self.Leakage={'500pA':0,'100pA':1,'5nA':2,'1nA':3} #[SLKH:SLK]
        self.S16={'Disconnect':0,'Connect':1}
        self.Monitor={'Analog':0,'Temp':1,'Bandgap':3}
        self.Pulse={'Disable':0,'External':1,'Internal':2,'ExtM':3}

    def fe_ver_sel(self):
        if "P2" in self.ver:
            pass
        elif "P3" in self.ver:
            self.ver= "P3"
            self.Gain={'4.7mV/fC':3,'7.8mV/fC':2,'14mV/fC':0,'25mV/fC':1}
        elif "P4" in self.ver:
            self.ver= "P4"
            self.Gain={'4.7mV/fC':3,'7.8mV/fC':2,'14mV/fC':0,'25mV/fC':1}
            self.SDD = {"Disabled": 0, "Enabled": 1}
        elif "P5" in self.ver:
            self.ver= "P5"
            self.SGP = {"Enbled":0, "Disabled":1}
            self.Gain={'4.7mV/fC':3,'7.8mV/fC':2,'14mV/fC':0,'25mV/fC':1}
            self.SDD = {"Disabled": 0, "Enabled": 1}

        print("LArASIC Version Update to: {}".format(self.ver))
