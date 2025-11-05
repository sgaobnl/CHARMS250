# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 14:28:53 2018

@author: JunbinZhang
"""
import binascii
import socket
import struct
import sys
import time
from bit_op import Bit_Op


# from array import array

class UDP_frame:
    def info(self):
        print('udp packet cnt=%d' % self.udp_packet_cnt)

    def __init__(self, udp_frame_ptr, raw_data):
        self.udp_frame_length = (128 * 22) + 8  # in words
        self.udp_frame_data = raw_data[int(udp_frame_ptr):int(udp_frame_ptr + self.udp_frame_length)]
        self.udp_packet_cnt = (self.udp_frame_data[0] << 16) + self.udp_frame_data[1]
        # self.udp_header_user_info = 0
        # self.udp_system_status=0
        self.udp_user_data = self.udp_frame_data[8:]


class UDP_frames(UDP_frame):
    def user_data_collection(self):
        user_data = []
        packet_cnts = []
        for i in range(self.cycle):
            ptr = self.udp_frame_length * i
            udp_frame = UDP_frame(ptr, self.raw_data)
            user_data = user_data + udp_frame.udp_user_data
            packet_cnts.append(udp_frame.udp_packet_cnt)
        return [user_data, packet_cnts]

    def __init__(self, cycle, raw_data):
        self.udp_frame_length = (128 * 22) + 8
        self.cycle = cycle
        self.raw_data = raw_data


def rddata(args):
    pass


class UDP(UDP_frames):
    # judge the reg and data is avalible or not
    def Isavaliable(self, reg, data=None):
        regVal = int(reg)
        dataVal = int(data)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            return None
        elif (dataVal < 0) or (dataVal > self.MAX_REG_VAL):
            return None
        else:
            return [regVal, dataVal]

    def Msg_gen(self, regVal, dataVal):
        # Build a massage for a register with its value
        # crazy packet structure require for UDP interface
        dataValMSB = ((dataVal >> 16) & 0xFFFF)
        dataValLSB = dataVal & 0xFFFF
        MESSAGE = struct.pack('HHHHHHHHH', socket.htons(self.KEY1), socket.htons(self.KEY2), socket.htons(regVal),
                              socket.htons(dataValMSB),
                              socket.htons(dataValLSB), socket.htons(self.FOOTER), 0x0, 0x0,
                              0x0)  # format=unsigned short, convert 16-bit positive integers from host to network byte order
        return MESSAGE

    def socket_gen(self, socket_type):
        # Build a socket for communication
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # creat a new socket, IPv4,UDP
        if socket_type == "Listen":
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            new_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000)  # open a large buffer for that
            new_socket.settimeout(5)  # unit second
        else:
            new_socket.setblocking(0)  # non-blocking socket
        return new_socket

    # Write register from PC to FPGA ,this is an overloading function for wib and FEMB both
    def write_reg(self, reg, data, femb_addr=None):
        Value = self.Isavaliable(reg, data)
        if Value is None:
            return None
        else:
            WRITE_MESSAGE = self.Msg_gen(Value[0], Value[1])  # build a message for register
            sock_write = self.socket_gen("Write")
            if femb_addr is None:  # wib mode
                # send the UDP socket with the IP address and port parameters necessary to create the correct header
                sock_write.sendto(WRITE_MESSAGE, (self.UDP_IP, self.UDP_PORT_WREG))  # WIB   WREG UDP port 32000
            elif femb_addr == 0:
                sock_write.sendto(WRITE_MESSAGE, (self.UDP_IP, self.UDPFEMB0_PORT_WREG))  # FEMB0 WREG UDP port 32016
            elif femb_addr == 1:
                sock_write.sendto(WRITE_MESSAGE, (self.UDP_IP, self.UDPFEMB1_PORT_WREG))  # FEMB1 WREG UDP port 32032
            elif femb_addr == 2:
                sock_write.sendto(WRITE_MESSAGE, (self.UDP_IP, self.UDPFEMB2_PORT_WREG))  # FEMB2 WREG UDP port 32048
            elif femb_addr == 3:
                sock_write.sendto(WRITE_MESSAGE, (self.UDP_IP, self.UDPFEMB3_PORT_WREG))  # FEMB3 WREG UDP port 32064
            sock_write.close()

    # Read register from FPGA to PC, this is an overloading function for wib and FEMB both
    def read_reg(self, reg, femb_addr=None):
        regVal = int(reg)
        if (regVal < 0) or (regVal > self.MAX_REG_NUM):
            return None
        else:
            for j in range(10):
                # set up listening socket, do before sending read request
                sock_readresp = self.socket_gen("Listen")
                READ_MESSAGE = self.Msg_gen(regVal, 0)
                # set up a read request socket
                sock_read = self.socket_gen("Write")
                if femb_addr is None:
                    sock_readresp.bind(('', self.UDP_PORT_RREGRESP))  # WIB Response UDP port 32002
                    sock_read.sendto(READ_MESSAGE, (self.UDP_IP, self.UDP_PORT_RREG))  # Read request UDP port 32001
                elif femb_addr == 0:
                    sock_readresp.bind(('', self.UDPFEMB0_PORT_RREGRESP))  # FEMB0 Response UDP port 32018
                    sock_read.sendto(READ_MESSAGE,
                                     (self.UDP_IP, self.UDPFEMB0_PORT_RREG))  # FEMB0 Read request UDP port 32017
                elif femb_addr == 1:
                    sock_readresp.bind(('', self.UDPFEMB1_PORT_RREGRESP))  # FEMB1 Response UDP port 32034
                    sock_read.sendto(READ_MESSAGE,
                                     (self.UDP_IP, self.UDPFEMB1_PORT_RREG))  # FEMB1 Read request UDP port 32033
                elif femb_addr == 2:
                    sock_readresp.bind(('', self.UDPFEMB2_PORT_RREGRESP))  # FEMB2 Response UDP port 32050
                    sock_read.sendto(READ_MESSAGE,
                                     (self.UDP_IP, self.UDPFEMB2_PORT_RREG))  # FEMB2 Read request UDP port 32049
                elif femb_addr == 3:
                    sock_readresp.bind(('', self.UDPFEMB3_PORT_RREGRESP))  # FEMB3 Response UDP port 32066
                    sock_read.sendto(READ_MESSAGE,
                                     (self.UDP_IP, self.UDPFEMB3_PORT_RREG))  # FEMB3 Read request UDP port 32065

                try:
                    data = sock_readresp.recv(4 * 1024)
                except socket.timeout:
                    if j < 8:
                        sock_read.close()
                        sock_readresp.close()
                        # print("Read reg time out (%d)" % j)
                        time.sleep(0.01)
                        continue
                    else:
                        print("FEMB_UDP--> Error read_reg: No read packet received from board, quitting")
                        sock_read.close()
                        sock_readresp.close()
                        sys.exit()
                dataHex = binascii.hexlify(data)  # change it to fit in python3
                sock_readresp.close()
                if int(dataHex[0:4], 16) != regVal:
                    if j < 8:
                        # print("Read reg time out (wrong package received) (%d)" % j)
                        time.sleep(0.01)
                        continue
                    else:
                        print("FEMB_UDP--> Error read_reg: Invalid response packet")
                        sys.exit()
                else:
                    dataHexVal = int(dataHex[4:12], 16)
                    break
            return dataHexVal

    # Check the register if it has been written correctly, this is an overloading function for wib and FEMB both
    def write_reg_checked(self, reg, data, femb_addr=None):
        for i in range(10):
            self.write_reg(reg, data, femb_addr)
            time.sleep(0.001)
            rdata = self.read_reg(reg, femb_addr)
            rdata = self.read_reg(reg, femb_addr)  # twice
            if data == rdata:
                break
            elif i >= 9:
                print("readback value is different from written data, Reg=%d, WR=%x, RD=%x" % (reg, data, rddata))
                sys.exit()
            else:
                time.sleep(0.1)

    # Write register with bit mask
    def write_mask(self, reg, mask, data, femb_addr=None):
        if mask == 0xFFFFFFFF:
            self.write_reg(reg, data, femb_addr)
        else:
            # read the register and get original value
            temp = self.read_reg(reg, femb_addr)
            # get mask bits
            index, size = self.bitop.mask(mask)
            # generate a new value
            val = self.bitop.set_bits(temp, index, size, data)
            # write
            self.write_reg(reg, val, femb_addr)

    def write_mask_checked(self, reg, mask, data, femb_addr=None):
        if mask == 0xFFFFFFFF:
            self.write_reg(reg, data, femb_addr)
        else:
            # read the register and get original value
            temp = self.read_reg(reg, femb_addr)
            # get mask bits
            index, size = self.bitop.mask(mask)
            # generate a new value
            val = self.bitop.set_bits(temp, index, size, data)
            # write
            for i in range(10):
                self.write_reg(reg, val, femb_addr)
                rddata = self.read_reg(reg, femb_addr)
                if val == rddata:
                    break
                elif i >= 9:
                    print("readback value is different from written data, Reg=%d, WR=%x, RD=%x" % (reg, data, rddata))
                    sys.exit()
                else:
                    time.sleep(0.1)

    # Read register with bit mask
    def read_mask(self, reg, mask, femb_addr=None):
        # read the register and get original value
        temp = self.read_reg(reg, femb_addr)
        if mask == 0xFFFFFFFF:
            return temp
        else:
            # get mask bits
            index, size = self.bitop.mask(mask)
            return self.bitop.get_bits(temp, index, size)

    def data_fifo_en(self, en=1):
        tmp = self.read_reg(1)
        tmp = self.read_reg(1)
        self.write_reg_checked(0x01, tmp | 0x10)
        self.write_reg_checked(0x01, tmp & 0xFFFFFFEF)
        time.sleep(0.001)
        self.write_reg_checked(0x0F, en)
        if en == 1:
            time.sleep(0.01)

    def get_pure_rawdata(self, PktNum, Jumbo=None):
        # set up listening socket
        for j in range(100):
            sock_data = self.socket_gen("Listen")
            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000)  # open a large buffer for that
            sock_data.bind(('', self.UDP_PORT_HSDATA))  # high-speed data UDP port 32003

            self.data_fifo_en(en=1)

            if Jumbo == 'None':
                recvbuf = 8192
            else:
                recvbuf = 9014  # match to 0xefc
            if (PktNum < self.PKT_MAX) or (PktNum == self.PKT_MAX):
                cycle = 1
            else:
                cycle = (PktNum // self.PKT_MAX) + 1

            recv_raw = []
            for i in range(cycle):
                data = None
                try:
                    data = sock_data.recv(recvbuf)
                except socket.timeout:
                    if j < 8:
                        sock_data.close()
                        print("High-speed data time out (%d)" % j)
                        time.sleep(0.05)
                        continue
                    else:
                        print("UDP--> Error get_data: No data packet received from board, quitting")
                        sock_data.close()
                        sys.exit()
                if data is not None:
                    recv_raw.append(data)
                else:
                    sock_data.close()
                    print("No high-speed data received (%d)" % j)
                    time.sleep(0.05)
                    continue
            sock_data.close()

            pkg_len = (0x1610 // 2)
            bad_pkg_flg = False
            for upkg in recv_raw:
                dataNtuple = struct.unpack_from(">%dH" % pkg_len, upkg)
                i = 8
                if dataNtuple[i] == 0xbc3c:
                    pass
                else:
                    print(hex(dataNtuple[i]))
                    print("Error: incomplete user package is found, please retake data %d" % j)
                    bad_pkg_flg = True
                    break
            if bad_pkg_flg:
                self.data_fifo_en(en=0)
                time.sleep(0.05)
                continue
            else:
                self.data_fifo_en(en=0)
                break
        return recv_raw

    def clr_server_buf(self, en=False):
        if en:
            # set up listening socket
            sock_data = self.socket_gen("Listen")
            sock_data.settimeout(1)
            sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000)  # open a large buffer for that
            sock_data.bind(('', self.UDP_PORT_HSDATA))  # high-speed data UDP port 32003
            recvbuf = 9014  # match to 0xefc
            buflen = 0
            while 1:
                try:
                    buflen = buflen + len(sock_data.recv(recvbuf))
                except socket.timeout:
                    print("Server Buffer (%d bytes) is cleared" % buflen)
                    sock_data.close()
                    break
        else:
            pass

    # __INIT__#
    def __init__(self):
        self.bitop = Bit_Op()
        self.UDP_IP = "192.168.121.1"
        self.PKT_MAX = 128

        self.udp_timeout_cnt = 0
        self.KEY1 = 0xDEAD
        self.KEY2 = 0xBEEF
        self.FOOTER = 0xFFFF
        self.UDP_PORT_WREG = 32000
        self.UDP_PORT_RREG = 32001
        self.UDP_PORT_RREGRESP = 32002
        self.UDP_PORT_HSDATA = 32003

        self.MAX_REG_NUM = 0x666
        self.MAX_REG_VAL = 0xFFFFFFFF
        self.MAX_NUM_PACKETS = 1000000
        # ---------------------------------#
        self.PKT_LEN = 44  # 44 bytes per pkt
        self.PKT_HEADER = 0xBC3C
        self.PKT_HEADER1 = 0x3CBC
        # ---------------------------------#
        self.UDPFEMB0_PORT_WREG = 32016
        self.UDPFEMB0_PORT_RREG = 32017
        self.UDPFEMB0_PORT_RREGRESP = 32018

        self.UDPFEMB1_PORT_WREG = 32032
        self.UDPFEMB1_PORT_RREG = 32033
        self.UDPFEMB1_PORT_RREGRESP = 32034

        self.UDPFEMB2_PORT_WREG = 32048
        self.UDPFEMB2_PORT_RREG = 32049
        self.UDPFEMB2_PORT_RREGRESP = 32050

        self.UDPFEMB3_PORT_WREG = 32064
        self.UDPFEMB3_PORT_RREG = 32065
        self.UDPFEMB3_PORT_RREGRESP = 32066


#        self.sock_data = self.socket_gen("Listen")
#        self.sock_data.bind(('', self.UDP_PORT_HSDATA)) #high-speed data UDP port 32003
if __name__ == '__main__':
    udp = UDP()
#    udp.udp_port_update()
    while True:
        addr = int(input ("addr: "))
#        value = int(input ("value: "))
#
#        udp.write_reg(addr, value )
        time.sleep(0.1)
        rd = udp.read_reg(addr )
        print (hex(rd))
#    # Get high-speed data
#    def get_rawdata(self, PktNum, checkflg, Jumbo=None):
#        # set up listening socket
#        sock_data = self.socket_gen("Listen")
#        sock_data.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920000)  # open a large buffer for that
#        sock_data.bind(('', self.UDP_PORT_HSDATA))  # high-speed data UDP port 32003
#
#        if Jumbo == 'None':
#            recvbuf = 8192
#        else:
#            recvbuf = 9014  # match to 0xefc
#
#        if (PktNum < self.PKT_MAX) or (PktNum == self.PKT_MAX):
#            cycle = 1
#        else:
#            cycle = (PktNum // self.PKT_MAX) + 1
#        # print('cycle=%d'%cycle)
#        recv_raw = []
#        for i in range(cycle):
#            data = None
#            try:
#                data = sock_data.recv(recvbuf)
#            except socket.timeout:
#                print("UDP--> Error get_data: No data packet received from board, quitting")
#                sock_data.close()
#                return None
#            if data != None:
#                recv_raw.append(data)
#        sock_data.close()
#        rawdata = array('H', b''.join(recv_raw))  # array.array
#        rawdata.byteswap()  # byte swapping
#        rawdata = rawdata.tolist()  # change it to list
#        udp_frames_inst = UDP_frames(cycle, rawdata)
#        user_data, packet_cnts = udp_frames_inst.user_data_collection()
#        if checkflg == True:
#            self.check_packets(packet_cnts)
#        return user_data
#    def check_packets(self, data):
#        num = len(data)
#        if (num == 2 or num > 2):
#            for i in range(num - 1):
#                if (data[i + 1] - data[i] == 1):
#                    continue
#                else:
#                    print("noncontinuous udp packet found!!! %d" % (i + 1))
