# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:47:52 2019

@author: JunbinZhang
"""
from udp import UDP
from bit_op import Bit_Op
from ColdadcCfg import ColdadcCfg
from FECfg import FECfg
import time
import sys
import pickle
from raw_data_decoder import raw_conv

# import os


class BoardCfg:
    def udp_fifo_clear(self):
        self.udp.write_mask(reg=0x01, mask=0x04, data=1)
        self.udp.write_mask(reg=0x01, mask=0x04, data=1)
        time.sleep(0.01)
        self.udp.write_mask(reg=0x01, mask=0x04, data=0)

    def Acq_start_stop(self, Val):
        if Val == 1:
            self.udp_fifo_clear()
            self.udp.write_reg_checked(reg=0x0f, data=1)
        else:
            self.udp.write_reg_checked(reg=0x0f, data=0)
        time.sleep(0.01)

    def get_adcdata(self, PktNum=128, saveraw=False, fn=""):
        self.Acq_start_stop(1)
        rawdata = self.udp.get_pure_rawdata(PktNum + 1000)
        self.Acq_start_stop(0)
        if (saveraw):
            with open(fn, 'wb') as f:
                pickle.dump(rawdata, f)
        chns = raw_conv(rawdata, PktNum)[0]
        return chns

    def init_chk(self):
        # Hard reset ADC -> Read register
        # 0 -> Soft reset (necessary for default page 2 registers, recently discovered problem)
#        self.Acq_start_stop(0)
        print("ADC hard reset after power on")
        self.adc.hard_reset()
        init_str = self.adc.adc_read(page=1, addr=0x80)
        if init_str != '0xA3':
            status = "FAIL"
            err_log = "Initialization check failed. Read/Write not working correctly. \n Exit anyway!"
        self.adc.soft_reset()

    def cots_adc_data(self, avr=5):
        result = 0
        for i in range(avr + 2):
            self.udp.write_mask_checked(reg=0x11, mask=0x1, data=1)
            check_done = 1
            while check_done:
                check_done = self.udp.read_mask(reg=0x13, mask=0x1)
                time.sleep(0.001)
            temp = self.udp.read_mask(reg=0x12, mask=0x0fff)
            self.udp.write_mask_checked(reg=0x11, mask=0x1, data=0)
            if i > 1:
                result = result + temp
            time.sleep(0.001)
        else:
            code = result / avr
            amp = int(code)
            # ---conversion---#
            amp = code * 2.5 / 4096
        return amp

    def ref_vmon(self, vmon="VBGR", avg_points=5):
        #self.udp.write_mask(reg=7, mask=7, data=3)  # "VOLTAGE_MON"
        self.cots_adc_mux_mon_src(src="VOLTAGE_MON")
        self.adc.adc_write_mask(page=1, addr=0x80 + 47, mask=0x1, data=1)
        if "VBGR" in vmon:
            vval = 0
        elif "VCMI" in vmon:
            vval = 1
        elif "VCMO" in vmon:
            vval = 2
        elif "VREFP" in vmon:
            vval = 3
        elif "VREFN" in vmon:
            vval = 4
        elif "VBGR" in vmon:
            vval = 5
        elif "VSSA" in vmon:
            vval = 6
        else:
            vval = 7
        self.adc.adc_write_mask(page=1, addr=0x80 + 47, mask=0x1c, data=vval)
        val = self.cots_adc_data(avr=avg_points)
        self.adc.adc_write_mask(page=1, addr=0x80 + 47, mask=0x1, data=0)
        return val

    def ref_imon(self, imon="ICMOS_REF_5k", avg_points=5):
        self.cots_adc_mux_mon_src(src="CURRENT_MON")
        self.adc.adc_write_mask(page=1, addr=0x80 + 47, mask=0x2, data=1)
        ival = self.cost_adc_i_mon_select(imon)
        self.adc.adc_write_mask(page=1, addr=0x80 + 47, mask=0xe0, data=ival)
        val = self.cots_adc_data(avr=avg_points)
        self.adc.adc_write_mask(page=1, addr=0x80 + 47, mask=0x2, data=0)
        return val

    def cost_adc_i_mon_select(self, src):
        if src == "ICMOS_REF_5k":
            val = 0
        elif src == "ISHA0_5k":
            val = 1
        elif src == "IADC0_5k":
            val = 2
        elif src == "ISHA1_5k":
            val = 3
        elif src == "IADC1_5k":
            val = 4
        elif src == "IBUFF_CMOS":
            val = 5
        elif src == "IREF_5k":
            val = 6
        elif src == "IREFBUFFER0":
            val = 7
        return val

    def ref_vmons(self):
        vcmi = self.ref_vmon(vmon="VCMI")
        vcmo = self.ref_vmon(vmon="VCMO")
        vrefp = self.ref_vmon(vmon="VREFP")
        vrefn = self.ref_vmon(vmon="VREFN")
        return (vcmi, vcmo, vrefp, vrefn)

    def cots_adc_bjt_mon_src(self, src):
        if src == "None":
            reg20 = 0x0
            reg21 = 0x0
        elif src == "VREF_ext":
            reg20 = 0x1
            reg21 = 0x0
        elif src == "VREFN":
            reg20 = 0x2
            reg21 = 0x0
        elif src == "VREFP":
            reg20 = 0x4
            reg21 = 0x0
        elif src == "VCMI":
            reg20 = 0x8
            reg21 = 0x0
        elif src == "VCMO":
            reg20 = 0x10
            reg21 = 0x0
        elif src == "VBGR_1.2V":
            reg20 = 0x0
            reg21 = 0x80
        elif src == "Vdac0_5k":
            reg20 = 0x20
            reg21 = 0x0
        elif src == "Vdac1_5k":
            reg20 = 0x40
            reg21 = 0x0
        elif src == "ibuff0_5k":
            reg20 = 0x80
            reg21 = 0x0
        elif src == "ibuff1_5k":
            reg20 = 0x0
            reg21 = 0x1
        elif src == "Isink_adc1_5k":
            reg20 = 0x0
            reg21 = 0x2
        elif src == "Isink_adc0_5k":
            reg20 = 0x0
            reg21 = 0x4
        elif src == "Isink_sha1_5k":
            reg20 = 0x0
            reg21 = 0x8
        elif src == "Isink_sha0_5k":
            reg20 = 0x0
            reg21 = 0x10
        elif src == "Isink_refbuf0_5k":
            reg20 = 0x0
            reg21 = 0x20
        elif src == "Isink_refbuf1_5k":
            reg20 = 0x0
            reg21 = 0x40
        self.adc.adc_write_mask(page=1, addr=0x80 + 20, mask=0xff, data=reg20)
        self.adc.adc_write_mask(page=1, addr=0x80 + 21, mask=0xff, data=reg21)

    # MUX output selection
    def cots_adc_mux_mon_src(self, src):
        if src == "AUX_ISINK":
            val = 0
        elif src == "AUX_VOLTAGE":
            val = 1
        elif src == "AUX_ISOURCE":
            val = 2
        elif src == "VOLTAGE_MON":
            val = 3
        elif src == "CURRENT_MON":
            val = 4
        self.udp.write_mask_checked(reg=7, mask=7, data=val)

    def bjt_ref_aux(self, mon_src="VREFP", mux_src="AUX_VOLTAGE", avg_points=5):
        self.cots_adc_bjt_mon_src(src=mon_src)
        self.cots_adc_mux_mon_src(src=mux_src)
        val = self.cots_adc_data(avr=avg_points)
        return val

    def all_bjt_ref_auxs(self):
        vref = self.bjt_ref_aux(mon_src="VREF_ext", mux_src="AUX_VOLTAGE")
        vrefn = self.bjt_ref_aux(mon_src="VREFN", mux_src="AUX_VOLTAGE")
        vrefp = self.bjt_ref_aux(mon_src="VREFP", mux_src="AUX_VOLTAGE")
        vcmi = self.bjt_ref_aux(mon_src="VCMI", mux_src="AUX_VOLTAGE")
        vcmo = self.bjt_ref_aux(mon_src="VCMO", mux_src="AUX_VOLTAGE")
        vbgr = self.bjt_ref_aux(mon_src="VBGR_1.2V", mux_src="AUX_VOLTAGE")
        vdac0_5k = self.bjt_ref_aux(mon_src="Vdac0_5k", mux_src="AUX_ISOURCE")
        vdac1_5k = self.bjt_ref_aux(mon_src="Vdac1_5k", mux_src="AUX_ISOURCE")
        ibuff0_5k = self.bjt_ref_aux(mon_src="ibuff0_5k", mux_src="AUX_ISOURCE")
        ibuff1_5k = self.bjt_ref_aux(mon_src="ibuff1_5k", mux_src="AUX_ISOURCE")
        isink_adc1_5k = self.bjt_ref_aux(mon_src="Isink_adc1_5k", mux_src="AUX_ISINK")
        isink_adc0_5k = self.bjt_ref_aux(mon_src="Isink_adc0_5k", mux_src="AUX_ISINK")
        isink_sha1_5k = self.bjt_ref_aux(mon_src="Isink_sha1_5k", mux_src="AUX_ISINK")
        isink_sha0_5k = self.bjt_ref_aux(mon_src="Isink_sha0_5k", mux_src="AUX_ISINK")
        isink_refbuf0_5k = self.bjt_ref_aux(mon_src="Isink_refbuf0_5k", mux_src="AUX_ISINK")
        isink_refbuf1_5k = self.bjt_ref_aux(mon_src="Isink_refbuf1_5k", mux_src="AUX_ISINK")
        return (vref, vrefn, vrefp, vcmi, vcmo, vbgr, vdac0_5k, vdac1_5k, ibuff0_5k, ibuff1_5k,
                isink_adc1_5k, isink_adc0_5k, isink_sha1_5k, isink_sha0_5k, isink_refbuf0_5k, isink_refbuf1_5k)

    def all_ref_vmons(self):
        vbgr = self.ref_vmon(vmon="VBGR")
        vcmi = self.ref_vmon(vmon="VCMI")
        vcmo = self.ref_vmon(vmon="VCMO")
        vrefp = self.ref_vmon(vmon="VREFP")
        vrefn = self.ref_vmon(vmon="VREFN")
        vssa = self.ref_vmon(vmon="VSSA")
        return vbgr, vcmi, vcmo, vrefp, vrefn, vssa

    def ref_set_find(self, fp):
        self.adc.adc_cfg_all()
        self.vp_vcmi = False
        self.vn_vcmi = False
        self.vm_vcmi = False
        self.vp_vcmo = False
        self.vn_vcmo = False
        self.vm_vcmo = False
        self.vp_vrefp = False
        self.vn_vrefp = False
        self.vm_vrefp = False
        self.vp_vrefn = False
        self.vn_vrefn = False
        self.vm_vrefn = False
        if self.adc.ref == "CMOS":
            self.vrefp_voft = self.adc.adc_read(page=1, addr=0x80 + 24)
            self.vrefn_voft = self.adc.adc_read(page=1, addr=0x80 + 25)
            self.vcmo_voft = self.adc.adc_read(page=1, addr=0x80 + 26)
            self.vcmi_voft = self.adc.adc_read(page=1, addr=0x80 + 27)
        else:
            self.vrefp_voft = self.adc.adc_read(page=1, addr=0x80 + 10)
            self.vrefn_voft = self.adc.adc_read(page=1, addr=0x80 + 11)
            self.vcmo_voft = self.adc.adc_read(page=1, addr=0x80 + 12)
            self.vcmi_voft = self.adc.adc_read(page=1, addr=0x80 + 13)

        for tmp in range(257):
            if self.adc.ref == "CMOS":
                print("CMOS reference is being calibrated !")
                self.adc.cmos_vrefp = self.vrefp_voft
                self.adc.cmos_vrefn = self.vrefn_voft
                self.adc.cmos_vcmi = self.vcmi_voft
                self.adc.cmos_vcmo = self.vcmo_voft
            else:
                print("BJT reference is being calibrated !")
                self.adc.bjt_vrefp = self.vrefp_voft
                self.adc.bjt_vrefn = self.vrefn_voft
                self.adc.bjt_vcmi = self.vcmi_voft
                self.adc.bjt_vcmo = self.vcmo_voft
            self.adc.adc_set_ref_values()
            vbgr, vcmi, vcmo, vrefp, vrefn, vssa = self.all_ref_vmons()
            vrefp_f = False
            vrefn_f = False
            vcmi_f = False
            vcmo_f = False
            if not ((self.vp_vrefp and self.vn_vrefp) or self.vm_vrefp):
                self.vrefp_voft, self.vp_vrefp, self.vn_vrefp, self.vm_vrefp = \
                    self.find_ref(self.vrefp_voft, self.vp_vrefp, self.vn_vrefp, self.vm_vrefp, vread=vrefp,
                                  vset=1.95)
            else:
                vrefp_f = True
            if not ((self.vp_vrefn and self.vn_vrefn) or self.vm_vrefn):
                self.vrefn_voft, self.vp_vrefn, self.vn_vrefn, self.vm_vrefn = \
                    self.find_ref(self.vrefn_voft, self.vp_vrefn, self.vn_vrefn, self.vm_vrefn, vread=vrefn,
                                  vset=0.45)
            else:
                vrefn_f = True
            if not ((self.vp_vcmi and self.vn_vcmi) or self.vm_vcmi):
                self.vcmi_voft, self.vp_vcmi, self.vn_vcmi, self.vm_vcmi = \
                    self.find_ref(self.vcmi_voft, self.vp_vcmi, self.vn_vcmi, self.vm_vcmi, vread=vcmi, vset=0.90)
            else:
                vcmi_f = True
            if not ((self.vp_vcmi and self.vn_vcmi) or self.vm_vcmo):
                self.vcmo_voft, self.vp_vcmo, self.vn_vcmo, self.vm_vcmo = \
                    self.find_ref(self.vcmo_voft, self.vp_vcmo, self.vn_vcmo, self.vm_vcmo, vread=vcmo, vset=1.20)
            else:
                vcmo_f = True

            print("VREFP = %.3f, VREFN = %.3f, VCMO = %.3f, VCMI = %.3f" % (vrefp, vrefn, vcmo, vcmi))
            print("VREFP = %x, VREFN = %x, VCMO = %x, VCMI = %x" % (
                self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft))
            if vrefp_f and vrefn_f and vcmi_f and vcmo_f:
                print("VREFP = %.3f, VREFN = %.3f, VCMO = %.3f, VCMI = %.3f" % (vrefp, vrefn, vcmo, vcmi))
                print(hex(self.vrefp_voft), hex(self.vrefn_voft), hex(self.vcmo_voft), hex(self.vcmi_voft))
                break

            with open(fp, 'wb+') as f:
                vref_regs = [self.vrefp_voft, self.vrefn_voft, self.vcmo_voft, self.vcmi_voft]
                vref_values = [vbgr, vrefp, vrefn, vcmo, vcmi, vssa]
                pickle.dump([vref_regs, vref_values], f)

            if tmp == 256:
                print("Proper Reference can't be found, please check setup! Exit anyway!")
                sys.exit()

    def find_ref(self, vreg, vp, vn, vm, vread, vset):
        if vp and vn:
            pass
        else:
            if vread > (vset + 0.01):
                vreg -= 1
                vp = True
            elif vread < (vset - 0.01):
                vreg += 1
                vp = vp
                vn = True
            else:
                vreg = vreg
                vm = True
        return vreg, vp, vn, vm

    def ref_set(self, fp):
        with open(fp, 'rb') as f:
            vref_regs, vref_values = pickle.load(f)
        if self.adc.ref == "BJT":
            self.adc.bjt_vrefp, self.adc.bjt_vrefn, self.adc.bjt_vcmo, self.adc.bjt_vcmi = vref_regs
        else:
            self.adc.cmos_vrefp, self.adc.cmos_vrefn, self.adc.cmos_vcmo, self.adc.cmos_vcmi = vref_regs
        self.adc.adc_set_ref_values()

    def brd_adc_init(self, ref="CMOS", sdc="OFF", db="OFF", sha="Single-Ended"):
        self.adc.re_init()
        self.adc.ref = ref
        self.adc.sdc = sdc
        self.adc.db = db
        self.adc.sha = sha
        self.adc.adc_cfg_all()

    def bjt_set_ioffset(self, vrefp_c, vrefn_c, vcmo_c, vcmi_c):
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0e, mask=0x03, data=vrefp_c)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0e, mask=0x0c, data=vrefn_c)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0e, mask=0x30, data=vcmo_c)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0e, mask=0xc0, data=vcmi_c)

    def bjt_set_vrefs(self, vrefp_c, vrefn_c, vcmo_c, vcmi_c):
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0a, mask=0xff, data=vrefp_c)
        time.sleep(0.001)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0b, mask=0xff, data=vrefn_c)
        time.sleep(0.001)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0c, mask=0xff, data=vcmo_c)
        time.sleep(0.001)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x0d, mask=0xff, data=vcmi_c)

    def bjt_set_curr_vdac(self, vdac0, vdac1):
        self.adc.adc_write_mask(page=1, addr=0x80 + 17, mask=0xff, data=vdac0)
        self.adc.adc_write_mask(page=1, addr=0x80 + 18, mask=0xff, data=vdac1)

    def bjt_set_curr_ibuff(self, ibuff0, ibuff1):
        self.adc.adc_write_mask(page=1, addr=0x80 + 15, mask=0xff, data=ibuff0)
        self.adc.adc_write_mask(page=1, addr=0x80 + 16, mask=0xff, data=ibuff1)

    # CMOS reference
    def adc_set_cmos_vrefs(self, vrefp_c, vrefn_c, vcmi_c, vcmo_c):
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x18, mask=0xff, data=vrefp_c)
        time.sleep(0.001)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x19, mask=0xff, data=vrefn_c)
        time.sleep(0.001)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x1a, mask=0xff, data=vcmi_c)
        time.sleep(0.001)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x1b, mask=0xff, data=vcmo_c)

    def adc_set_cmos_ibuff(self, ibuff0, ibuff1):
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x1d, mask=0x3f, data=ibuff0)
        self.adc.adc_write_mask(page=1, addr=0x80 + 0x1e, mask=0x3f, data=ibuff1)


    def refs_chk(self, flg_bjt=True):
        # Sweeps reference voltages and currents
#        err_log = []
#        pass_log = []
        avgs = 1
        if flg_bjt:
            self.brd_adc_init(ref="BJT", sdc="OFF", db="OFF", sha="Single-Ended")
            vbgr = self.ref_vmon(vmon="VBGR")
#            if vbgr > 1.3 or vbgr < 1.1:
#                status = "FAIL"
#                err_log.append("Bandgap Reference out of expected range: VBGR = %0.3f \n" % vbgr)
#            else:
#                pass_log.append("Bandgap reference: PASS \n")

            vrefp_bjt = []
            vrefn_bjt = []
            vcmi_bjt = []
            vcmo_bjt = []
            ibuff0_bjt = []
            ibuff1_bjt = []
            ivdac0_bjt = []
            ivdac1_bjt = []
            for j in range(avgs):
                if j == 0:
                    # Codes between 0 and 256. Take data every 15
                    for i in range(0, 256, 1):
                        # Set and collect IBUFF and IDAC values
                        self.bjt_set_curr_ibuff(i, i)
                        ibuff0_bjt.append(self.bjt_ref_aux("ibuff0_5k", "AUX_ISOURCE"))
                        ibuff1_bjt.append(self.bjt_ref_aux("ibuff1_5k", "AUX_ISOURCE"))
                        self.bjt_set_curr_vdac(i, i)
                        ivdac0_bjt.append(self.bjt_ref_aux("Vdac0_5k", "AUX_ISOURCE"))
                        ivdac1_bjt.append(self.bjt_ref_aux("Vdac1_5k", "AUX_ISOURCE"))
                        # Set and collect VREFs values
                        self.bjt_set_vrefs(i, i, i, i)
                        time.sleep(0.01)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        print("BJT", i, vcmi_i, vcmo_i, vrefp_i, vrefn_i)
                        vcmi_bjt.append(vcmi_i)
                        vcmo_bjt.append(vcmo_i)
                        vrefp_bjt.append(vrefp_i)
                        vrefn_bjt.append(vrefn_i)
                else:
                    # Only for avgs > 1
                    for i in range(0, 256, 1):
                        # for i in range (0,256,1):
                        self.bjt_set_vrefs(i, i, i, i)
                        time.sleep(0.1)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        vcmi_bjt[i] += vcmi_i
                        vcmo_bjt[i] += vcmo_i
                        vrefp_bjt[i] += vrefp_i
                        vrefn_bjt[i] += vrefn_i
                        self.bjt_set_curr_ibuff(i, i)
                        ibuff0_bjt[i] += self.bjt_ref_aux("ibuff0_5k", "AUX_ISOURCE")
                        ibuff1_bjt[i] += self.bjt_ref_aux("ibuff1_5k", "AUX_ISOURCE")
                        self.bjt_set_curr_vdac(i, i)
                        ivdac0_bjt[i] += self.bjt_ref_aux("Vdac0_5k", "AUX_ISOURCE")
                        ivdac1_bjt[i] += self.bjt_ref_aux("Vdac1_5k", "AUX_ISOURCE")
            vrefp_bjt[:] = [x / avgs for x in vrefp_bjt]
            vrefn_bjt[:] = [x / avgs for x in vrefn_bjt]
            vcmi_bjt[:] = [x / avgs for x in vcmi_bjt]
            vcmo_bjt[:] = [x / avgs for x in vcmo_bjt]
            ibuff0_bjt[:] = [x / avgs for x in ibuff0_bjt]
            ibuff1_bjt[:] = [x / avgs for x in ibuff1_bjt]
            ivdac0_bjt[:] = [x / avgs for x in ivdac0_bjt]
            ivdac1_bjt[:] = [x / avgs for x in ivdac1_bjt]
            return vrefp_bjt, vrefn_bjt, vcmi_bjt, vcmo_bjt, ibuff0_bjt, ibuff1_bjt, ivdac0_bjt, ivdac1_bjt

        else:
            # Repeat same procedure for CMOS references
            self.brd_adc_init(ref="CMOS", sdc="OFF", db="OFF", sha="Single-Ended")
            vrefp_cmos = []
            vrefn_cmos = []
            vcmi_cmos = []
            vcmo_cmos = []
            ibuff_cmos = []
            for j in range(avgs):
                if j == 0:
                    for i in range(0, 256, 1):
                        self.adc_set_cmos_vrefs(i, i, i, i)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        print("CMOS", i, vcmi_i, vcmo_i, vrefp_i, vrefn_i)
                        vcmi_cmos.append(vcmi_i)
                        vcmo_cmos.append(vcmo_i)
                        vrefp_cmos.append(vrefp_i)
                        vrefn_cmos.append(vrefn_i)
                    for k in range(0, 64, 1):
                        self.adc_set_cmos_ibuff(k, k)
                        ibuff_cmos.append(self.ref_imon(imon="IBUFF_CMOS"))
                else:
                    for i in range(0, 256, 1):
                        # for i in range (0,256,1):
                        self.adc_set_cmos_vrefs(i, i, i, i)
                        vcmi_i, vcmo_i, vrefp_i, vrefn_i = self.ref_vmons()
                        vcmi_cmos[i] += vcmi_i
                        vcmo_cmos[i] += vcmo_i
                        vrefp_cmos[i] += vrefp_i
                        vrefn_cmos[i] += vrefn_i
                    for k in range(0, 64, 1):
                        self.adc_set_cmos_ibuff(k, k)
                        ibuff_cmos[k] += self.ref_imon(imon="IBUFF_CMOS")
            vrefp_cmos[:] = [x / avgs for x in vrefp_cmos]
            vrefn_cmos[:] = [x / avgs for x in vrefn_cmos]
            vcmi_cmos[:] = [x / avgs for x in vcmi_cmos]
            vcmo_cmos[:] = [x / avgs for x in vcmo_cmos]
            ibuff_cmos[:] = [x / avgs for x in ibuff_cmos]
            return vrefp_cmos, vrefn_cmos, vcmi_cmos, vcmo_cmos, ibuff_cmos

    def sample_rate_set(self, sr=16):
        # Sampling frequency initialized: 500 kHz
        if (sr == 4):
            print("Sampling frequency set: 500 kHz (ADC sampling at 4 Ms/s)")
            tmp = self.udp.read_reg(0x05)
            tmp = self.udp.read_reg(0x05)
            self.udp.write_reg_checked(0x05, tmp | 0x01)
        else:
            tmp = self.udp.read_reg(0x05)
            tmp = self.udp.read_reg(0x05)
            self.udp.write_reg_checked(0x05, tmp & 0xFFFFFFFE)
            print("Sampling frequency set: 2 MHz (ADC sampling at 16 Ms/s)")

    def fe_cfg(self,sts=16*[0], snc=16*[0], sg=16*[3], st=16*[2], sbf = 16*[0], smn = 16*[0], sdc = 0, sdd = 0,sgp =0, slk=0, slkh=0, sdacsw=0, fpga_dac=0,asic_dac=0, delay=10, period=200, width=0xa00 ):
        self.fe.sts = sts
        self.fe.snc = snc
        self.fe.sg  = sg
        self.fe.st  = st
        self.fe.smn = smn
        self.fe.sbf = sbf #buffer on
        self.fe.sdc = sdc #FE AC
        self.fe.sdd = sdd
        self.fe.sgp = sgp
        self.fe.sdacsw = sdacsw
        self.fe.sdac = asic_dac
        self.fe.slk = slk
        self.fe.slkh = slkh
        self.fe.fe_spi_config()
        if sdacsw == 0:
            mode = "RMS"
        elif sdacsw == 1:
            mode = "External"
        elif sdacsw == 2:
            mode = "Internal"
        self.fe.fe_pulse_config(mode)
        self.fe.fe_fpga_dac(fpga_dac)
        self.fe.fe_pulse_param(delay, period, width)
        print ("LArFE is configurated")

    def __init__(self):
        self.bitop = Bit_Op()
        self.udp = UDP()
        self.adc = ColdadcCfg()
        self.adc.uart_flag = False
        self.adc.chip_id = 4
        self.adc.ref = "CMOS"
        self.adc.sdc = "OFF"
        self.adc.db = "OFF"
        self.adc.sha = "Single-Ended"
        self.vrefp_voft = 0xe4
        self.vrefn_voft = 0x28
        self.vcmi_voft = 0x60
        self.vcmo_voft = 0x80

        self.vp_vcmi = False
        self.vn_vcmi = False
        self.vm_vcmi = False
        self.vp_vcmo = False
        self.vn_vcmo = False
        self.vm_vcmo = False
        self.vp_vrefp = False
        self.vn_vrefp = False
        self.vm_vrefp = False
        self.vp_vrefn = False
        self.vn_vrefn = False
        self.vm_vrefn = False

        self.fe = FECfg()

    def charms_i2c_wr(self, CH=0x00, REG_Addr=0x00, REG_Val=0x00):
        self.udp.write_reg_checked (21, 0 ) 
        DEV = 0x70
        self.udp.write_reg_checked (23, DEV )
        self.udp.write_reg_checked (22, CH )
        self.udp.write_reg_checked (24, 2 ) #two bytes
        REG = REG_Val*256 + REG_Addr
        self.udp.write_reg_checked (25, REG ) 
        #I2C write operation
        self.udp.write_reg_checked (21, 1 ) 
        time.sleep(0.1)
        self.udp.write_reg_checked (21, 0 ) 
        print (f'Write Dev={DEV:#x}, CH={CH:#x}, REG_Addr={REG_Addr:#x}, REG_Val={REG_Val:#x}')

    def charms_i2c_rd(self, CH=0x00, REG_Addr=0x00):
        self.udp.write_reg_checked (21, 0 ) 
        DEV = 0x70
        #CH = int(rstrs[0],16) &0xFF
        #REG_Addr = int(rstrs[1],16) & 0xFF
        self.udp.write_reg_checked (23, DEV )
        self.udp.write_reg_checked (22, CH )
        self.udp.write_reg_checked (24, 1 ) #one byte
        self.udp.write_reg_checked (25, REG_Addr ) #one byte
        #I2C write operation
        self.udp.write_reg_checked (21, 1 ) 
        time.sleep(0.1)
        self.udp.write_reg_checked (21, 0 ) 
        self.udp.write_reg_checked (21, 2 ) 
        time.sleep(0.1)
        self.udp.write_reg_checked (21, 0 ) 
        REG_Val = self.udp.read_reg(28)
        print (f'Read Dev={DEV:#x}, CH={CH:#x}, REG_Addr={REG_Addr:#x}, REG_Val={REG_Val:#x}')
        return REG_Val

    def charms_reset(self):
        self.udp.write_reg_checked (29, 255 ) 
        time.sleep(0.1)
        self.udp.write_reg_checked (29, 0 ) 
#        self.fe.fe_def.ver = "P3"
#        self.fe.fe_def.fe_ver_sel()
