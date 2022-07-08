#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 24 Nis 2019

@author: erdidogan
'''
## Initialization
import os, sys
import requests
sys.path.append(r"C:\Program Files\PTI\PSSE35\35.2\PSSPY37")
os.environ['PATH'] = r"C:\Program Files\PTI\PSSE35\35.2\PSSBIN;" + os.environ['PATH']
import psse35
psse35.set_minor(2)
import psspy
import pssarrays
import numpy as np
_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()
psspy.psseinit(150000)
KBA, Trakya, bursa, istanbul, sakarya, kutahya, istanbul_trakya = 2, 1, 702, 704, 705, 706, 701
class ShortCircuit:
    
    def __init__(self, sav_ismi, file_directory, tieLines=None, location = None):
        self.sav_ismi, self.file_directory, self.location = sav_ismi, file_directory, location
        #Subsystems
        psspy.fdns([0,1,0,1,1,4,0,0])                               #flat start fdns power flow solution
        if location == 701:
            psspy.bsys(2,0,[ 0.38, 400.],1,[1],0,[],1,[701],1,[2])    #Bursa region
        if location == 702:
            psspy.bsys(2,0,[ 0.38, 400.],1,[2],0,[],1,[702],1,[2])    #Bursa region
        if location == 704:
            psspy.bsys(4,0,[ 0.38, 400.],1,[2],0,[],1,[704],1,[2])    #Istanbul Anatolia region
            psspy.bsys(7,0,[ 0.38, 400.],0,[],1,[210321],0,[],0,[])
        #psspy.bsys(4,0,[ 0.38, 400.],0,[],60,[210021,210022,210121,210122,210123,210124,210221,210222,210223,210321,210721,210722,210821,210822,210921,210922,211021,211022,211121,211122,211221,211222,211321,211322,211421,211422,211521,211522,211621,211622,211721,211722,211821,211822,211921,211922,212021,212022,212221,212222,214021,214022,214121,214122,214321,214322,214821,214822,214823,216621,216622,216721,216722,217221,217222,217521,217522,217621,217622,219121],0,[],0,[])
        if location == 705:
            psspy.bsys(5,0,[ 0.38, 400.],1,[2],0,[],1,[705],1,[2])    #Sakarya region
        if location == 706:
            psspy.bsys(6,0,[ 0.38, 400.],1,[2],0,[],1,[706],1,[2])    #Kutahya region
        if location == 1:
            psspy.bsys(1,0,[0.0, 230.],3,[2,1,3],0,[],1,[1],2,[1,2])    #RTS96
    def shortcircuit(self):
        #IEC 60909 short-circuit calculation 
        if self.location ==701:
            #self.bak = psspy.iecs_4(2,0,[1,1,0,0,0,0,1,0,0,0,1,1,0,0,0,2,1],[ 0.1, 1.1],self.file_directory+"\\"+self.sav_ismi+".iec","","")
            self.istanbul_trakya = pssarrays.iecs_currents(2,0,1,1,0,0,0,0,0,0,1,1,0,0, 2,2,1,0.1,1.1,self.file_directory+"\\"+self.sav_ismi+".iec","","")      
            self.region = self.istanbul_trakya
        if self.location ==702:
            self.bursa = pssarrays.iecs_currents(2,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1)      #Bursa region
            self.region = self.bursa
        elif self.location ==704:
            #self.bak = psspy.iecs_4(4,0,[1,1,0,0,0,0,1,0,0,0,1,1,0,0,0,2,1],[ 0.1, 1.1],self.file_directory+"\\"+self.sav_ismi+".iec","","")
            #self.bak = psspy.iecs_4(4,0,[1,1,0,0,0,0,0,0,0,0,1,1,0,0,2,2,1],[ 0.1, 1.1],self.file_directory+"\\"+self.sav_ismi+".iec","","")
            self.istanbul = pssarrays.iecs_currents(4,0,1,1,0,0,0,0,0,0,1,1,0,0, 2,2,1,0.1,1.1,self.file_directory+"\\"+self.sav_ismi+".iec","","")  #Istanbul Anatolia region
            self.ada = pssarrays.iecs_currents(7,0,1,1,0,0,0,0,0,0,1,1,0,0, 2,2,1,0.1,1.1,self.file_directory+"\\"+self.sav_ismi+".iec","","")
            self.region = self.istanbul
            self.region2 = self.ada
        elif self.location == 705:
            self.sakarya = pssarrays.iecs_currents(5,0,1,1,0,0,0,0,0,0,1,1,0,0,0,0,1)    #Sakarya region
            self.region = self.sakarya
        elif self.location == 706:
            self.kutahya = pssarrays.iecs_currents(6,0,1,1,0,0,0,0,0,0,1,1,0,0, 0,0,1)   #Kutahya region
            self.region = self.kutahya
        elif self.location == 1:
            self.region = pssarrays.iecs_currents(1,0,1,1,0,0,0,0,0,0,1,1,0,0, 0,0,1)   #Kutahya region
        self.ShortCircuit3Ph_1PhList = []
        [[self.ShortCircuit3Ph_1PhList.append(self.region.flt3ph[i].ia.real),self.ShortCircuit3Ph_1PhList.append(self.region.fltlg[i].ia.real)] for i in range(len(self.region.fltbus))]
        if self.location == 704: 
            [[self.ShortCircuit3Ph_1PhList.append(self.region2.flt3ph[i].ia.real), self.ShortCircuit3Ph_1PhList.append(self.region2.fltlg[i].ia.real)] for i in range(len(self.region2.fltbus))]
        self.sc_3_1 = np.array(self.ShortCircuit3Ph_1PhList)
        #print (self.sc_3_1)
        sc_bounds = [20000,30800,31000,31200,31300,31500,32000,32500,32500,33000,33500,34000,35000,36000,37000,38000]
        #sc_bounds = [17000,18000,18500,18700,18900,19000,19100,19200,19300,19400,19500,19600,20000,21000,22000,23000]
        #sc_bounds = [0,13000,14000,15000,16000,17000,18000,19000,20000]

        #self.ShortCircuitPerformanceIndex = np.sum(np.power((np.array(self.sc_3_1)[self.sc_3_1>=30800])/1.0,1))
        self.SCPFIndex0 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[0]) & (self.sc_3_1<sc_bounds[1])]/12000.0
        self.SCPFIndex1 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[1]) & (self.sc_3_1<sc_bounds[2])]/9000.0
        self.SCPFIndex2 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[2]) & (self.sc_3_1<sc_bounds[3])]/6000.0
        self.SCPFIndex3 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[3]) & (self.sc_3_1<sc_bounds[4])]/5000.0
        self.SCPFIndex4 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[4]) & (self.sc_3_1<sc_bounds[5])]/100.0
        self.SCPFIndex5 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[5]) & (self.sc_3_1<sc_bounds[6])]/90.0
        self.SCPFIndex6 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[6]) & (self.sc_3_1<sc_bounds[7])]/80.0
        self.SCPFIndex7 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[7]) & (self.sc_3_1<sc_bounds[8])]/70.0
        self.SCPFIndex8 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[8])]/60.0
        self.SCPFIndex9 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[9]) & (self.sc_3_1<sc_bounds[10])]/50
        self.SCPFIndex10 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[10]) & (self.sc_3_1<sc_bounds[11])]/40
        self.SCPFIndex11 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[11]) & (self.sc_3_1<sc_bounds[12])]/30
        self.SCPFIndex12 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[12]) & (self.sc_3_1<sc_bounds[13])]/20
        self.SCPFIndex13 = np.array(self.sc_3_1)[(self.sc_3_1>=sc_bounds[13]) & (self.sc_3_1<sc_bounds[14])]/10
        self.SCPFIndex14 = np.array(self.sc_3_1)[self.sc_3_1>=sc_bounds[14]]
        #print self.SCPFIndex1, self.SCPFIndex2,self.SCPFIndex3,self.SCPFIndex4,self.SCPFIndex5,self.SCPFIndex6,self.SCPFIndex7,self.SCPFIndex8,self.SCPFIndex9,self.SCPFIndex10,self.SCPFIndex11,self.SCPFIndex12,self.SCPFIndex13,self.SCPFIndex14
        self.total_sc = np.sum(self.SCPFIndex0) + np.sum(self.SCPFIndex1) + np.sum(self.SCPFIndex2) + np.sum(self.SCPFIndex3) + np.sum(self.SCPFIndex4) + np.sum(self.SCPFIndex5) + np.sum(self.SCPFIndex6) + np.sum(self.SCPFIndex7) + np.sum(self.SCPFIndex8) + np.sum(self.SCPFIndex9) + np.sum(self.SCPFIndex10) + np.sum(self.SCPFIndex11) + np.sum(self.SCPFIndex12) + np.sum(self.SCPFIndex13) + np.sum(self.SCPFIndex14)
        #self.total_sc = np.sum(self.SCPFIndex0)
        return self.total_sc

#sc = ShortCircuit('20210805_1400_SN4_TR0 (1)',r"C:\Users\erdidogan\Downloads", location = 704)
#print (sc.shortcircuit())

