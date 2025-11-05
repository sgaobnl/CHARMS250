# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 16:47:52 2019

@author: JunbinZhang
"""
from udp import UDP
from bit_op import Bit_Op
import time
import sys


# import os
# import sys

class ColdadcCfg:
    def i2c_uart_sel(self):
        if self.uart_flag:
            print("ADC UART is chosen")
            self.udp.write_mask_checked(reg=1, mask=0x02, data=1)
        else:
            print("ADC I2C is chosen")
            self.udp.write_mask_checked(reg=1, mask=0x02, data=0)
        time.sleep(0.1)

    def hard_reset(self):
        self.udp.write_mask_checked(reg=1, mask=0x01, data=0)
        time.sleep(0.3)
        self.udp.write_mask_checked(reg=1, mask=0x01, data=1)
        time.sleep(0.5)
        print("ADC hard reset is performed")

    def adc_read(self, page, addr):
        chip_id = self.chip_id
        if self.uart_flag:
            if page == 2:
                if addr == 1:
                    ladr = ((0x80 + 49) & 0xff) << 20
                elif addr == 2:
                    ladr = ((0x80 + 48) & 0xff) << 20
                elif addr == 3:
                    ladr = ((0x80 + 50) & 0xff) << 20
                else:
                    print("Invalid address")
                    ladr = ((0x80 + 0x7f) & 0xff) << 20
            else:
                ladr = (addr & 0xff) << 20
            ldata = (0x00 & 0xff) << 12  # useless
            lwen = (0x00 & 0x01) << 7  # read
            lchip_id = (chip_id & 0x07) << 8
            data = (ladr & 0x0ff00000) + (ldata & 0x000ff000) + (lchip_id & 0x700) + (lwen & 0x80)
            par_cnt = 0
            for i in range(32):
                if (data >> i) & 0x01 == 0x01:
                    par_cnt = par_cnt + 1
            if par_cnt % 2 == 1:
                par_chk = 0
            else:
                par_chk = 1
            data = ((par_chk << 28) & 0x10000000) + data
            self.udp.write_reg(2, data + 0x01)
            vreg = self.udp.read_reg(3)
            rdadr = (vreg >> 16) & 0xff
            rddata = (vreg >> 8) & 0xff
            time.sleep(0.001)
            self.udp.write_reg(2, data + 0x00)
            # print(
            #    "UART read: chip_id = 0x{:X}, page = 0x{:X}, addr = 0x{:X}, data = 0x{:X}".format(chip_id, page, addr, rddata))
        else:
            # load address
            self.udp.write_mask_checked(reg=4, mask=0x100, data=1)
            # load data
            self.udp.write_mask_checked(reg=4, mask=0xf000, data=chip_id)
            # load byte count
            self.udp.write_mask_checked(reg=4, mask=0xe00, data=page)
            self.udp.write_mask_checked(reg=4, mask=0xff000000, data=addr)
            # run strobe
            self.udp.write_mask_checked(reg=4, mask=0x01, data=1)
            time.sleep(0.001)
            check_done = 1
            while check_done:
                check_done = self.udp.read_mask(reg=9, mask=0x01)
                time.sleep(0.001)
            rddata = self.udp.read_mask(reg=6, mask=0xff)
            self.udp.write_mask_checked(reg=4, mask=0x01, data=0)
            #print("I2C read: chip_id = 0x{:X}, page = 0x{:X}, addr = 0x{:X}, data = 0x{:X}".format(chip_id, page, addr, rddata))
        return rddata

    def adc_write(self, page, addr, data):
        chip_id = self.chip_id
        if self.uart_flag:
            if page == 2:
                if addr == 1:
                    ladr = ((0x80 + 49) & 0xff) << 20
                elif addr == 2:
                    ladr = ((0x80 + 48) & 0xff) << 20
                elif addr == 3:
                    ladr = ((0x80 + 50) & 0xff) << 20
                else:
                    print("invalid address")
                    ladr = ((0x80 + 0x7f) & 0xff) << 20
            else:
                ladr = (addr & 0xff) << 20
            ldata = (data & 0xff) << 12
            lwen = (0x01 & 0x01) << 7  # read
            lchip_id = (chip_id & 0x07) << 8
            data_w = (ladr & 0x0ff00000) + (ldata & 0x000ff000) + (lchip_id & 0x700) + (lwen & 0x80)
            par_cnt = 0
            for i in range(32):
                if (data >> i) & 0x01 == 0x01:
                    par_cnt = par_cnt + 1
            if par_cnt % 2 == 1:
                par_chk = 0
            else:
                par_chk = 1
            data_w = ((par_chk << 28) & 0x10000000) + data_w
            self.udp.write_reg(2, data_w + 0x01)
#            print("UART WRITE: chip_id = 0x{:X}, page = 0x{:X}, addr = 0x{:X}, data = 0x{:X}".format(chip_id, page, addr, data))
            time.sleep(0.001)
            self.udp.write_reg(2, data_w + 0x00)
        else:
            # load address
            self.udp.write_mask_checked(reg=4, mask=0x100, data=0)
            # load data
            self.udp.write_mask_checked(reg=4, mask=0xf000, data=chip_id)
            # load byte count
            self.udp.write_mask_checked(reg=4, mask=0xe00, data=page)
            self.udp.write_mask_checked(reg=4, mask=0xff000000, data=addr)
            self.udp.write_mask_checked(reg=4, mask=0xff0000, data=data)
            # run strobe
            self.udp.write_mask_checked(reg=4, mask=0x01, data=1)
            time.sleep(0.001)
            check_done = 1
            while check_done:
                check_done = self.udp.read_mask(reg=9, mask=0x01)
                time.sleep(0.001)
            self.udp.write_mask_checked(reg=4, mask=0x01, data=0)
            self.udp.write_mask_checked(reg=4, mask=0x01, data=0)
#            print("I2C WRITE: chip_id = 0x{:X}, page = 0x{:X}, addr = 0x{:X}, data = 0x{:X}".format(chip_id, page, addr, data))

    def adc_write_mask(self, page, addr, mask, data):  # reg, mask, data):
        if mask == 0xFFFFFFFF:
            self.adc_write(page, addr, data)
        else:
            temp = self.adc_read(page, addr)
            # get mask bits
            index, size = self.bitop.mask(mask)
            # generate a new value
            val = self.bitop.set_bits(temp, index, size, data)
            # write
            self.adc_write(page, addr, val)

    def soft_reset(self):  # soft reset can only reset I2C page2 registers
        chip_id = self.chip_id
        self.chip_id = 0
        self.adc_write(page=0, addr=6, data=0x0)
        self.adc_write(page=0, addr=0, data=0x0)
        self.chip_id = chip_id

    def adc_set_ref_values(self):
        if "CMOS" in self.ref:
            self.adc_write(page=1, addr=0x80 + 24, data=self.cmos_vrefp)
            self.adc_write(page=1, addr=0x80 + 25, data=self.cmos_vrefn)
            self.adc_write(page=1, addr=0x80 + 26, data=self.cmos_vcmo)
            self.adc_write(page=1, addr=0x80 + 27, data=self.cmos_vcmi)
        else:
            self.adc_write(page=1, addr=0x80 + 10, data=self.bjt_vrefp)
            self.adc_write(page=1, addr=0x80 + 11, data=self.bjt_vrefn)
            self.adc_write(page=1, addr=0x80 + 12, data=self.bjt_vcmo)
            self.adc_write(page=1, addr=0x80 + 13, data=self.bjt_vcmi)

    def __adc_rst_ref_buf_cs(self):
        ref = self.ref
        sdc = self.sdc
        db = self.db
        print("Reset ColdADC before changing reference, SDC, or DB ")
        self.hard_reset()
        self.soft_reset()
        time.sleep(0.5)
        if ref == "CMOS":
            self.adc_write_mask(page=1, addr=0x80+22, mask=0xFFFFFFFF, data=0xFF)
            self.adc_write_mask(page=1, addr=0x80+23, mask=0xFFFFFFFF, data=0x2F)
            self.adc_write_mask(page=1, addr=0x80+0, mask=0x30, data=2)
            self.adc_write_mask(page=1, addr=0x80+19, mask=0x4, data=1)
            self.adc_write_mask(page=1, addr=0x80+28, mask=0x3, data=1)
            self.adc_set_ref_values()
            if (sdc == "ON") or (db == "ON"):
                self.adc_write(page=1, addr=0x80 + 29, data=0x27)
                self.adc_write(page=1, addr=0x80 + 30, data=0x27)
        else:
            self.adc_write_mask(page=1, addr=0x80 + 22, mask=0xFFFFFFFF, data=0x00)
            self.adc_write_mask(page=1, addr=0x80 + 23, mask=0xFFFFFFFF, data=0x20)
            time.sleep(0.01)
            self.adc_write(page=1, addr=0x80 + 14, data=0x55)
            self.adc_write(page=1, addr=0x80 + 24, data=0x0)
            self.adc_write(page=1, addr=0x80 + 25, data=0x0)
            self.adc_write(page=1, addr=0x80 + 26, data=0x0)
            self.adc_write(page=1, addr=0x80 + 27, data=0x0)
            self.adc_set_ref_values()
            self.adc_write_mask(page=1, addr=0x80+0, mask=0x30, data=1)
            self.adc_write_mask(page=1, addr=0x80+19, mask=0x4, data=0)
            self.adc_write_mask(page=1, addr=0x80+28, mask=0x3, data=0)
            if (sdc == "ON") or (db == "ON"):
                self.adc_write(page=1, addr=0x80 + 15, data=0x99)
                self.adc_write(page=1, addr=0x80 + 16, data=0x99)
                self.adc_write(page=1, addr=0x80 + 17, data=0x99)
                self.adc_write(page=1, addr=0x80 + 18, data=0x99)
        if (sdc == "ON") and (db == "ON"):
            print("Error: SDC and DB can't power up at the same time!")
            sys.exit()
        if sdc == "OFF":
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x1, data=1)
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x40, data=0)
        else:
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x1, data=0)
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x40, data=1)
        if db == "OFF":
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x2, data=1)
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x80, data=0)
        else:
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x2, data=0)
            self.adc_write_mask(page=1, addr=0x80 + 0, mask=0x80, data=1)

    def __adc_sha_mode(self):
        chip_id = self.chip_id
        sha = self.sha
        if ("Single" in sha) and ("OFF" in self.sdc):
            self.adc_write_mask(page=1, addr=0x80 + 4, mask=0x8, data=1)
        else:
            self.adc_write_mask(page=1, addr=0x80 + 4, mask=0x8, data=0)

    def adc_cfg_all(self):
        print("Ref={}, SDC={}, DB={}, SHA={}".format(self.ref, self.sdc, self.db, self.sha))
        self.__adc_rst_ref_buf_cs()
        self.__adc_sha_mode()
        print ("Page 2")
        self.adc_write(page=2, addr=1, data=0x0C)
        print("ADC auto calibration")
        self.adc_write_mask(page=1, addr=0x80 + 31, mask=0x03, data=0x03)
        time.sleep(1)
        self.adc_write_mask(page=1, addr=0x80 + 31, mask=0x03, data=0x00)
        time.sleep(0.1)
        print("ADC data with offset binary code")
        self.adc_write_mask(page=1, addr=0x80 + 9, mask=0x8, data=0x1)
        #self.adc_write_mask(page=1, addr=0xB2, mask=0xFFFFFFFF, data=0x20)
        #self.adc_write_mask(page=1, addr=0xB3, mask=0xFFFFFFFF, data=0xCD)
        #self.adc_write_mask(page=1, addr=0xB4, mask=0xFFFFFFFF, data=0xAB)
        #self.adc_write_mask(page=1, addr=0xB5, mask=0xFFFFFFFF, data=0x34)
        #self.adc_write_mask(page=1, addr=0xB6, mask=0xFFFFFFFF, data=0x12)

    def adc_read_weights(self):
        reg = []
        val = []
        # read weights from ADC0
        for addrs in [range(0, 0xe, 1), range(0x20, 0x2e, 1), range(0x40, 0x4e, 1), range(0x60, 0x6e, 1)]:
            for addr in addrs:
                value = self.adc_read(page=1, addr=addr)
                value = self.adc_read(page=1, addr=addr)
                reg.append(addr)
                val.append(value)
        return reg, val

    def i2c_uart_chk(self):
        # Read and Write register with I2C
        for chk_str in ("I2C", "UART"):
            if "I2C" in chk_str:
                self.uart_flag = False
            else:
                self.uart_flag = True
            self.i2c_uart_sel()
            time.sleep(0.1)
            self.adc_write_mask(page=1, addr=0x80 + 2, mask=0x2, data=0)
            self.adc_write_mask(page=1, addr=0x80 + 2, mask=0x2, data=1)
            rd = self.adc_read(page=1, addr=0x80 + 2)
            self.adc_write_mask(page=1, addr=0x80 + 2, mask=0x2, data=0)
            if (rd & 0x02) != 0x02:
                status = "FAIL"
                err_log = "{} check failed. Read/Write not working correctly. \n".format(chk_str)
                print(status, err_log)
                sys.exit()
            else:
                print("{} Connection works".format(chk_str))
        self.uart_flag = False
        self.i2c_uart_sel()

    def default_regs_chk(self):
        self.hard_reset()
        self.soft_reset()
        if self.coldadc_ver == "P2":
            page1 = [0xA3, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x33, 0x0B, 0x00,
                       0xf1, 0x29, 0x8d, 0x65, 0x55, 0xff, 0xff, 0xff, 0xff, 0x04,
                       0x00, 0x00, 0xff, 0x2f, 0xdf, 0x33, 0x89, 0x67, 0x15, 0xff,
                       0xff, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                       0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x10,
                       0x00, 0xcd, 0xab, 0x34, 0x12]
            page2 =[0x10,0x04,0x00, 0x00]
        else:
            page1 = [0x52, 0x00, 0x00, 0x00, 0x33, 0x33, 0x33, 0x33, 0x0a, 0x00,
                        0xfa, 0x3a, 0x9a, 0x73, 0xff, 0x99, 0x99, 0x99, 0x99, 0x00,
                        0x00, 0x00, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x0c, 0x27,
                        0x27, 0x00, 0x7f, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                        0x00, 0x00, 0xa5, 0xca, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00,
                        0x00, 0xcd, 0xab, 0x34, 0x12]
            page2 = [0x04, 0xff, 0x00]

        for i in range(len(page1)):
            tmp = self.adc_read(page=1, addr=0x80 + i)
            if tmp != page1[i]:
                status = "FAIL"
                err_log = "Page1 reg addr = 0x{:02X}: default value=0x{:02X}, readback = 0x{:02X}".format(i, page1[i], tmp)
                print(status, err_log)
                sys.exit()
        for i in range(len(page2)):
            tmp = self.adc_read(page=2, addr=i + 1)
            if tmp != page2[i]:
                status = "FAIL"
                err_log = "Page2 reg addr = 0x{:02X}: default value=0x{:02X}, readback = 0x{:02X}".format(i, page2[i], tmp)
                print(status, err_log)
                sys.exit()
        print("Pass Default registers checkout")

            #
    def re_init(self):
        self.__init__()

    def __init__(self):
        self.bitop = Bit_Op()
        self.uart_flag = False
        self.udp = UDP()
        self.coldadc_ver = "P2"
        self.chip_id = 4
        self.ref = "CMOS"
        self.sdc = "OFF"
        self.db = "OFF"
        self.sha = "Single-Ended"
        self.bjt_vrefp = 0xF1
        self.bjt_vrefn = 0x29
        self.bjt_vcmo = 0x8D
        self.bjt_vcmi = 0x65
        self.cmos_vrefp = 0xDF
        self.cmos_vrefn = 0x33
        self.cmos_vcmo = 0x89
        self.cmos_vcmi = 0x67

