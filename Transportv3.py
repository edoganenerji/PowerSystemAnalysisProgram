#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 11 Nis 2021

@author: erdidogan
'''
## Initialization
import os, sys
import requests
import ConAn
sys.path.append(r"C:\Program Files\PTI\PSSE35\35.2\PSSPY37")
os.environ['PATH'] = r"C:\Program Files\PTI\PSSE35\35.2\PSSBIN;" + os.environ['PATH']
import psse35
psse35.set_minor(2)
import psspy
import time
from search import *
import string
from random import randint
import numpy as np
import pandas as pd
import copy
_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()
psspy.psseinit(150000)
KBA, istanbul, bursa, sakarya, kutahya = 2, 704, 702, 705, 706

class networkReduction():
    r'''
    This class is used to create a reduced network.
    r'''
    def __init__(self, ytim, regions, file_directory, sav_ismi):
        r'''
        :param int ytim:
            ytim is represents the number of area of the related yuk tevzi isletme mudurlugu
        :param list regions:
            regions of network chosen by user in order to optimize
        :param str file_directory:
            file_directory is the sav file path added by user
        :param str sav_ismi:
            sav_ismi is the name of the sav file
        r'''
        self.regions = regions
        self.ytim = ytim
        self.file_directory = file_directory
        self.sav_ismi = sav_ismi
        #all regions area list
        self.area_list = [1 + i for i in range(10)]
    def TieLine(self):  
        r'''
        :return object self.dftieBus:
            tie buses are retrieved at the related subsystem
        r'''
        #subsystem id no (2) is created by the outofRegion function
        self.TieFlow = psspy.aflowcount(2,1,2,1)[1]                          # Number of Power Flow
        self.TieFrName = psspy.aflowchar(2,1,2,1,'FROMEXNAME')[1]            #From Bus Name
        self.TieToName = psspy.aflowchar(2,1,2,1,'TOEXNAME')[1]              #To Bus Name
        self.TieLineID = psspy.aflowchar(2,1,2,1,'ID')[1]                    #Line ID
        self.TieFrNumber = psspy.aflowint(2, 1, 2, 1, 'FROMNUMBER')[1]       #From Number
        self.TieToNumber = psspy.aflowint(2, 1, 2, 1, 'TONUMBER')[1]         #To Number
        self.LineList, self.TieFrNumberlst, self.TieToNumberlst, self.TieFrNamelst, self.TieToNamelst, self.TieLineIDlst = [], [], [], [], [], []
        for i in range(self.TieFlow):
            if int(str(self.TieToNumber[0][i])[4]) <= 2:                     
                if int(str(self.TieFrNumber[0][i])[4]) <= 2:
                    if int(str(self.TieFrNumber[0][i])[0:4]) != int(str(self.TieToNumber[0][i])[0:4]):
                        if int(str(self.TieToNumber[0][i])[1]) != 9:
                            self.LineList.append([self.TieFrNumber[0][i],self.TieToNumber[0][i],self.TieFrName[0][i],self.TieToName[0][i],self.TieLineID[0][i]])
                            self.TieFrNumberlst.append(self.TieFrNumber[0][i]) 
                            self.TieToNumberlst.append(self.TieToNumber[0][i])
                            self.TieFrNamelst.append(self.TieFrName[0][i])
                            self.TieToNamelst.append(self.TieToName[0][i])
                            self.TieLineIDlst.append(self.TieLineID[0][i])
        self.dfLineList = pd.DataFrame(np.array(self.LineList), columns = ["From Number","To Number","From Name","To Name","Line ID"])
        self.tieBus = []
        for i in range(len(self.TieToNumberlst)):
            if self.TieToNumberlst[i] not in self.tieBus:
                self.tieBus.append([self.TieToNumberlst[i],int(str(self.TieFrNumberlst[i])+str(self.TieToNumberlst[i]))])
        self.dftieBus = pd.DataFrame(np.array(self.tieBus), columns = ["Bus Number","From-To Branch"])
        return self.dftieBus
    def outofRegion(self):
        r'''
        :return list self.OutBusforRemove:
            which buses will be removed is determined.
        r'''
        #Determine which area won't be removed from the network
        self.area_list.remove(self.ytim)
        psspy.bsys(0,0,[ 0.38, 400.],len(self.area_list),self.area_list,0,[],0,[],0,[])
        psspy.bsys(2,0,[ 0.38, 400.],1,[self.ytim],0,[],0,[],0,[])
        self.OutBusforRemove = []
        #Retrieve bus numbers to be removed
        self.OutBus  = psspy.abusint(0, 2, 'NUMBER')[1]
        #Determine tie line
        self.tieRetrieve = self.TieLine()
        #Determine buses to be removed while considering tie buses with related area
        for i in range(len(self.OutBus[0])):
            if int(str(self.OutBus[0][i])[0]) != self.ytim:
                if self.OutBus[0][i] not in self.tieRetrieve["Bus Number"].to_numpy():
                    self.OutBusforRemove.append(self.OutBus[0][i])
        return self.OutBusforRemove
    def tieBusData(self):
        r'''
        :return list [self.dfTieLoadAdd,self.dfTieGeneratorAdd]:
            Before reducing network, the active and reactive power flow through tie lines are recorded 
            to simulate same situation with original network by adding those flows as generation or load.
        r'''
        psspy.fdns([0,1,0,1,1,1,0,0])
        self.tieForSub = self.tieRetrieve["Bus Number"].to_numpy()
        self.TieFlowlst, self.TieLoadAdd, self.TieGeneratorAdd = [], [], []
        psspy.bsys(0,0,[ 0.38, 400.],0,[],self.tieForSub.shape[0],self.tieForSub.tolist(),0,[],0,[])
        self.ierr, self.TieFrBusNumber = psspy.aflowint(0, 1, 2, 1, "FROMNUMBER")
        self.ierr, self.TieToBusNumber = psspy.aflowint(0, 1, 2, 1, "TONUMBER")
        self.ierr, self.TieFrBusName = psspy.aflowchar(0, 1, 2, 1, "FROMNAME")
        self.ierr, self.TieToBusName = psspy.aflowchar(0, 1, 2, 1, "TONAME")
        self.ierr, self.ActivePower = psspy.aflowreal(0, 1, 2, 1, 'P')
        self.ierr, self.ReactivePower = psspy.aflowreal(0, 1, 2, 1, 'Q')
        for i in range(len(self.TieFrBusNumber[0])):
            if int(str(self.TieToBusNumber[0][i])[0]) == self.ytim:
                if str(self.ActivePower[0][i])[0] == "-":
                    self.TieFlowlst.append([self.TieFrBusNumber[0][i],self.TieToBusNumber[0][i],self.TieFrBusName[0][i],self.TieToBusName[0][i],int(round(float(str(self.ActivePower[0][i])[1:]))),self.ReactivePower[0][i]])
                    self.TieLoadAdd.append([self.TieFrBusNumber[0][i],self.TieToBusNumber[0][i],self.TieFrBusName[0][i],self.TieToBusName[0][i],int(round(self.ActivePower[0][i])),self.ReactivePower[0][i]])
                else:
                    self.TieFlowlst.append([self.TieFrBusNumber[0][i],self.TieToBusNumber[0][i],self.TieFrBusName[0][i],self.TieToBusName[0][i],int(round(self.ActivePower[0][i])),self.ReactivePower[0][i]])
                    self.TieGeneratorAdd.append([self.TieFrBusNumber[0][i],self.TieToBusNumber[0][i],self.TieFrBusName[0][i],self.TieToBusName[0][i],int(round(self.ActivePower[0][i])),self.ReactivePower[0][i]])
        self.dfSwingBusFlow = pd.DataFrame(np.array(self.TieFlowlst), columns = ["From Number", "To Number", "From Name", "To Name", "ActivePower", "Reactive Power"])
        self.dfSwingBusFlow.ActivePower = pd.to_numeric(self.dfSwingBusFlow.ActivePower, errors='coerce')
        self.dfTieLoadAdd = pd.DataFrame(np.array(self.TieLoadAdd), columns = ["From Number", "To Number", "From Name", "To Name", "Active Power", "Reactive Power"])
        self.dfTieGeneratorAdd = pd.DataFrame(np.array(self.TieGeneratorAdd), columns = ["From Number", "To Number", "From Name", "To Name", "Active Power", "Reactive Power"])
        self.dfSwingBusFlow.describe()
        self.dfTieLoadAdd.describe()
        self.dfTieGeneratorAdd.describe()
        return [self.dfTieLoadAdd,self.dfTieGeneratorAdd]
    def importFlowsintoTies(self):
        r'''
        the active and reactive power flow through tie lines are recorded 
        to simulate same situation with original network by adding those flows as generation or load.
        r'''
        self.importLoadActivePowerList, self.importLoadReactivePowerList, self.importGenActivePowerList, self.importGenReactivePowerList, self.importTieLoadFromNumberList, self.importTieGenFromNumberList = [], [], [], [], [], []
        self.importTieLoadFromNumber = self.dfTieLoadAdd["From Number"].to_numpy()
        self.importLoadActivePower = self.dfTieLoadAdd["Active Power"].to_numpy()
        self.importLoadReactivePower = self.dfTieLoadAdd["Reactive Power"].to_numpy()
        self.importTieGenFromNumber = self.dfTieGeneratorAdd["From Number"].to_numpy()
        self.importGenActivePower = self.dfTieGeneratorAdd["Active Power"].to_numpy()
        self.importGenReactivePower = self.dfTieGeneratorAdd["Reactive Power"].to_numpy()
        for i in range(len(self.importTieLoadFromNumber)):
            self.importTieLoadFromNumberList.append(int(self.importTieLoadFromNumber[i]))
            self.importLoadActivePowerList.append(float(self.importLoadActivePower[i]))
            self.importLoadReactivePowerList.append(float(self.importLoadReactivePower[i]))
        for i in range(len(self.importTieGenFromNumber)):
            self.importTieGenFromNumberList.append(int(self.importTieGenFromNumber[i]))
            self.importGenActivePowerList.append(float(self.importGenActivePower[i]))
            self.importGenReactivePowerList.append(float(self.importGenReactivePower[i]))
        for i in range(len(self.importTieLoadFromNumberList)):
            psspy.load_data_5(self.importTieLoadFromNumberList[i],r"""1""",[1,2,int(str(self.importTieLoadFromNumberList[i])[4]),701,1,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
            psspy.load_chng_5(self.importTieLoadFromNumberList[i],r"""1""",[_i,_i,_i,_i,_i,_i,_i],[(self.importLoadActivePowerList[i]*(-1)),(self.importLoadReactivePowerList[i]*(-1)),_f,_f,_f,_f,_f,_f])
        for i in range(len(self.importTieGenFromNumberList)):
            psspy.load_data_5(self.importTieGenFromNumberList[i],r"""1""",[1,2,int(str(self.importTieGenFromNumberList[i])[4]),701,1,0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0])
            psspy.load_chng_5(self.importTieGenFromNumberList[i],r"""1""",[_i,_i,_i,_i,_i,_i,_i],[(self.importGenActivePowerList[i]*(-1)),(self.importGenReactivePowerList[i]*(-1)),_f,_f,_f,_f,_f,_f])
        psspy.save(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
    def removeBus(self):
        r'''
        remove all buses except for the related area (ytim)
        r'''
        psspy.case(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
        psspy.bsysinit(1)
        for i in range(len(self.OutBusforRemove)):
            psspy.bsyso(1,self.OutBusforRemove[i])
            self.ierr = psspy.extr(1,0,[0,0])
        psspy.save(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
    def createSwingBus(self):
        r'''
        create swing bus in the new reduced network. The most loaded bus is determined and chosen as swing bus.
        if the result of the power flow does not met convergence tolerances, the second loaded bus is added
        as swing bus and so on until four swing bus.
        r'''
        self.swingBusRetrieve = self.tieRetrieve
        self.SortwhichBusBecomeSwing = self.dfSwingBusFlow.sort_values(by = "ActivePower", ascending = False)
        psspy.plant_data(int(self.SortwhichBusBecomeSwing.iat[0,0]),_i,[_f,_f])
        psspy.machine_data_2(int(self.SortwhichBusBecomeSwing.iat[0,0]),r"""1""",[_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
        psspy.bus_chng_4(int(self.SortwhichBusBecomeSwing.iat[0,0]),0,[3,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f],_s)
        psspy.fdns([0,1,0,1,1,1,0,0])
        convergence = psspy.solved()
        if convergence == 9:
            self.IslandBuses = psspy.treedat()['island_busnum']
            print(f'{self.IslandBuses} numarali baralar sistemden kopuk! Bu baralar servis harici edildi!')
            psspy.tree(1,0)
            psspy.tree(2,1)
        convergence = ConAn.multiple_load_flow()
        if convergence != 0:
            psspy.bus_chng_4(int(self.SortwhichBusBecomeSwing.iat[1,0]),0,[3,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f],_s)
            convergence = ConAn.multiple_load_flow()
            if convergence != 0:
                psspy.bus_chng_4(int(self.SortwhichBusBecomeSwing.iat[2,0]),0,[3,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f],_s)
                convergence = ConAn.multiple_load_flow()
                if convergence != 0:
                    psspy.bus_chng_4(int(self.SortwhichBusBecomeSwing.iat[3,0]),0,[3,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f],_s)
        psspy.save(self.file_directory+'\\'+self.sav_ismi+"_ReducedVersion_"+str(self.regions)+".sav")
    def runNetReduction(self):
        self.outofRegion()
        self.tieBusData()
        self.importFlowsintoTies()
        self.removeBus()
        self.createSwingBus()
        return self.tieRetrieve
def prepare_busbars(sav_ismi, ytim, regions, file_directory = "C:\\Users\erdidogan\Desktop\BusLayoutDCcon"):
    psspy.case(file_directory+"\\"+sav_ismi+".sav")        # Open Folder 
    psspy.progress_output(6,"",[0,0])
    psspy.bsys(1,1,[154., 400.],1, [ytim],0,[],len(regions),regions,2,[2,1])                 #Create a subsystem
    string = psspy.brnnam(220021, 220022, r"""1""")[1]
    string_list = string.split()
    zil_name = string_list[-1]
    if zil_name != r"""KUPLAJ""":
        psspy.purgbrn(220021,220022,r"""1""")
        psspy.purgbrn(220021,220023,r"""1""")
        psspy.system_swd_data(220021,220022,r"""1""",[0,0,220021,2], 0.0001,[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],r"""C276:154-A K""")
        psspy.system_swd_chng(220021,220022,r"""1""",[_i,_i,220021,_i],_f,[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],r"""C276:154 KUPLAJ""")
        psspy.bsys(0,0,[ 0.38, 400.],0,[],1,[220022],0,[],0,[])
        feeder_connected_fr_bus = psspy.abrnint(0, 1, 3, 4, 1, 'FROMNUMBER')[1][0]
        feeder_connected_to_bus = psspy.abrnint(0, 1, 3, 4, 1, 'TONUMBER')[1][0]
        feeder_connected_id = psspy.abrnchar(0, 1, 3, 4, 1, 'ID')[1][0]
        #This peace of code ensure that all feeders connected to the bus-2 transport to the bus-1
        for i in range(len(feeder_connected_fr_bus)):
            if int(str(feeder_connected_fr_bus[i])[:5]) != int(str(feeder_connected_to_bus[i])[:5]):
                psspy.bsysinit(4)
                psspy.bsyso(4,220021)
                conveyed_bus_fr_nmb = psspy.abrnint(4, 1, 3, 3, 1, 'FROMNUMBER')[1][0]                                   #From number of branch
                conveyed_bus_t_nmb = psspy.abrnint(4, 1, 3, 3, 1, 'TONUMBER')[1][0]                                      #To number of branch
                conveyed_bus_id = psspy.abrnchar(4, 1, 3, 3, 1, 'ID')[1][0]                                              #ID
                conveyed_bus_fr_to_nmb = [int(str(conveyed_bus_fr_nmb[c])+str(conveyed_bus_t_nmb[c])) for c in range(len(conveyed_bus_t_nmb))]
                is_this_line_already_exist_fr = np.where(int(str(220021)+str(feeder_connected_to_bus[i])) == np.array(conveyed_bus_fr_to_nmb))
                is_this_line_already_exist_to = np.where(int(str(feeder_connected_fr_bus[i])+str(220021)) == np.array(conveyed_bus_fr_to_nmb))
                exist_id_fr = [conveyed_bus_id[id].strip() for id in is_this_line_already_exist_fr[0] if is_this_line_already_exist_fr[0].shape[0] > 0]
                exist_id_to = [conveyed_bus_id[id].strip() for id in is_this_line_already_exist_to[0] if is_this_line_already_exist_to[0].shape[0] > 0]
                new_id_lst = ['1', '2', '3', '4', '5']
                new_ckt_fr = [new_id_lst[nw] if len(exist_id_fr) > 0 else '1' for nw in range(len(new_id_lst)) if new_id_lst[nw] not in exist_id_fr] 
                new_ckt_to = [new_id_lst[nw] if len(exist_id_to) > 0 and new_id_lst[nw] not in exist_id_to else '1' for nw in range(len(new_id_lst))] 
                if feeder_connected_fr_bus[i] == 220022:
                    psspy.movebrn(feeder_connected_to_bus[i],feeder_connected_fr_bus[i],_s,220021,new_ckt_fr[0])
                elif feeder_connected_to_bus[i] == 220022:
                    psspy.movebrn(feeder_connected_fr_bus[i],feeder_connected_to_bus[i],_s,220021,new_ckt_to[0])
        psspy.bsys(0,0,[ 0.38, 400.],0,[],2,[220023,220024],0,[],0,[])
        feeder_connected_fr_bus = psspy.abrnint(0, 1, 3, 4, 1, 'FROMNUMBER')[1][0]
        feeder_connected_to_bus = psspy.abrnint(0, 1, 3, 4, 1, 'TONUMBER')[1][0]
        feeder_connected_id = psspy.abrnchar(0, 1, 3, 4, 1, 'ID')[1][0]
        #This peace of code ensure that all feeders connected to the bus-3 and bus-4 transport to the bus-2
        for i in range(len(feeder_connected_fr_bus)):
            psspy.bsysinit(4)
            psspy.bsyso(4,220022)
            conveyed_bus_fr_nmb = psspy.abrnint(4, 1, 3, 3, 1, 'FROMNUMBER')[1][0]                                   #From number of branch
            conveyed_bus_t_nmb = psspy.abrnint(4, 1, 3, 3, 1, 'TONUMBER')[1][0]                                      #To number of branch
            conveyed_bus_id = psspy.abrnchar(4, 1, 3, 3, 1, 'ID')[1][0]                                              #ID
            conveyed_bus_fr_to_nmb = [int(str(conveyed_bus_fr_nmb[c])+str(conveyed_bus_t_nmb[c])) for c in range(len(conveyed_bus_t_nmb))]
            is_this_line_already_exist_fr = np.where(int(str(220022)+str(feeder_connected_to_bus[i])) == np.array(conveyed_bus_fr_to_nmb))
            is_this_line_already_exist_to = np.where(int(str(feeder_connected_fr_bus[i])+str(220022)) == np.array(conveyed_bus_fr_to_nmb))
            exist_id_fr = [conveyed_bus_id[id].strip() for id in is_this_line_already_exist_fr[0] if is_this_line_already_exist_fr[0].shape[0] > 0]
            exist_id_to = [conveyed_bus_id[id].strip() for id in is_this_line_already_exist_to[0] if is_this_line_already_exist_to[0].shape[0] > 0]
            new_id_lst = ['1', '2', '3', '4', '5']
            new_ckt_fr = [new_id_lst[nw] if len(exist_id_fr) > 0 else '1' for nw in range(len(new_id_lst)) if new_id_lst[nw] not in exist_id_fr] 
            new_ckt_to = [new_id_lst[nw] if len(exist_id_to) > 0 and new_id_lst[nw] not in exist_id_to else '1' for nw in range(len(new_id_lst))] 
            if feeder_connected_fr_bus[i] == 220023:
                psspy.movebrn(feeder_connected_to_bus[i],feeder_connected_fr_bus[i],_s,220022,new_ckt_fr[0])
            elif feeder_connected_to_bus[i] == 220023:
                psspy.movebrn(feeder_connected_fr_bus[i],feeder_connected_to_bus[i],_s,220022,new_ckt_to[0])
            elif feeder_connected_fr_bus[i] == 220024:
                psspy.movebrn(feeder_connected_to_bus[i],feeder_connected_fr_bus[i],_s,220022,new_ckt_fr[0])
            elif feeder_connected_to_bus[i] == 220024:
                psspy.movebrn(feeder_connected_fr_bus[i],feeder_connected_to_bus[i],_s,220022,new_ckt_to[0])
        psspy.bsysinit(1)
        psspy.bsyso(1,220023)
        psspy.extr(1,0,[0,0])
        psspy.bsysinit(1)
        psspy.bsyso(1,220024)
        psspy.extr(1,0,[0,0])
        psspy.save(file_directory+"\\"+sav_ismi+".sav")

def bus_selection_to_split(sav_ismi, ytim, regions, file_directory,manuel_definition = None):
    psspy.case(file_directory+"\\"+sav_ismi+".sav")                                             #Open Folder 
    psspy.progress_output(6,"",[0,0])                                                           #Close output report
    psspy.bsys(1,1,[154., 400.],1, [ytim],0,[],len(regions),regions,2,[2,1])                    #Create a subsystem
    if bool(manuel_definition):
        buses_included_zil_and_enough_line = manuel_definition
    else:
        fr_nmb = psspy.abrnint(1, 1, 3, 4, 1, 'FROMNUMBER')[1][0]
        t_nmb = psspy.abrnint(1, 1, 3, 4, 1, 'TONUMBER')[1][0]                                      #To number of branch
        #This lists present from number + to number + id and it doesn't include zero impedance lines
        fr_to_id_num = [int(str(fr_nmb[i])+str(t_nmb[i])) for i in range(len(fr_nmb)) if int(str(fr_nmb[i])[:5]) == int(str(t_nmb[i])[:5]) if int(str(t_nmb[i])[5]) < 3 if int(str(t_nmb[i])[4]) == 2]
        #Buses included zero impedance line
        buses_included_zil = [fr_to for fr_to in fr_to_id_num if 'K' and 'U' and 'P' and 'L' and 'J' in list(psspy.brnnam(int(str(fr_to)[:6]),int(str(fr_to)[6:]), r"""1""")[1])]
        #Buses included zero impedance line and minimum 4 lines
        buses_included_zil_and_enough_line = []
        for fr_to in buses_included_zil:
            psspy.bsysinit(2), psspy.bsysinit(3)
            psspy.bsyso(2,int(str(fr_to)[:6])), psspy.bsyso(3,int(str(fr_to)[6:]))
            brn_count_in_bus1, brn_count_in_bus2= psspy.abrncount(2, 1, 3, 1, 1)[1], psspy.abrncount(3, 1, 3, 1, 1)[1] 
            if psspy.brnint(int(str(fr_to)[:6]),int(str(fr_to)[6:]),'1','STATUS')[1] == 1:
                #if zil connected to buses is in service, it should be removed from the amount of branches (1 from side, 1 to side, so minus 2)
                brn_count = brn_count_in_bus1 + brn_count_in_bus2 - 2
            else:
                brn_count = brn_count_in_bus1 + brn_count_in_bus2
            if brn_count >= 4:
                buses_included_zil_and_enough_line.append(fr_to)
        
    return buses_included_zil_and_enough_line 
def branches_in_slctd_bus(buses_included_zil_and_enough_line, tr_include = True, atr_include = True):
    #Branch list in selected buses
    fr_number_selected, to_number_selected, id_selected = [], [], []
    for fr_to in buses_included_zil_and_enough_line:
        psspy.bsysinit(2), psspy.bsysinit(3)
        fr_number_slctd, to_number_slctd, id_slctd = [], [], []
        psspy.bsyso(2,int(str(fr_to)[:6])), psspy.bsyso(3,int(str(fr_to)[6:]))
        
        fr_nmb_selected_bus1, t_nmb_selected_bus1, id_selected_bus1 = psspy.abrnint(2, 1, 3, 3, 1, 'FROMNUMBER')[1][0], psspy.abrnint(2, 1, 3, 3, 1, 'TONUMBER')[1][0], psspy.abrnchar(2, 1, 3, 3, 1, 'ID')[1][0]
        fr_nmb_selected_bus2, t_nmb_selected_bus2, id_selected_bus2 = psspy.abrnint(3, 1, 3, 3, 1, 'FROMNUMBER')[1][0], psspy.abrnint(3, 1, 3, 3, 1, 'TONUMBER')[1][0], psspy.abrnchar(3, 1, 3, 3, 1, 'ID')[1][0]
        fr_nmb_slctd_bus1 = [fr_nmb_selected_bus1[i] for i in range(len(fr_nmb_selected_bus1)) if int(str(fr_nmb_selected_bus1[i])[:5]) != int(str(t_nmb_selected_bus1[i])[:5])]
        t_nmb_slctd_bus1 = [t_nmb_selected_bus1[i] for i in range(len(t_nmb_selected_bus1)) if int(str(fr_nmb_selected_bus1[i])[:5]) != int(str(t_nmb_selected_bus1[i])[:5])]
        id_slctd_bus1 = [id_selected_bus1[i] for i in range(len(id_selected_bus1)) if int(str(fr_nmb_selected_bus1[i])[:5]) != int(str(t_nmb_selected_bus1[i])[:5])]
        fr_nmb_slctd_bus2 = [fr_nmb_selected_bus2[i] for i in range(len(fr_nmb_selected_bus2)) if int(str(fr_nmb_selected_bus2[i])[:5]) != int(str(t_nmb_selected_bus2[i])[:5])]
        t_nmb_slctd_bus2 = [t_nmb_selected_bus2[i] for i in range(len(t_nmb_selected_bus2)) if int(str(fr_nmb_selected_bus2[i])[:5]) != int(str(t_nmb_selected_bus2[i])[:5])]
        id_slctd_bus2 = [id_selected_bus2[i] for i in range(len(id_selected_bus2)) if int(str(fr_nmb_selected_bus2[i])[:5]) != int(str(t_nmb_selected_bus2[i])[:5])]
        [fr_number_slctd.append(fr_nmb) for fr_nmb in fr_nmb_slctd_bus1], [fr_number_slctd.append(fr_nmb2) for fr_nmb2 in fr_nmb_slctd_bus2]
        [to_number_slctd.append(t_nmb) for t_nmb in t_nmb_slctd_bus1], [to_number_slctd.append(t_nmb2) for t_nmb2 in t_nmb_slctd_bus2]
        [id_slctd.append(id_nmb) for id_nmb in id_slctd_bus1], [id_slctd.append(id_nmb2) for id_nmb2 in id_slctd_bus2]
        fr_number_selected.append(fr_number_slctd)
        to_number_selected.append(to_number_slctd)
        id_selected.append(id_slctd)
    fr_to_nmb_selected_buses = [[int(str(fr_number_selected[i][j])+str(to_number_selected[i][j])+id_selected[i][j]) for j in range(len(fr_number_selected[i]))] for i in range(len(fr_number_selected))]
    #This section removes transformer branches from fr_to_nmb_selected_buses. Therefore, if you select tr_include as True, positions of transformers in selected substations will not change
    if tr_include == False:
        tr_idx = [[j for j in range(len(fr_to_nmb_selected_buses[i])) if int(str(fr_to_nmb_selected_buses[i][j])[4]) > 2 or int(str(fr_to_nmb_selected_buses[i][j])[10]) > 2] for i in range(len(fr_to_nmb_selected_buses))]
        [[fr_to_nmb_selected_buses[i].remove(fr_to_nmb_selected_buses[i][tr_idx[i][-j-1]]) for j in range(len(tr_idx[i]))] for i in range(len(tr_idx))]
    #This section removes autotransformer branches from fr_to_nmb_selected_buses
    if atr_include == False:
        atr_idx = [[j for j in range(len(fr_to_nmb_selected_buses[i])) if int(str(fr_to_nmb_selected_buses[i][j])[4]) == 1 and int(str(fr_to_nmb_selected_buses[i][j])[10]) == 2] for i in range(len(fr_to_nmb_selected_buses))]
        [[fr_to_nmb_selected_buses[i].remove(fr_to_nmb_selected_buses[i][atr_idx[i][-j-1]]) for j in range(len(atr_idx[i]))] for i in range(len(atr_idx))]
    name_dict = [{psspy.brnnam(int(str(fr_to_nmb_selected_buses[i][j])[:6]), int(str(fr_to_nmb_selected_buses[i][j])[6:12]), str(fr_to_nmb_selected_buses[i][j])[12])[1].strip()[:4]:psspy.brnnam(int(str(fr_to_nmb_selected_buses[i][j])[:6]), int(str(fr_to_nmb_selected_buses[i][j])[6:12]), str(fr_to_nmb_selected_buses[i][j])[12])[1].strip()[5:] for j in range(len(fr_to_nmb_selected_buses[i]))} for i in range(len(fr_to_nmb_selected_buses))]
    number_of_name = [[psspy.brnnam(int(str(fr_to_nmb_selected_buses[i][j])[:6]), int(str(fr_to_nmb_selected_buses[i][j])[6:12]), str(fr_to_nmb_selected_buses[i][j])[12])[1].strip()[:4] for j in range(len(fr_to_nmb_selected_buses[i]))] for i in range(len(fr_to_nmb_selected_buses))]
    return fr_to_nmb_selected_buses, name_dict, number_of_name
def individual_structure(name_dictionary):
    sorted_name_dictionary = [dict(sorted(name_dictionaries.items())) for name_dictionaries in name_dictionary]
    individual_number_of_name = [list(sorted_name_dictionary[i].keys()) for i in range(len(sorted_name_dictionary))]
    return individual_number_of_name
def initial_position(buses_included_zil_and_enough_line, fr_to_nmb_selected_buses, individual_number, current_number_of_name):
    start_pos = []
    for i in range(len(individual_number)):
        temp_pos = []
        for j in range(len(individual_number[i])):
            idx = current_number_of_name[i].index(individual_number[i][j])
            if (int(str(buses_included_zil_and_enough_line[i])[:6]) == int(str(fr_to_nmb_selected_buses[i][idx])[:6])) or (int(str(buses_included_zil_and_enough_line[i])[6:12]) == int(str(fr_to_nmb_selected_buses[i][idx])[:6])):
                connected_bus = int(str(fr_to_nmb_selected_buses[i][idx])[5])
            else:
                connected_bus = int(str(fr_to_nmb_selected_buses[i][idx])[11])
            temp_pos.append(connected_bus)
        start_pos.append(temp_pos)
    return start_pos
def generate_position(start_pos):
    random_position_generator = [[randint(1,2) for j in range(len(start_pos[i]))] for i in range(len(start_pos))]
    return random_position_generator
def position_control(buses_included_zil_and_enough_line, position, tr_include = False, atr_include = False):
    if tr_include==True or atr_include==True:
        #Creating autotransformers labels which work as bank.
        with open(r"bank_list\bank_label.txt",'r') as file:
            lines = file.readlines()
            double_otr_list = np.array([line.rstrip() for line in lines])
        try:
            fr_to_nmb_selected_buses, name_dict, number_of_name = branches_in_slctd_bus(buses_included_zil_and_enough_line, tr_include = tr_include, atr_include = atr_include)
        except:
            print("json dosyasıyla mevcut sav dosyasında bulunan toplam fider sayıları eşit değil!")
        try:
            int_number_of_name = [[int(number_of_name[i][j]) for j in range(len(number_of_name[i]))] for i in range(len(number_of_name))]
        except:
            print("Aynı trafo merkezinde bulunan iletim teçhizatının branch name alanında bulunan 4 haneli numara etiket bilgisi aynı olmamalıdır!")
            print("Etiket bilgisi tam sayı olmalıdır!")
        fr_to_otr_number_of_name = [[int_number_of_name[i][j] for j in range(len(fr_to_nmb_selected_buses[i])) if (int(str(fr_to_nmb_selected_buses[i][j])[4]) == 1 and int(str(fr_to_nmb_selected_buses[i][j])[10]) == 2)] for i in range(len(fr_to_nmb_selected_buses))]
        #Determine the index of parallel autotransformers in the number_of_name which is created from otr_name
        ind = individual_structure(name_dict)
        int_ind = [[int(ind[i][j]) for j in range(len(ind[i]))] for i in range(len(ind))]
        idx_double_otr_fr_to_id = [[[int_ind[i].index(int(str(double)[:4])), int_ind[i].index(int(str(double)[4:]))] for double in double_otr_list if (int(str(double)[:4]) and int(str(double)[4:])) in fr_to_otr_number_of_name[i]]for i in range(len(fr_to_otr_number_of_name))]
        idx_line = [[int_ind[i].index(int_number_of_name[i][j]) for j in range(len(int_ind[i])) if (int(str(fr_to_nmb_selected_buses[i][j])[4])==2) and (int(str(fr_to_nmb_selected_buses[i][j])[10])==2)] for i in range(len(int_ind)) ]
        idx_tr = [[j for j in range(len(ind[i])) if j not in idx_line[i]] for i in range(len(ind))]
        position_tobe_control = [[position[i][idx_line[i][j]] for j in range(len(idx_line[i]))] for i in range(len(idx_line))]
    else:
        position_tobe_control=copy.deepcopy(position)
    for pos in range(len(position_tobe_control)):
        position_one = np.where(1 == np.array(position_tobe_control[pos]))
        position_two = np.where(2 == np.array(position_tobe_control[pos]))
        idx1, idx2 = 0, 0
        while position_one[0].shape[0] == 1:
            if tr_include==True or atr_include==True:
                position[pos][idx1] = 1
                position_tobe_control = [[position[i][idx_line[i][j]] for j in range(len(idx_line[i]))] for i in range(len(idx_line))]
                position_one = np.where(1 == np.array(position_tobe_control[pos]))
            else:
                position_tobe_control[pos][position_two[0][idx1]] = 1   #If one busbar has one branch, then one more branch will be added to the related busbar. 
                position_one = np.where(1 == np.array(position_tobe_control[pos]))
            idx1 += 1
        while position_two[0].shape[0] == 1:
            if tr_include==True or atr_include==True:
                position[pos][idx2] = 2
                position_tobe_control = [[position[i][idx_line[i][j]] for j in range(len(idx_line[i]))] for i in range(len(idx_line))]
                position_two = np.where(2 == np.array(position_tobe_control[pos]))
            else:
                position_tobe_control[pos][idx2] = 2
                position_two = np.where(2 == np.array(position_tobe_control[pos]))
            idx2 += 1
        if position_one[0].shape[0] == 0:
            for tr_cor in range(len(idx_tr[pos])):
                position[pos][idx_tr[pos][tr_cor]] = 2
        if position_two[0].shape[0] == 0:
            for tr_cor in range(len(idx_tr[pos])):
                position[pos][idx_tr[pos][tr_cor]] = 1
        
    if tr_include==True or atr_include==True:
        #Parallel otr position correction
        for i in range(len(idx_double_otr_fr_to_id)):
            if len(idx_double_otr_fr_to_id) > 0:
                for j in range(len(idx_double_otr_fr_to_id[i])):
                    position[i][idx_double_otr_fr_to_id[i][j][1]] = position[i][idx_double_otr_fr_to_id[i][j][0]]

    return position
def zil_control(position,fr_to_nmb_selected_buses, number_of_name, ind, tr_include = True, atr_include = True):
    #If all branches are connected to one bus, then zero impedance line between busbars will be in service.
    if tr_include==True or atr_include==True:
        pos_tupl = [[(str(i)+str(j), position[i][j]) for j in range(len(position[i])) if (int(str(fr_to_nmb_selected_buses[i][number_of_name[i].index(ind[i][j])])[4]) == 2 and int(str(fr_to_nmb_selected_buses[i][number_of_name[i].index(ind[i][j])])[10]) == 2)] for i in range(len(position))]            
        position_tobe_control = [[pos_tupl[i][j][1] for j in range(len(pos_tupl[i])) ] for i in range(len(pos_tupl))]            
    else:
        position_tobe_control=copy.deepcopy(position)
    zil_situation = []
    for pos in position_tobe_control:   
        position_one = np.where(1 == np.array(pos))
        position_two = np.where(2 == np.array(pos)) 
        if position_one[0].shape[0] == 0 or position_two[0].shape[0] == 0:
            zil_situation.append(1)
        else:
            zil_situation.append(0)   
    return zil_situation
def move_branch(position, buses_included_zil_and_enough_line, tr_include = True, atr_include = True):
    #buses_included_zil_and_enough_line = bus_selection_to_split(sav_ismi, ytim, regions, file_directory, manuel_definition=manuel_def_bus)
    #Branch list in selected buses
    fr_to_nmb_selected_buses, name_dict, number_of_name = branches_in_slctd_bus(buses_included_zil_and_enough_line, tr_include = tr_include, atr_include = atr_include)
    ind = individual_structure(name_dict)
    zil_situation = zil_control(position, fr_to_nmb_selected_buses, number_of_name, ind, tr_include=tr_include, atr_include=atr_include)
    for j in range(len(fr_to_nmb_selected_buses)):
        fr_to_nmb_selected_buses, name_dict, number_of_name = branches_in_slctd_bus(buses_included_zil_and_enough_line, tr_include = tr_include, atr_include = atr_include)
        if zil_situation[j] == 0:
            #disconnect zero impedance line
            if (int(str(buses_included_zil_and_enough_line[j])[4]) == 2) or (int(str(buses_included_zil_and_enough_line[j])[10]) == 2):
                #If substation have buses to be split, check each buses whether in service or not. If related bus is out of service and branches will be connected to the bus, reconnect related bus and make out of service the zero impedance line between two buses in the substation
                #From side control
                if (int(str(buses_included_zil_and_enough_line[j])[:6]) == int(str(fr_to_nmb_selected_buses[j][number_of_name[j].index(ind[j][0])])[:6])) or (int(str(buses_included_zil_and_enough_line[j])[6:12]) == int(str(fr_to_nmb_selected_buses[j][number_of_name[j].index(ind[j][0])])[:6])):
                    subst = str(buses_included_zil_and_enough_line[j])[:5]
                    zero_impedance_line = int(subst+'1'+subst+'2')
                    psspy.bsysinit(5), psspy.bsysinit(6)
                    psspy.bsyso(5,int(subst+'1')), psspy.bsyso(6,int(subst+'2'))
                    bus_count1, bus_count2 = psspy.abuscount(5, 1)[1], psspy.abuscount(6, 1)[1]
                    if bus_count1 == 0 and (1 in position[j]):
                        psspy.bsysinit(1)
                        psspy.bsyso(1,int(subst+'1'))
                        psspy.recn(int(subst+'1'))
                    elif bus_count2 == 0 and (2 in position[j]):
                        psspy.bsysinit(1)
                        psspy.bsyso(1,int(subst+'2'))
                        psspy.recn(int(subst+'2'))
                else:
                #To side control
                    subst = str(buses_included_zil_and_enough_line[j])[6:11]
                    zero_impedance_line = int(subst+'1'+subst+'2')
                    psspy.bsysinit(5), psspy.bsysinit(6)
                    psspy.bsyso(5,int(subst+'1')), psspy.bsyso(6,int(subst+'2'))
                    bus_count1, bus_count2 = psspy.abuscount(5, 1)[1], psspy.abuscount(6, 1)[1]
                    if bus_count1 == 0 and (1 in position[j]):
                        psspy.bsysinit(1)
                        psspy.bsyso(1,int(subst+'1'))
                        psspy.recn(int(subst+'1'))
                    elif bus_count2 == 0 and (2 in position[j]):
                        psspy.bsysinit(1)
                        psspy.bsyso(1,int(subst+'2'))
                        psspy.recn(int(subst+'2'))
                psspy.system_swd_chng(int(subst+'1'),int(subst+'2'),r"""1""",[0,_i,_i,_i],_f,[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],_s)
        else:
            #connect zero impedance line
            if (int(str(buses_included_zil_and_enough_line[j])[:6]) == int(str(fr_to_nmb_selected_buses[j][number_of_name[j].index(ind[j][0])])[:6])) or (int(str(buses_included_zil_and_enough_line[j])[6:12]) == int(str(fr_to_nmb_selected_buses[j][number_of_name[j].index(ind[j][0])])[:6])):
                subst = str(buses_included_zil_and_enough_line[j])[:5]
                psspy.system_swd_chng(int(subst+'1'),int(subst+'2'),r"""1""",[1,_i,_i,_i],_f,[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],_s)     
            else:
                #connect zero impedance line
                subst = str(buses_included_zil_and_enough_line[j])[6:11]
                psspy.system_swd_chng(int(subst+'1'),int(subst+'2'),r"""1""",[1,_i,_i,_i],_f,[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0],_s)
        if zil_situation[j] == 0:
            #Move lines 
            for i in range(len(position[j])):
                branch_idx = number_of_name[j].index(ind[j][i])
                if (int(str(buses_included_zil_and_enough_line[j])[:6]) == int(str(fr_to_nmb_selected_buses[j][branch_idx])[:6])) or (int(str(buses_included_zil_and_enough_line[j])[6:12]) == int(str(fr_to_nmb_selected_buses[j][branch_idx])[:6])):
                    if position[j][i] != int(str(fr_to_nmb_selected_buses[j][branch_idx])[5]):
                        new_from_number = int(str(fr_to_nmb_selected_buses[j][branch_idx])[:5]+str(position[j][i]))
                        to_number, from_number, id_no = int(str(fr_to_nmb_selected_buses[j][branch_idx])[6:12]), int(str(fr_to_nmb_selected_buses[j][branch_idx])[:6]), str(fr_to_nmb_selected_buses[j][branch_idx])[12]
                        psspy.bsysinit(4)
                        psspy.bsyso(4,new_from_number)
                        conveyed_bus_fr_nmb = psspy.abrnint(4, 1, 3, 4, 1, 'FROMNUMBER')[1][0]                                   #From number of branch
                        conveyed_bus_t_nmb = psspy.abrnint(4, 1, 3, 4, 1, 'TONUMBER')[1][0]                                      #To number of branch
                        conveyed_bus_id = psspy.abrnchar(4, 1, 3, 4, 1, 'ID')[1][0]                                              #ID
                        conveyed_bus_fr_to_nmb = [int(str(conveyed_bus_fr_nmb[c])+str(conveyed_bus_t_nmb[c])) for c in range(len(conveyed_bus_t_nmb))]
                        is_this_line_already_exist = np.where(int(str(new_from_number)+str(to_number)) == np.array(conveyed_bus_fr_to_nmb))
                        exist_id = [conveyed_bus_id[id].strip() for id in is_this_line_already_exist[0] if is_this_line_already_exist[0].shape[0] > 0]
                        new_id_lst = ['1', '2', '3', '4', '5', '6', '7']
                        new_ckt = [new_id_lst[nw] if len(exist_id) > 0 else '1' for nw in range(len(new_id_lst)) if new_id_lst[nw] not in exist_id]
                        psspy.movebrn(to_number, from_number, id_no, new_from_number, new_ckt[0])
                else:
                    if position[j][i] != int(str(fr_to_nmb_selected_buses[j][branch_idx])[11]):
                        new_to_number = int(str(fr_to_nmb_selected_buses[j][branch_idx])[6:11]+str(position[j][i]))
                        to_number, from_number, id_no = int(str(fr_to_nmb_selected_buses[j][branch_idx])[6:12]), int(str(fr_to_nmb_selected_buses[j][branch_idx])[:6]), str(fr_to_nmb_selected_buses[j][branch_idx])[12]
                        psspy.bsysinit(4)
                        psspy.bsyso(4,new_to_number)
                        conveyed_bus_fr_nmb = psspy.abrnint(4, 1, 3, 4, 1, 'FROMNUMBER')[1][0]                                   #From number of branch
                        conveyed_bus_t_nmb = psspy.abrnint(4, 1, 3, 4, 1, 'TONUMBER')[1][0]                                      #To number of branch
                        conveyed_bus_id = psspy.abrnchar(4, 1, 3, 4, 1, 'ID')[1][0]                                              #ID
                        conveyed_bus_fr_to_nmb = [int(str(conveyed_bus_fr_nmb[c])+str(conveyed_bus_t_nmb[c])) for c in range(len(conveyed_bus_t_nmb))]
                        is_this_line_already_exist = np.where(int(str(from_number)+str(new_to_number)) == np.array(conveyed_bus_fr_to_nmb))
                        exist_id = [conveyed_bus_id[id].strip() for id in is_this_line_already_exist[0] if is_this_line_already_exist[0].shape[0] > 0]
                        new_id_lst = ['1', '2', '3', '4', '5', '6', '7']
                        new_ckt = [new_id_lst[nw] if len(exist_id) > 0 else '1' for nw in range(len(new_id_lst)) if new_id_lst[nw] not in exist_id]
                        psspy.movebrn(from_number, to_number, id_no, new_to_number, new_ckt[0])
    return zil_situation