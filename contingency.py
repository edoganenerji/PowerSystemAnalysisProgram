#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

MIT License
ŞAP version 2
Copyright (c) 2022 Dr. Erdi Do�an

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
## Initialization
import os, sys
sys.path.append(r"C:\Program Files\PTI\PSSE35\35.2\PSSPY37")
os.environ['PATH'] = r"C:\Program Files\PTI\PSSE35\35.2\PSSBIN;" + os.environ['PATH']
import psse35
psse35.set_minor(2)
import psspy
import pssarrays
import numpy as np
import pandas as pd
_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()
psspy.psseinit(150000)
class contingency():
    def __init__(self,ytim,regions, file_name, line_rate = "RATEA", load_change = True):
        self.file_name, self.line_rate = file_name, line_rate
        self.bus_number = None
        self.bus_name = None
        self.bus_voltage = None
        self.from_bus_number = None
        self.to_bus_number = None
        self.from_bus_name = None
        self.to_bus_name = None
        self.branch_id = None
        self.branch_name = None
        self.power_flow = None
        self.power_flow_percent = None
        self.power_flow_limit = None
        self.power_data = None
        self.con_pd = None
        self.bank_label = None
        self.islanding_buses = None
        self.generator_name = None
        self.generator_number = None
        self.gen_regulated_bus = None
        self.gen_bus_number = None
        self.outage_explaining = None
        self.outage_frnumber = None
        self.outage_tonumber = None
        self.outage_frname = None
        self.outage_toname = None
        self.outage_lineid = None
        self.mon_data = pd.DataFrame({"From Bus": np.array([]), "To Bus": np.array([]), "From Name": np.array([]), "To Name": np.array([]), "ID": np.array([]), "Power Flow(%)": np.array([]), "Power Flow(MVA)": np.array([]), line_rate: np.array([]), "Label" : np.array([])})
        self.mon_data_voltage = pd.DataFrame({"Bus Number": np.array([]), "Bus Name": np.array([]), "Voltage": np.array([])})
        #Branch list which will exclude from being disconnected branch list because of radial connection
        with open(r"exception_list\fr_num.txt",'r') as file:
            lines = file.readlines()
            self.not_disconnect_fr_num = [int(line.rstrip()) for line in lines]
        with open(r"exception_list\to_num.txt",'r') as file:
            lines = file.readlines()
            self.not_disconnect_to_num = [int(line.rstrip()) for line in lines]
        with open(r"exception_list\fr_name.txt",'r') as file:
            lines = file.readlines()
            self.not_disconnect_fr_name = [line.rstrip() for line in lines]
        with open(r"exception_list\to_name.txt",'r') as file:
            lines = file.readlines()
            self.not_disconnect_to_name = [line.rstrip() for line in lines]
        self.nottobe_disc_fr_to_num = [int(str(self.not_disconnect_fr_num[i])+str(self.not_disconnect_to_num[i])) for i in range(len(self.not_disconnect_to_num))]
        #Creating autotransformers labels which work as bank.
        with open(r"bank_list\bank_label.txt",'r') as file:
            lines = file.readlines()
            self.bank_label = np.array([line.rstrip() for line in lines])
        self.firstsideatrlabelofbank = np.array([first_label[:4] for first_label in self.bank_label])
        self.secondsideatrlabelofbank = np.array([first_label[4:] for first_label in self.bank_label])
        #If a gas turbine is out of service, the generation of the steam turbine which works with it  should be reduced at half.
        #Therefore gas_gen and steam_gen_relatedto_gasgen lists are created.
        with open(r"gas_steam_gen_list\gasgen_list.txt",'r') as file:
            lines = file.readlines()
            self.gas_gen = np.array([int(line.rstrip()) for line in lines])
        with open(r"gas_steam_gen_list\steamgen_rt_gasgen.txt",'r') as file:
            lines = file.readlines()
            self.steam_gen_relatedto_gasgen = np.array([int(line.rstrip()) for line in lines])
        self.open_case(file_name)
        if load_change == True:
            self.multiple_load_change()
        self.short_circuit_data = pd.DataFrame({"Bus Number": np.array([]), "Bus Name": np.array([]),"3-phase Fault": np.array([]), "1-phase Fault": np.array([]) })
        self.create_subsystem(ytim,regions)
        self.open_case(file_name)
        #Display extended results in printing panda dataframe
        display = pd.options.display
        display.max_columns = 1000
        display.max_rows = 30000
        display.max_colwidth = 199
        display.width = 1000
    def open_case(self,file_name):
        #Open file
        psspy.case(file_name)
        psspy.progress_output(6,"",[0,0])
    
    def create_subsystem(self,ytim,regions):
        #Make subsystem according to dispatching center and region
        psspy.bsys(1,1,[154., 400.],1, [ytim],0,[],len(regions),regions,2,[2,1])
        psspy.bsys(7,0,[ 0.38, 400.],1,[ytim],0,[],len(regions),regions,1,[7])
    def load_change(self, subs, power_amount, show_case=True):
        siddik, kroman1, kroman2, colak1, colak2, colak3, asilcelik1, asilcelik2 = 217241, 211441, 211442, 211541, 211542, 211545, 215841, 215842
        erdemir11, erdemir12, erdemir13, erdemir21, erdemir22, orhangazi1, orhangazi2 = 231351, 231352, 231353, 231451, 231452, 220841, 220842
        if subs == siddik or subs == kroman1 or subs == kroman2 or subs == colak1 or subs == colak2 \
           or subs == colak3 or subs == asilcelik1 or subs == asilcelik2\
           or subs == erdemir11 or subs == erdemir12 or subs == erdemir13 or subs == erdemir21\
           or subs == erdemir22 or subs == orhangazi1 or subs == orhangazi2:
            psspy.bsysinit(1)
            psspy.bsyso(1,subs)
        load_bus_count = psspy.abuscount(1, 1)[1]
        if load_bus_count == 0:
            psspy.recn(subs)
            psspy.load_chng_5(subs,r"""1""",[1,_i,_i,_i,_i,_i,_i],[power_amount,_f,_f,_f,_f,_f,_f,_f])
            psspy.fdns([0,0,0,1,1,1,0,0])
            load_flow = psspy.aloadreal(1, 1, 'MVAACT')[1]
            loadbus_name = psspy.abuschar(1, 1, 'NAME')[1]
            if show_case == True:
                print(("%d numarali %sTM'de servis harici olan bara servise alinmis ve 1 adet yuk %.1f MVA'ya ayarlanmistir."%(subs,loadbus_name[0][0],load_flow[0][0])))
        else:
            psspy.load_chng_5(subs,r"""1""",[1,_i,_i,_i,_i,_i,_i],[power_amount,_f,_f,_f,_f,_f,_f,_f])
            psspy.fdns([0,0,0,1,1,1,0,0])
            load_f2 = psspy.aloadreal(1, 1, 'MVAACT')[1]
            loadbus_name = psspy.abuschar(1, 1, 'NAME')[1]
            if show_case == True:
                print(("%d numarali %sTM'de 1 adet yuk %.1f MVA'ya ayarlanmistir."%(subs,loadbus_name[0][0], load_f2[0][0])))
    def multiple_load_change(self):
        self.load_list_tobechange = [217241, 211441, 211442, 211541, 211542, 211545, 215841, 215842, 231351, 231352, 231353, 231451, 231452, 220841, 220842]
        self.power_list           = [90, 110, 40, 15, 110, 225, 20, 50, 100, 25, 25, 25, 25, 50, 25]
        for i in range(len(self.load_list_tobechange)):
            self.load_change(self.load_list_tobechange[i], self.power_list[i], show_case=False)
        psspy.save(self.file_name) 
    def island_detection(self):
        treeobj = psspy.treedat()
        IslandBuses = treeobj['island_busnum']
        self.islanding_buses = [IslandBuses[i][j] for i in range(len(IslandBuses)) for j in range(len(IslandBuses[i])) if len(IslandBuses[i]) > 0 if int(str(IslandBuses[i][j])[4]) <= 2]
        return self.islanding_buses
    def retrieve_data(self):
        #From and To bus number, name and ID lists of lines
        self.fr_bus = psspy.abrnint(1,1,3,1,1,'FROMNUMBER')[1][0]
        self.to_bus = psspy.abrnint(1,1,3,1,1,'TONUMBER')[1][0]
        self.fr_name = psspy.abrnchar(1,1,3,1,1,'FROMNAME')[1][0]
        self.to_name = psspy.abrnchar(1,1,3,1,1,'TONAME')[1][0]
        self.id = psspy.abrnchar(1,1,3,1,1,'ID')[1][0]
        #From and To bus number, name and ID lists of transformers
        self.tr_fr_bus = psspy.atrnint(1,1,3,1,1,'FROMNUMBER')[1][0]
        self.tr_to_bus = psspy.atrnint(1,1,3,1,1,'TONUMBER')[1][0]
        self.tr_fr_name = psspy.atrnchar(1,1,3,1,1,'XFRNAME')[1][0]
        self.tr_to_name = self.tr_fr_name
        self.tr_id = psspy.atrnchar(1,1,3,1,1,'ID')[1][0]
        #From and To bus number, name and ID lists of lines apart from zero impedance lines
        self.from_bus_number = [self.fr_bus[i] for i in range(len(self.fr_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])]
        self.to_bus_number = [self.to_bus[i] for i in range(len(self.to_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])]
        self.from_bus_name = [self.fr_name[i] for i in range(len(self.fr_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])]
        self.to_bus_name = [self.to_name[i] for i in range(len(self.fr_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])]
        self.branch_id = [self.id[i] for i in range(len(self.fr_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])]
        #Adding autotransformers into the line lists
        [self.from_bus_number.append(self.tr_fr_bus[i]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        [self.to_bus_number.append(self.tr_to_bus[i]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        [self.from_bus_name.append(self.tr_fr_name[i].split()[0]+' '+self.tr_fr_name[i].split()[1]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        [self.to_bus_name.append(self.tr_to_name[i].split()[0]+' '+self.tr_to_name[i].split()[1]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        [self.branch_id.append(self.tr_id[i]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        #In order to determine autotransformers which work as bank, autotransformers name label are retrieved.
        self.label_list = np.array([self.from_bus_name[i][:4] if (int(str(self.from_bus_number[i])[4]) == 1 and int(str(self.to_bus_number[i])[4]) == 2) else "None" for i in range(len(self.from_bus_name))])
        #remove label from autotransformers' name
        self.from_bus_name = [self.from_bus_name[i][5:] if self.label_list[i] != "None" else self.from_bus_name[i] for i in range(len(self.from_bus_name))]
        self.to_bus_name = [self.to_bus_name[i][5:] if self.label_list[i] != "None" else self.to_bus_name[i] for i in range(len(self.to_bus_name))]
        
        #Converting the lists into the numpy arrays
        self.from_bus_number, self.to_bus_number = np.array(self.from_bus_number), np.array(self.to_bus_number)
        self.from_bus_name, self.to_bus_name, self.branch_id = np.array(self.from_bus_name), np.array(self.to_bus_name), np.array(self.branch_id)
        self.generator_name = psspy.agenbuschar(7, 1, 'NAME')[1][0]
        self.generator_number = psspy.agenbusint(7, 1, 'NUMBER')[1][0]
        self.gen_regulated_bus = psspy.agenbusint(7, 1, 'IREG')[1][0]
        self.gen_bus_number = psspy.agenbuscount(7, 1)[1]
    def retrieve_power_flow(self, rate='RATEA'):
        #fixed slope decoupled newton raphson power flow
        error = self.multiple_load_flow()
        #Percent loading of lines 
        self.percent_pf = psspy.abrnreal(1, 1, 3, 1, 1, "PCT"+rate)[1][0] 
        #Overloading limits of lines
        self.limit = psspy.abrnreal(1, 1, 3, 1, 1, rate)[1][0]
        #Percent loading of transformers
        self.tr_percent_pf =psspy.atrnreal(1, 1, 3, 1, 1, "PCT"+rate)[1][0]
        #Overloading limits of transformers
        self.tr_limit = psspy.atrnreal(1, 1, 3, 1, 1, rate)[1][0]
        #Bus voltages 
        self.bus_name = np.array(psspy.abuschar(1, 1, "NAME")[1][0])
        self.bus_number = np.array(psspy.abusint(1, 1, "NUMBER")[1][0])
        self.bus_voltage = np.array(psspy.abusreal(1, 1, "PU")[1][0])
        
        self.power_flow_percent = [self.percent_pf[i] for i in range(len(self.fr_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])] 
        self.power_flow_limit = [self.limit[i] for i in range(len(self.fr_bus)) if int(str(self.fr_bus[i])[:5])!=int(str(self.to_bus[i])[:5])]
        [self.power_flow_percent.append(self.tr_percent_pf[i]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        [self.power_flow_limit.append(self.tr_limit[i]) for i in range(len(self.tr_fr_bus)) if int(str(self.tr_to_bus[i])[4]) <= 2]
        self.power_flow_percent, self.power_flow_limit = np.round(np.array(self.power_flow_percent),2), np.round(np.array(self.power_flow_limit),2)
        #Calculating power flow
        self.power_flow = (self.power_flow_percent * self.power_flow_limit)/100.0
        #Creating pandas data frames with power network data
        self.power_data_dict = {"From Bus": self.from_bus_number, "To Bus": self.to_bus_number, "From Name": self.from_bus_name, "To Name": self.to_bus_name, "ID": self.branch_id, "Power Flow(%)": self.power_flow_percent, "Power Flow(MVA)": self.power_flow, rate: self.power_flow_limit, "Label" : self.label_list}
        self.power_data = pd.DataFrame(self.power_data_dict)
        self.power_data = self.power_data.sort_values(by=['Power Flow(%)'], ascending=False)
        self.power_data = self.power_data.reset_index(drop=True)
        
        self.voltage_data_dict = {"Bus Number": self.bus_number, "Bus Name": self.bus_name, "Voltage": self.bus_voltage}
        self.voltage_data = pd.DataFrame(self.voltage_data_dict)
        self.voltage_data = self.voltage_data.sort_values(by=['Voltage'], ascending=True)
        self.voltage_data = self.voltage_data.reset_index(drop=True)
        return error
    def multiple_load_flow(self):
        self.load_flow_result = None
        #fixed slope decoupled newton raphson power flow with flat start
        recompute = psspy.fdns([0,1,0,1,1,1,0,0])

        if recompute > 0:
            return recompute
        recompute = psspy.solved()
        if recompute!=0:
            #Newton raphson power flow with flat start
            psspy.fnsl([0,0,0,1,1,1,0,0])
            recompute = psspy.solved()
            if recompute!=0:
                psspy.fdns([0,1,0,1,1,2,0,0])
                recompute = psspy.solved()
                if recompute != 0:
                    psspy.fdns([0,1,0,1,1,3,0,0])
                    recompute = psspy.solved()
                    if recompute != 0:
                        psspy.fdns([0,1,0,1,1,4,0,0])
                        recompute = psspy.solved()
        if recompute == 0:
            self.load_flow_result = "Met convergence tolerance"
        elif recompute == 1:
            self.load_flow_result = "Iteration limit exceeded"
        elif recompute == 2:
            self.load_flow_result = "Terminated by non-divergent option"
        elif recompute == 3:
            self.load_flow_result = "Blown up"
        elif recompute == 4:
            self.load_flow_result = "Terminated by console interrupt"
        elif recompute == 5:
            self.load_flow_result = "Singular Jacobian matrix or voltage of 0.0 detected"
        elif recompute == 6:
            self.load_flow_result = "Inertial power flow dispatch error (INLF)"
        elif recompute == 7:
            self.load_flow_result = "OPF solution met convergence tolerance"
        elif recompute == 8:
            self.load_flow_result = "Solution not attempted"
        elif recompute == 9:
            self.load_flow_result = "Solution not attempted"
        return recompute
    def N_1_analysis(self, con_rate, result_rate, show_case_base = True, show_case_con = True):
        self.retrieve_data()
        pf_convergence_error = self.retrieve_power_flow(rate = self.line_rate)
        if pf_convergence_error > 0:
            print ("Baslangic guc akisi cozulemedi. Data'yi kontrol edin.")
            print ("\n----------------------------------------------------------------------------------------------------------")
            print ("----------------------------------------------------------------------------------------------------------")
            return "Baslangic guc akisi cozulemedi. Data'yi kontrol edin."
        if show_case_base == True:
            print ("\n----------------------------------------------------------------------------------------------------------")
            print ("TEMEL DURUM GÜÇ AKIŞI")
            print ("----------------------------------------------------------------------------------------------------------")
            self.powerdata = self.power_data
            print (self.powerdata.drop(columns = ["Label"]))
            print ("----------------------------------------------------------------------------------------------------------")
        self.outage_explaining, self.outage_frnumber, self.outage_tonumber, self.outage_frname, self.outage_toname, self.outage_lineid = [], [], [], [], [], []
        self.outage_explaining_voltage, self.outage_frnumber_voltage, self.outage_tonumber_voltage, self.outage_frname_voltage, self.outage_toname_voltage, self.outage_lineid_voltage = [], [], [], [], [], []
        self.regulated_power_data = self.power_data[self.power_data["Power Flow(%)"]>con_rate]
        #Implement line and autotransformer outages
        for i in range(self.regulated_power_data["From Bus"].shape[0]):
            status_check = 0
            if int(str(self.regulated_power_data["From Bus"][i])[4]) == 1 and int(str(self.regulated_power_data["To Bus"][i])[4]) == 2:
                if self.regulated_power_data["Label"][i] not in self.secondsideatrlabelofbank:
                    psspy.two_winding_chng_6(self.regulated_power_data["From Bus"][i],self.regulated_power_data["To Bus"][i],self.regulated_power_data["ID"][i],[0,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)
                    status_check = 1
                    if self.regulated_power_data["Label"][i] in self.firstsideatrlabelofbank:
                        self.first_atr_idx = np.where(self.regulated_power_data["Label"][i]==self.firstsideatrlabelofbank)[0]
                        self.second_atr_idx_indata = np.where(self.bank_label[self.first_atr_idx[0]][4:]==self.regulated_power_data["Label"])[0]
                        if self.second_atr_idx_indata.shape[0] > 0:
                            psspy.two_winding_chng_6(self.regulated_power_data["From Bus"][self.second_atr_idx_indata[0]],self.regulated_power_data["To Bus"][self.second_atr_idx_indata[0]],self.regulated_power_data["ID"][self.second_atr_idx_indata[0]],[0,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)
                            status_check = 2
            else:
                if int(str(self.regulated_power_data["From Bus"][i])+str(self.regulated_power_data["To Bus"][i])) not in self.nottobe_disc_fr_to_num:
                    psspy.branch_chng_3(self.regulated_power_data["From Bus"][i],self.regulated_power_data["To Bus"][i],self.regulated_power_data["ID"][i],[0,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s)
                    status_check = 1
            if status_check != 0:
                self.retrieve_data()
                pf_convergence_error = self.retrieve_power_flow(rate = self.line_rate)
                if pf_convergence_error == 3 and self.load_flow_result == None:
                    print ("\n\n\n---------------------------------------------------------------------------------------------------------------------------------")
                    print ("Servis harici olmasi durumunda radyal baglanti nedeniyle inkitaya neden olan ariza: %i - %i, %s - %s (%s)"%(self.regulated_power_data["From Bus"][i],self.regulated_power_data["To Bus"][i], self.regulated_power_data["From Name"][i], self.regulated_power_data["To Name"][i],self.regulated_power_data["ID"][i]))
                    print ("Inkitaya giden bara numaralari:")
                    print (self.island_detection())
                    print ("--------------------------------------------------------------------------------------------------------------------------------------")
                elif pf_convergence_error == 0:
                    if show_case_con == True:
                        self.con_pd = self.power_data[self.power_data["Power Flow(%)"]>result_rate]
                        if self.con_pd["Power Flow(%)"].shape[0]>0:
                            for _ in range(self.con_pd["From Bus"].shape[0]):
                                self.outage_frnumber.append(int(self.regulated_power_data["From Bus"][i]))
                                self.outage_tonumber.append(int(self.regulated_power_data["To Bus"][i]))
                                self.outage_lineid.append(self.regulated_power_data["ID"][i])
                            if int(str(self.regulated_power_data["From Bus"][i])[4]) == 1 and int(str(self.regulated_power_data["To Bus"][i])[4]) == 2:
                                if status_check == 1:
                                    for _ in range(self.con_pd["From Bus"].shape[0]):
                                        self.outage_explaining.append("OTR:")
                                        self.outage_frname.append(self.regulated_power_data["From Name"][i])
                                        self.outage_toname.append(self.regulated_power_data["To Name"][i])
                                else:
                                    for _ in range(self.con_pd["From Bus"].shape[0]):
                                        self.outage_explaining.append("BANK:")
                                        self.outage_frname.append(self.regulated_power_data["From Name"][i][:-6])
                                        self.outage_toname.append(self.regulated_power_data["To Name"][i][:-6])
                            else:
                                for _ in range(self.con_pd["From Bus"].shape[0]):
                                    self.outage_explaining.append("EIH:")
                                    self.outage_frname.append(self.regulated_power_data["From Name"][i])
                                    self.outage_toname.append(self.regulated_power_data["To Name"][i])
                            self.mon_data = pd.concat([self.mon_data, self.con_pd])
                        self.voltage_violation_up = self.voltage_data[self.voltage_data["Voltage"]>1.05]
                        self.voltage_violation_down = self.voltage_data[self.voltage_data["Voltage"]<0.95]
                        self.voltage_violation = pd.concat([self.voltage_violation_up, self.voltage_violation_down], axis = 0,  join='inner')
                        if self.voltage_violation["Voltage"].shape[0]>0:
                            for _ in range(self.voltage_violation["Voltage"].shape[0]):
                                self.outage_frnumber_voltage.append(int(self.regulated_power_data["From Bus"][i]))
                                self.outage_tonumber_voltage.append(int(self.regulated_power_data["To Bus"][i]))
                                self.outage_lineid_voltage.append(self.regulated_power_data["ID"][i])
                            if int(str(self.regulated_power_data["From Bus"][i])[4]) == 1 and int(str(self.regulated_power_data["To Bus"][i])[4]) == 2:
                                if status_check == 1:
                                    for _ in range(self.voltage_violation["Voltage"].shape[0]):
                                        self.outage_explaining_voltage.append("OTR:")
                                        self.outage_frname_voltage.append(self.regulated_power_data["From Name"][i])
                                        self.outage_toname_voltage.append(self.regulated_power_data["To Name"][i])
                                else:
                                    for _ in range(self.voltage_violation["Voltage"].shape[0]):
                                        self.outage_explaining_voltage.append("BANK:")
                                        self.outage_frname_voltage.append(self.regulated_power_data["From Name"][i][:-6])
                                        self.outage_toname_voltage.append(self.regulated_power_data["To Name"][i][:-6])
                            else:
                                for _ in range(self.voltage_violation["Voltage"].shape[0]):
                                    self.outage_explaining_voltage.append("EIH:")
                                    self.outage_frname_voltage.append(self.regulated_power_data["From Name"][i])
                                    self.outage_toname_voltage.append(self.regulated_power_data["To Name"][i])
                            self.mon_data_voltage = pd.concat([self.mon_data_voltage, self.voltage_violation])
                else:
                    print ("\n\n\n----------------------------------------------------------------------------------------------------------")
                    print (self.load_flow_result)
                    print ("Guc akisi cozulemeyen ariza: %i - %i, %s - %s (%s)"%(self.regulated_power_data["From Bus"][i],self.regulated_power_data["To Bus"][i], self.regulated_power_data["From Name"][i], self.regulated_power_data["To Name"][i],self.regulated_power_data["ID"][i]))
                    print ("----------------------------------------------------------------------------------------------------------")
                if int(str(self.regulated_power_data["From Bus"][i])[4]) == 1 and int(str(self.regulated_power_data["To Bus"][i])[4]) == 2:
                    psspy.two_winding_chng_6(self.regulated_power_data["From Bus"][i],self.regulated_power_data["To Bus"][i],self.regulated_power_data["ID"][i],[1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)
                    if self.regulated_power_data["Label"][i] not in self.secondsideatrlabelofbank:
                        if self.regulated_power_data["Label"][i] in self.firstsideatrlabelofbank:
                            if self.second_atr_idx_indata.shape[0] > 0:
                                psspy.two_winding_chng_6(self.regulated_power_data["From Bus"][self.second_atr_idx_indata[0]],self.regulated_power_data["To Bus"][self.second_atr_idx_indata[0]],self.regulated_power_data["ID"][self.second_atr_idx_indata[0]],[1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)
                else:
                    psspy.branch_chng_3(self.regulated_power_data["From Bus"][i],self.regulated_power_data["To Bus"][i],self.regulated_power_data["ID"][i],[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s)
        #Implement Generator outage                  
        self.regulated_generator_number = np.array([self.generator_number[i] for i in range(len(self.generator_number)) if int(str(self.gen_regulated_bus[i])[4]) <= 2])
        self.regulated_generator_name = np.array([self.generator_name[i] for i in range(len(self.generator_name)) if int(str(self.gen_regulated_bus[i])[4]) <= 2])
        for i in range(self.regulated_generator_number.shape[0]):
            gen_num = self.regulated_generator_number[i]
            gen_name = self.regulated_generator_name[i]
            machine_loading = psspy.macdat(gen_num, r"""1""", "MVA")[1]
            if machine_loading is not None: 
                if machine_loading > 50:
                    if gen_num in self.gas_gen:
                        steam_idx = np.where(gen_num==self.gas_gen)[0]
                        steam_generation = psspy.macdt2(self.steam_gen_relatedto_gasgen[steam_idx[0]],r'''1''', "PQ")[1].real
                        psspy.machine_chng_3(self.steam_gen_relatedto_gasgen[steam_idx[0]],_s,[_i,_i,_i,_i,_i,_i,_i],[ steam_generation/2.0,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
                    psspy.bsysinit(8)
                    psspy.bsyso(8,self.regulated_generator_number[i])
                    psspy.dscn(self.regulated_generator_number[i])
                    self.retrieve_data()
                    pf_convergence_error = self.retrieve_power_flow(rate = self.line_rate)        
                    if pf_convergence_error > 0:
                        print (self.load_flow_result)
                        print ("Guc akisi cozulemeyen ariza: bara no %i, generator ismi %s" % (self.regulated_generator_number[i], self.regulated_generator_name[i]))
                    else:
                        self.con_pd = self.power_data[self.power_data["Power Flow(%)"]>result_rate]
                        if show_case_con == True:
                            if self.con_pd["Power Flow(%)"].shape[0]>0:
                                for _ in range(self.con_pd["From Bus"].shape[0]):
                                    self.outage_explaining.append("Generator:")
                                    self.outage_frname.append(gen_name)
                                    self.outage_toname.append("None")
                                    self.outage_frnumber.append(int(gen_num))
                                    self.outage_tonumber.append("None")
                                    self.outage_lineid.append("None")
                                self.mon_data = pd.concat([self.mon_data, self.con_pd])
                            self.voltage_violation_up = self.voltage_data[self.voltage_data["Voltage"]>1.05]
                            self.voltage_violation_down = self.voltage_data[self.voltage_data["Voltage"]<0.95]
                            self.voltage_violation = pd.concat([self.voltage_violation_up, self.voltage_violation_down], axis = 0,  join='inner')
                            if self.voltage_violation["Voltage"].shape[0]>0:
                                for _ in range(self.voltage_violation["Voltage"].shape[0]):
                                    self.outage_explaining.append("Generator:")
                                    self.outage_frname.append(gen_name)
                                    self.outage_toname.append("None")
                                    self.outage_frnumber.append(int(gen_num))
                                    self.outage_tonumber.append("None")
                                    self.outage_lineid.append("None")
                                self.mon_data_voltage = pd.concat([self.mon_data_voltage, self.voltage_violation])
                    if gen_num in self.gas_gen:
                        steam_idx = np.where(gen_num==self.gas_gen)[0]
                        psspy.machine_chng_3(self.steam_gen_relatedto_gasgen[steam_idx[0]],_s,[_i,_i,_i,_i,_i,_i,_i],[ steam_generation,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
                    psspy.bsysinit(8)
                    psspy.bsyso(8,self.regulated_generator_number[i])
                    psspy.recn(self.regulated_generator_number[i])
        #Organizing contingency data
        self.mon_data['From Bus'] = self.mon_data['From Bus'].apply(np.int64)
        self.mon_data['To Bus'] = self.mon_data['To Bus'].apply(np.int64)
        self.mon_data = self.mon_data.reset_index(drop=True)
        self.mon_data.columns = pd.MultiIndex.from_product([["İzlenen Techizat"], self.mon_data.columns])
        self.outage_data = pd.DataFrame({"Type": np.array(self.outage_explaining), "From Bus": np.array(self.outage_frnumber), "To Bus": np.array(self.outage_tonumber), "From Name": np.array(self.outage_frname), "To Name": np.array(self.outage_toname), "ID": np.array(self.outage_lineid)})
        self.outage_data.columns = pd.MultiIndex.from_product([["Kısıt"], self.outage_data.columns])
        self.outage_data_voltage = pd.DataFrame({"Type": np.array(self.outage_explaining_voltage), "From Bus": np.array(self.outage_frnumber_voltage), "To Bus": np.array(self.outage_tonumber_voltage), "From Name": np.array(self.outage_frname_voltage), "To Name": np.array(self.outage_toname_voltage), "ID": np.array(self.outage_lineid_voltage)})
        self.outage_data_voltage.columns = pd.MultiIndex.from_product([["Kısıt"], self.outage_data_voltage.columns])
        self.mon_data_voltage['Bus Number'] = self.mon_data_voltage['Bus Number'].apply(np.int64)
        self.mon_data_voltage = self.mon_data_voltage.reset_index(drop=True)
        self.mon_data_voltage.columns = pd.MultiIndex.from_product([["İzlenen Techizat"], self.mon_data_voltage.columns])
        self.contingency_data = pd.concat([self.outage_data, self.mon_data], axis = 1,  join='inner')
        self.contingency_data = self.contingency_data.sort_values(by=[('İzlenen Techizat','Power Flow(%)')], ascending=False)
        self.contingency_data = self.contingency_data.reset_index(drop=True)
        self.contingency_data_voltage = pd.concat([self.outage_data_voltage, self.mon_data_voltage], axis = 1,  join='inner')
        self.contingency_data_voltage = self.contingency_data_voltage.sort_values(by=[('İzlenen Techizat','Voltage')], ascending=True)
        self.contingency_data_voltage = self.contingency_data_voltage.reset_index(drop=True)
        if show_case_con == True:
            print ("\n------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            print ("N-1 DURUMU GÜÇ AKIŞI")
            if self.contingency_data[("Kısıt", "From Bus")].shape[0]>0:
                print (self.contingency_data.drop(columns=[('İzlenen Techizat',"Label")]))
                print ("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")  
            else:
                print ("N-1 durumunda %" + str(result_rate) + " üzerinde yüklenen bir teçhizat yoktur.")
                print ("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")  
            if self.contingency_data_voltage[("Kısıt", "From Bus")].shape[0]>0:
                print (self.contingency_data_voltage)
                print ("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")  
            else:
                print ("N-1 durumunda gerilim bozulması yoktur.")
                print ("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")  
    def short_circuit(self, show_case_sc = True):
        self.sc_current = pssarrays.iecs_currents(1,0,1,1,0,0,0,0,0,0,1,1,0,0, 2,2,1,0.1,1.1,self.file_name[:-4]+".iec","","")      
        bus_number_forsc, bus_name, three_phase_sc, phasetoground_sc = [], [], [], []
        for i in range(len(self.sc_current.fltbus)):
            bus_voltage_level = psspy.busdat(self.sc_current.fltbus[i] ,'BASE')[1]
            if bus_voltage_level == 154.0:
                if self.sc_current.flt3ph[i].ia.real > 28000 or self.sc_current.fltlg[i].ia.real > 28000:
                    psspy.bsys(3,0,[ 0.38, 400.],0,[],1,[self.sc_current.fltbus[i]],0,[],0,[])
                    bus_number_forsc.append(self.sc_current.fltbus[i])
                    bus_name.append(psspy.abuschar(3,1,'NAME')[1][0][0])
                    three_phase_sc.append(self.sc_current.flt3ph[i].ia.real)
                    phasetoground_sc.append(self.sc_current.fltlg[i].ia.real)
        self.short_circuit_data["Bus Number"] = np.array(bus_number_forsc)
        self.short_circuit_data["Bus Name"] = np.array(bus_name)
        self.short_circuit_data["3-phase Fault"] = np.round(np.array(three_phase_sc), decimals=2)
        self.short_circuit_data["1-phase Fault"] = np.round(np.array(phasetoground_sc), decimals=2)
        self.short_circuit_data = self.short_circuit_data.sort_values(by=["3-phase Fault"], ascending=False)
        self.short_circuit_data = self.short_circuit_data.reset_index(drop=True)
        print ("\n---------------------------------------------------------------")
        print ("KISA DEVRE ANALİZ SONUCU")
        if show_case_sc == True and self.short_circuit_data["Bus Number"].shape[0]>0:
            print (self.short_circuit_data)
            print ("---------------------------------------------------------------")  
        else:
            print ("Kısa devre akımı 28 kA'in üzerinde herhangi bir bara yoktur")
            print ("---------------------------------------------------------------")    
    def create_dfax(self):
        dir_path = os.getcwd()
        err = psspy.dfax_2([1,1,0],dir_path+"\\"+"kba.sub",dir_path+"\\"+"kba.mon",dir_path+"\\"+"kba.con","kba.dfx")
        if err > 0:
            print("DFAX ERROR TYPE: %i"%(err))
        return err
    def dc_N_1_analysis(self):
        self.create_dfax()
        psspy.dccc_2([1,0,1,0,0,1,1,1],[ 100.0, 90.0, 1.0],r"""kba.dfx""")
#con = contingency(2,[704], r"""C:\Users\erdidogan\Downloads\20220103_1100_SN1_TR0.sav""", line_rate = "RATEA", load_change = True)
#con.N_1_analysis(10, 90, show_case_base = True, show_case_con = True)
#con.dc_N_1_analysis()