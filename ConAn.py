#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 10 Nis 2021

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
import numpy as np
import string
import time as tm
import numpy as np
import search
_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()
psspy.psseinit(150000)
istanbul_trakya, bursa, izmir, istanbul, sakarya, kutahya, denizli, Trakya, KBA, BA = 701, 702, 703, 704, 705, 706, 721, 1, 2, 3
def print_case(loading_list_brn, loading_list_otr, loading_list_voltage, equipment, performance_list_loading, performance_list_reactive, con_num_fr = True, con_num_to = True, con_name_fr = True, con_name_to = True, con_id = True, bank = False):
    #In order to show which branch, autotransformer or generator outage is problem for system security, print_case functions is created.
    ConLine_fr_no = psspy.abrnint(1,1,3,1,1,'FROMNUMBER')[1][0]
    ConLine_to_no = psspy.abrnint(1,1,3,1,1,'TONUMBER')[1][0]
    ConLine_fr_name = psspy.abrnchar(1,1,3,1,1,'FROMNAME')[1][0]
    ConLine_to_name = psspy.abrnchar(1,1,3,1,1,'TONAME')[1][0]
    ConOTR_fr_no = psspy.abrnint(1,1,1,5,1,'FROMNUMBER')[1][0]
    ConOTR_to_no = psspy.abrnint(1,1,1,5,1,'TONUMBER')[1][0]
    ConOTR_fr_name = psspy.abrnchar(1,1,1,5,1,'FROMNAME')[1][0]
    ConOTR_to_name = psspy.abrnchar(1,1,1,5,1,'TONAME')[1][0]
    ConVoltage_bus_num = psspy.abusint(1, 1, "NUMBER")[1][0]
    ConVoltage_bus_name = psspy.abuschar(1, 1, "NAME")[1][0]
    c_brn = 0
    for con in range(len(ConLine_fr_no)):
        if loading_list_brn[con] > 92:
            c_brn += 1
            print ("------------------------------------------------------------")
            print ("Overload Line")
            print ("From Bus Number: %i - To Bus Number: %i"%(ConLine_fr_no[con], ConLine_to_no[con]))
            print ("From Bus Name: %s - To Bus Name: %s"%(ConLine_fr_name[con], ConLine_to_name[con]))
            print ("Percent Loading: %.2f"%(loading_list_brn[con]))
    for con in range(len(ConOTR_fr_no)):
        if loading_list_otr[con] > 92:
            c_brn += 1
            print ("------------------------------------------------------------")
            print ("Overload OTR")
            print ("From Bus Number: %i - To Bus Number: %i"%(ConOTR_fr_no[con], ConOTR_to_no[con]))
            print ("From Bus Name: %s - To Bus Name: %s"%(ConOTR_fr_name[con], ConOTR_to_name[con]))
            print ("Percent Loading: %.2f"%(loading_list_otr[con]))
    if c_brn > 0:
        print (equipment+" Contingency")
        if con_num_fr != True:
            if bank is not False:
                print ("%i - %i , %s - %s (%s)"%(con_num_fr,con_num_to,con_name_fr, con_name_to, con_id))
                print ("%i - %i , %s - %s (%s)"%(bank[0],bank[1],bank[2], bank[2], bank[3]))
            else:
                print ("%i - %i , %s - %s (%s)"%(con_num_fr,con_num_to,con_name_fr, con_name_to, con_id))
        print ("------------------------------------------------------------")
        print ("Overall Loading Performance: %.2f"%(performance_list_loading))
        print ("------------------------------------------------------------")
    c_reak = 0
    for con in range(len(ConVoltage_bus_num)):
        if loading_list_voltage[con] > 1.1 or loading_list_voltage[con] < 0.90:
            c_reak += 1
            print ("------------------------------------------------------------")
            print ("Voltage Performance")
            print ("Bus Name: %s, Bus Number: %i"%(ConVoltage_bus_name[con], ConVoltage_bus_num[con]))
            print ("Voltage Violation in single outage: %.2f"%(loading_list_voltage[con]))
    if c_reak > 0:
        print (equipment + "Contingency")
        print ("%i - %i , %s - %s (%s)"%(con_num_fr,con_num_to,con_name_fr, con_name_to, con_id))
        print ("------------------------------------------------------------") 
        print ("Overall Reactive Power Performance: %.2f"%(performance_list_reactive)) 
        print ("------------------------------------------------------------")  
def multiple_load_flow(): 
    psspy.fdns([0,1,0,1,1,1,0,0])
    recompute = psspy.solved()
    if recompute!=0:
        #psspy.fdns([0,1,0,1,1,0,0,0])
        #recompute = psspy.solved()
        #if recompute != 0:
            #psspy.fdns([0,1,0,1,1,4,0,0])
            #recompute = psspy.solved()
        psspy.fnsl([0,0,0,1,1,1,0,0])
        psspy.fnsl([0,0,0,1,1,0,0,0])
        psspy.fnsl([0,0,0,1,1,0,0,0])
        recompute = psspy.solved()
    else:
        recompute = 0
    return recompute
def calculate_performance(loading_list_brn, loading_list_otr, voltage_list, Vimax, Vimin):
    BranchPerformance1 = (loading_list_brn[((loading_list_brn>=92) & (loading_list_brn<94))])/30.0
    BranchPerformance2 = (loading_list_brn[((loading_list_brn>=94) & (loading_list_brn<96))])/25.0
    BranchPerformance3 = (loading_list_brn[((loading_list_brn>=96) & (loading_list_brn<98))])/20.0
    BranchPerformance4 = (loading_list_brn[((loading_list_brn>=98) & (loading_list_brn<99))])/15.0
    BranchPerformance5 = (loading_list_brn[((loading_list_brn>=99) & (loading_list_brn<100))])/10.0
    BranchPerformance6 = (loading_list_brn[((loading_list_brn>=100) & (loading_list_brn<105))])
    BranchPerformance7 = (loading_list_brn[((loading_list_brn>=105) & (loading_list_brn<110))])*5.0
    BranchPerformance8 = (loading_list_brn[((loading_list_brn>=110) & (loading_list_brn<120))])*10.0
    BranchPerformance9 = (loading_list_brn[((loading_list_brn>=120) & (loading_list_brn<130))])*15.0
    BranchPerformance10 = (loading_list_brn[loading_list_brn>=130])*20.0
    OtrPerformance1 = (loading_list_otr[((loading_list_otr>=100) & (loading_list_otr<103))])/25.0
    OtrPerformance2 = (loading_list_otr[((loading_list_otr>=103) & (loading_list_otr<105))])/20.0
    OtrPerformance3 = (loading_list_otr[((loading_list_otr>=105) & (loading_list_otr<107))])/15.0
    OtrPerformance4 = (loading_list_otr[((loading_list_otr>=107) & (loading_list_otr<108))])/10.0
    OtrPerformance5 = (loading_list_otr[((loading_list_otr>=108) & (loading_list_otr<110))])
    OtrPerformance6 = (loading_list_otr[((loading_list_otr>=110) & (loading_list_otr<115))])*5.0
    OtrPerformance7 = (loading_list_otr[((loading_list_otr>=115) & (loading_list_otr<120))])*10.0
    OtrPerformance8 = (loading_list_otr[((loading_list_otr>=120) & (loading_list_otr<130))])*15.0
    OtrPerformance9 = (loading_list_otr[loading_list_otr>=130])*20.0
    Performance_Index_Loading = np.sum(BranchPerformance1) + np.sum(BranchPerformance2) + np.sum(BranchPerformance3) + np.sum(BranchPerformance4) + np.sum(BranchPerformance5) + np.sum(BranchPerformance6) + np.sum(BranchPerformance7) + np.sum(BranchPerformance8) + np.sum(BranchPerformance9) + np.sum(BranchPerformance10) + np.sum(OtrPerformance1) + np.sum(OtrPerformance2) + np.sum(OtrPerformance3) + np.sum(OtrPerformance4)+ np.sum(OtrPerformance5)+ np.sum(OtrPerformance6)+ np.sum(OtrPerformance7)+ np.sum(OtrPerformance8)+ np.sum(OtrPerformance9)
    ReactiveForConMatrix = np.power(((voltage_list-((Vimax+Vimin)/2))/(Vimax-Vimin)),2)
    Performance_Index_Voltage = np.sum((ReactiveForConMatrix[ReactiveForConMatrix>=0.25])*50.0)
    return Performance_Index_Loading, Performance_Index_Voltage
def contingency_loading():
    BranchLoading = np.array(psspy.abrnreal(1,1,3,1,1,'PCTRATEA')[1][0])
    OTRLoading = np.array(psspy.abrnreal(1,1,1,5,1,'PCTRATEA')[1][0])
    BusVoltage = np.array(psspy.abusreal(1, 1, "PU")[1][0])
    return BranchLoading, OTRLoading, BusVoltage
def islanding_buses():
    treeobj = psspy.treedat()
    IslandBuses = treeobj['island_busnum']
    islanding_buses_154kv = [IslandBuses[i][j] for i in range(len(IslandBuses)) for j in range(len(IslandBuses[i])) if len(IslandBuses[i]) > 0 if int(str(IslandBuses[i][j])[4]) == 2]
    g1 = len(islanding_buses_154kv)
    return g1*500.0
def prepare_otr_data(ytim):
    #Retrieve autotransformer informations from PSSE
    otr_fr = psspy.atrnint(1, 1, 1, 1, 1, 'FROMNUMBER')[1][0]
    otr_to = psspy.atrnint(1, 1, 1, 1, 1, 'TONUMBER')[1][0]
    otr_id = psspy.atrnchar(1, 1, 1, 1, 1, 'ID')[1][0]
    otr_name = psspy.atrnchar(1, 1, 1, 1, 1, 'XFRNAME')[1][0]
    otr_label = [int(name[:4]) for name in otr_name]
    #Parallel autotransformers' label retrieved from otr_name 
    #Creating autotransformers labels which work as bank.
    with open(r"bank_list\bank_label.txt",'r') as file:
        lines = file.readlines()
        double_otr_kba = np.array([int(line.rstrip()) for line in lines])
    double_otr_trakya = [32464343, 32683271, 32745207, 32794931, 32833284, 32885080, 32893292]
    double_otr_izmir = [50094635, 23413843, 38445719, 38864610, 23982401, 38393840, 38413842,38504398,38533851,38643865,50633867,38694952,38754972,24932494] 
                        #CanHavza, BALIKESIR2 A12, BALIKESIR2 A34, MORSAN A, ALIAGA2 A12, ALIAGA2 A34,ALIAGA2 A56, ISIKLAR A, ISIKLAR B,UZUNDERE A,UZUNDERE B,YATAGAN A,YENIKOYTES A,DENIZLI
    idx_double_otr_fr_to_id = []
    if ytim == KBA:
        double_list = double_otr_kba
    elif ytim == Trakya:
        double_list = double_otr_trakya
    elif ytim == BA:
        double_list = double_otr_izmir
    #Determine the index of parallel autotransformers in the otr_label which is created from otr_name
    for double in double_list:
        if (int(str(double)[:4]) and int(str(double)[4:])) in otr_label:
            try:
                idx1 = otr_label.index(int(str(double)[:4]))
                idx2 = otr_label.index(int(str(double)[4:]))
                idx_double_otr_fr_to_id.append(idx1)
                idx_double_otr_fr_to_id.append(idx2)
            except:
                print('Banklarda %i etiketine sahip bir ototrafo yok! Lutfen bank listesini duzeltiniz!'%(double))
    otr_parallel_fr = [otr_fr[idx] for idx in idx_double_otr_fr_to_id] 
    otr_parallel_to = [otr_to[idx] for idx in idx_double_otr_fr_to_id] 
    otr_parallel_id = [otr_id[idx] for idx in idx_double_otr_fr_to_id]
    otr_parallel_name = [otr_name[idx] for idx in idx_double_otr_fr_to_id]
    otr_single_fr = [otr_fr[i] for i in range(len(otr_fr)) if i not in idx_double_otr_fr_to_id] 
    otr_single_to = [otr_to[i] for i in range(len(otr_fr)) if i not in idx_double_otr_fr_to_id] 
    otr_single_id = [otr_id[i] for i in range(len(otr_fr)) if i not in idx_double_otr_fr_to_id]
    otr_single_name = [otr_name[i] for i in range(len(otr_fr)) if i not in idx_double_otr_fr_to_id]
    return otr_parallel_fr, otr_parallel_to, otr_parallel_id, otr_parallel_name, otr_single_fr, otr_single_to, otr_single_id, otr_single_name
def contingency_analysis(sav_ismi, ytim, regions, file_directory, rate, tieLines = None, fast_con = True, show_case = False):
    MajorLinePIList, MajorLineReactivePIList, LinePerformanceIndexList,ReactivePIForBranchConList, Paralel_otr_PI_list, Reactive_PI_Paralel_OTR_list, OTRPerformanceIndexList, ReactivePIForOTRConList, GeneratorPerformanceIndexList, ReactivePIGenConList = [], [], [], [], [], [], [], [], [], []
    if tieLines is not None:
        #Open the file of reduced network
        psspy.case(file_directory+'\\'+sav_ismi+"_ReducedVersion_"+str(regions)+".sav")
        psspy.progress_output(6,"",[0,0])
    #psspy.case(file_directory+'\\'+sav_ismi)
    #psspy.progress_output(6,"",[0,0])
    #Make subsystem according to dispatching center and region
    psspy.bsys(1,1,[154., 400.],1, [ytim],0,[],len(regions),regions,2,[2,1])
    
    #Maximum and minimum allowable voltage levels
    Vimax, Vimin = 1.1, 0.90
    #Fixed slop decoupled Newton-Raphson load flow solution (only flat start)
    psspy.fdns([0,1,0,1,1,1,0,0])
    #The amount of power flows on equipment and the voltage level of busbars
    BaseCaseLine = np.array(psspy.abrnreal(1,1,3,1,1,'PCTRATEC')[1][0])
    BaseCaseOTR = np.array(psspy.abrnreal(1,1,1,5,1,'PCTRATEC')[1][0])
    BaseCaseVoltage = np.array(psspy.abusreal(1, 1, "PU")[1][0])
    #Base case performans is calculated. See calculate_performance function
    base_case_load, base_case_voltage = calculate_performance(BaseCaseLine, BaseCaseOTR, BaseCaseVoltage, Vimax, Vimin)
    base_case_load_regul = base_case_load/10.0
    if show_case == True:
        print_case(BaseCaseLine, BaseCaseOTR, BaseCaseVoltage, "Base Case", base_case_load_regul, base_case_voltage, con_num_fr = True, con_num_to = True, con_name_fr = True, con_name_to = True, con_id = True)
    otr_parallel_fr, otr_parallel_to, otr_parallel_id, otr_parallel_name, otr_single_fr, otr_single_to, otr_single_id, otr_single_name = prepare_otr_data(ytim)
    #Retrieve branch informations from PSSE
    BranchFromNumber, BranchToNumber, BranchID, BranchFromName, BranchToName = psspy.abrnint(1,1,3,1,1,'FROMNUMBER')[1][0], psspy.abrnint(1,1,3,1,1,'TONUMBER')[1][0], psspy.abrnchar(1,1,3,1,1,'ID')[1][0], psspy.abrnchar(1,1,3,1,1,'FROMNAME')[1][0], psspy.abrnchar(1,1,3,1,1,'TONAME')[1][0]
    Br_fr_to_num = [int(str(BranchFromNumber[i])+str(BranchToNumber[i])+str(BranchID[i])) for i in range(len(BranchToNumber))] 
    #Major line outages
    if fast_con == True:
        if regions == [704]:
            major_line_fr_list = [214310, 210111, 290310,210121,210121, 210122, 210122, 214321, 214322, 214321, 214322, 214821, 214822, 211321, 211321, 210021, 210021, 210022, 210022]
            major_line_to_list = [290310, 214310, 219110,211821,211822, 211821, 211822, 214821, 214821, 214822, 214822, 217221, 217221, 211621, 211622, 210921, 210922, 210921, 210922]
            major_line_fr_name = ['DILOVASI','TEPEOREN', 'DILERCELIK', 'TEPEOREN','TEPEOREN','TEPEOREN','TEPEOREN', 'MAKINAOSB', 'MAKINAOSB', 'MAKINAOSB', 'MAKINAOSB', 'MAKINAOSB', 'MAKINAOSB', 'TUZLA', 'TUZLA', 'UMRANIYE', 'UMRANIYE', 'UMRANIYE', 'UMRANIYE']
            major_line_to_name = ['DCELIKSANAL', 'DILOVASI', 'COLAKOGLU', 'GOSB-I','GOSB-I','GOSB-III','GOSB-III', 'DOSB', 'DOSB', 'DOSB', 'DOSB', 'SIDDIK', 'SIDDIK', 'ICMELER', 'ICMELER', 'KBAKKAL', 'KBAKKAL', 'KBAKKAL', 'KBAKKAL']
            major_line_id_list = ['1','1','1','1','1', '1','1','1', '1','1','1', '1','1','1', '1','1','1', '1','1']
            major_fr_to_num = [2143102903101, 2101112143101,2903102191101,2101212118211,2101212118221, 2101222118211, 2101222118221, 2143212148211, 2143222148211, 2143212148221, 2143222148221,2148212172211, 2148222172211, 2113212116211, 2113212116221, 2100212109211, 2100212109221, 2100222109211, 2100222109221]
            for ml in range(len(major_line_fr_list)): 
                if major_fr_to_num[ml] in Br_fr_to_num:
                    psspy.branch_chng_3(major_line_fr_list[ml],major_line_to_list[ml],major_line_id_list[ml],[0,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])               
                    island_check = islanding_buses()
                    if island_check == 0:
                        if multiple_load_flow() > 0:
                            MajorLinePIList.append(300)
                            if show_case == True:
                                print ("Load Flow Solution not Converge with Flat Start in Line Contingency Situation")
                                print ("%i - %i, %s - %s (%s)"%(major_line_fr_list[ml],major_line_to_list[ml],major_line_fr_name[ml],major_line_to_name[ml],major_line_id_list[ml]))
                        else:
                            BranchLoadBaseConLine, BranchLoadBaseConOTR, BaseBusVoltageForBranchCon = contingency_loading()
                            loading_perf, voltage_perf = calculate_performance(BranchLoadBaseConLine, BranchLoadBaseConOTR, BaseBusVoltageForBranchCon, Vimax, Vimin)
                            MajorLinePIList.append(loading_perf)                      
                            MajorLineReactivePIList.append(voltage_perf)
                            if show_case == True:
                                print_case(BranchLoadBaseConLine, BranchLoadBaseConOTR, BaseBusVoltageForBranchCon, "Line", loading_perf, voltage_perf, major_line_fr_list[ml], major_line_to_list[ml], major_line_fr_name[ml],major_line_to_name[ml], int(major_line_id_list[ml]))
                    else:
                        MajorLinePIList.append(island_check)
                        MajorLineReactivePIList = MajorLinePIList
    
                    psspy.branch_chng_3(major_line_fr_list[ml],major_line_to_list[ml],major_line_id_list[ml],[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])   
    #Start main loop for autotransformer outages in order to evaluate system N-1 security
    #Parallel autotransformers
    for i in range(0,len(otr_parallel_fr),2):
        if search.search(int(str(otr_parallel_fr[i])+str(otr_parallel_to[i])),[320010320024]) == -1:
            #Out of service parallel autotransformer
            psspy.two_winding_chng_6(otr_parallel_fr[i],otr_parallel_to[i],otr_parallel_id[i],[0,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[ _f, _f, _f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)                            
            psspy.two_winding_chng_6(otr_parallel_fr[i+1],otr_parallel_to[i+1],otr_parallel_id[i+1],[0,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[ _f, _f, _f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)   
            #Sometimes you should use the flat start or flat start with estimated voltage magnitude and phase angle in order to solve power flow equation
            #Therefore, multiple_load_flow function is created to implement various load flows if the single flat start cannot solve the power flow equations.
            island_check = islanding_buses()
            if island_check == 0:
                if multiple_load_flow() > 0:
                    #If even multiple load flow cannot solve the power flow equations, created bus layout will be punished due to related outage
                    Paralel_otr_PI_list.append(300)
                    if show_case == True:
                        print ("Load Flow Solution not Converge with Flat Start in OTR Contingency Situation")
                        print (otr_parallel_fr[i], otr_parallel_to[i], otr_parallel_id[i], otr_parallel_name[i])
                else:
                    OTRLoadBaseConLine, OTRLoadBaseConOTR, BaseBusVoltageForOTRCon = contingency_loading() 
                    loading_perf, voltage_perf = calculate_performance(OTRLoadBaseConLine, OTRLoadBaseConOTR, BaseBusVoltageForOTRCon, Vimax, Vimin)
                    Paralel_otr_PI_list.append(loading_perf)
                    Reactive_PI_Paralel_OTR_list.append(voltage_perf)
                    if show_case == True:
                        print_case(OTRLoadBaseConLine, OTRLoadBaseConOTR, BaseBusVoltageForOTRCon, "BANK", loading_perf, voltage_perf, otr_parallel_fr[i], otr_parallel_to[i], otr_parallel_name[i], otr_parallel_name[i], otr_parallel_id[i], bank = [otr_parallel_fr[i+1], otr_parallel_to[i+1], otr_parallel_name[i+1], otr_parallel_id [i+1]])
            else:
                Paralel_otr_PI_list.append(island_check)
                Reactive_PI_Paralel_OTR_list = Paralel_otr_PI_list
            #Reconnect parallel autotransformer
            psspy.two_winding_chng_6(otr_parallel_fr[i],otr_parallel_to[i],otr_parallel_id[i],[1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[ _f, _f, _f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)                            
            psspy.two_winding_chng_6(otr_parallel_fr[i+1],otr_parallel_to[i+1],otr_parallel_id[i+1],[1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[ _f, _f, _f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)  
    for i in range(len(otr_single_fr)):
        #Out of service single autotransformer
        psspy.two_winding_chng_6(otr_single_fr[i],otr_single_to[i],otr_single_id[i],[0,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[ _f, _f, _f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)  
        #Sometimes you should use the flat start or flat start with estimated voltage magnitude and phase angle in order to solve power flow equation
        #Therefore, multiple_load_flow function is created to implement various load flows if the single flat start cannot solve the power flow equations.
        island_check = islanding_buses()
        if island_check == 0:
            if multiple_load_flow() > 0:
                #If even multiple load flow cannot solve the power flow equations, created bus layout will be punished due to related outage
                OTRPerformanceIndexList.append(300)
                if show_case == True:
                    print ("Load Flow Solution not Converge with Flat Start in OTR Contingency Situation")
                    print (otr_single_fr[i], otr_single_to[i], otr_single_id[i], otr_single_name[i])
            else:
                OTRLoadBaseConLine, OTRLoadBaseConOTR, BaseBusVoltageForOTRCon = contingency_loading() 
                loading_perf, voltage_perf = calculate_performance(OTRLoadBaseConLine, OTRLoadBaseConOTR, BaseBusVoltageForOTRCon, Vimax, Vimin)
                OTRPerformanceIndexList.append(loading_perf)
                ReactivePIForOTRConList.append(voltage_perf)
                if show_case == True:
                    print_case(OTRLoadBaseConLine, OTRLoadBaseConOTR, BaseBusVoltageForOTRCon, "OTR", loading_perf, voltage_perf, otr_single_fr[i], otr_single_to[i], otr_single_name[i], otr_single_name[i], otr_single_id[i])
        else:
            OTRPerformanceIndexList.append(island_check)
            ReactivePIForOTRConList = OTRPerformanceIndexList
        #Reconnect single autotransformer
        psspy.two_winding_chng_6(otr_single_fr[i],otr_single_to[i],otr_single_id[i],[1,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],[ _f, _f, _f,_f,_f,_f,_f,_f,_f,_f,_f,_f],_s,_s)  
    otr_con = np.sum(np.array(OTRPerformanceIndexList)) + np.sum(np.array(Paralel_otr_PI_list))
    maj_line_con = 0
    MajorLinePIList = 0
    MajorLineReactivePIList = 0
    if fast_con == True:
        if regions == [704]:
            maj_line_con = np.sum(np.array(MajorLinePIList)) + np.sum(np.array(MajorLineReactivePIList))
        
    goon = False
    disregard_list = [221721224321, 216321220821, 216321226021,216321226621,214910290310,219110290310, 210022214121,110521111722,111722113522,111722114821,114821116421,116321116421,116321123421, 222621222821, 222621222822, 123421123621, 211522219121,211521219121, 290310219110 , 210111290310, 210112290310]
    if tieLines is not None:
        tieBranches = tieLines["From-To Branch"].to_numpy().tolist()
        for brn in tieBranches:
            disregard_list.append(brn)
    if fast_con == True and otr_con > 200:
    #If the created bus layout cannot show resilience to autotransformer outages which are most major outages for the 154 kV voltage level, it is not need to calculate branch outages. 
    #Therefore, when the otr_con represented the performance index of autotransformer outages is bigger than a determined number, a punishment is implemented to Line performance index.
        LinePerformanceIndexList.append(3000.0)
    elif fast_con == True and otr_con >100:
        LinePerformanceIndexList.append(300.0)
    if fast_con == True and maj_line_con > 200:
        LinePerformanceIndexList.append(3000.0)
    elif fast_con == True and maj_line_con >100:
        LinePerformanceIndexList.append(300.0)
    if (fast_con == True and otr_con <100 and maj_line_con < 100) or fast_con == False:
        for i in range(len(BranchFromNumber)):
            if int(str(BranchFromNumber[i])+str(BranchToNumber[i])) not in disregard_list:   
                goon = True
            else:
                goon = False
            if goon == True:   
                BranchLoadBase = psspy.brnmsc(BranchFromNumber[i],BranchToNumber[i],BranchID[i],'PCTMVC')[1]
                BranchRate = psspy.brndat(BranchFromNumber[i],BranchToNumber[i],BranchID[i],'RATEA')[1]
                if BranchLoadBase is not None:
                    if BranchRate == 360.0:
                        goon = True
                    else:
                        goon = False
                    if BranchLoadBase < rate and goon == True: 
                        goon = True
                    elif BranchLoadBase > rate and goon == True: 
                        goon = True
                    elif BranchLoadBase < rate and goon == False:
                        goon = False
                    elif BranchLoadBase > rate:
                        goon = True
                    if goon == True:
                        psspy.branch_chng_3(BranchFromNumber[i],BranchToNumber[i],BranchID[i],[0,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
                        island_check = islanding_buses()
                        if island_check == 0:
                            if multiple_load_flow() > 0:
                                LinePerformanceIndexList.append(300)
                                if show_case == True:
                                    print ("Load Flow Solution not Converge with Flat Start in Line Contingency Situation")
                                    print ("%i - %i, %s - %s (%s)"%(BranchFromNumber[i],BranchToNumber[i],BranchFromName[i],BranchToName[i],BranchID[i]))
                            else:
                                BranchLoadBaseConLine = np.array(psspy.abrnreal(1,1,3,1,1,'PCTRATEA')[1][0])
                                BranchLoadBaseConOTR = np.array(psspy.abrnreal(1,1,1,5,1,'PCTRATEA')[1][0])
                                BaseBusVoltageForBranchCon = np.array(psspy.abusreal(1, 1, "PU")[1][0])
                                loading_perf, voltage_perf = calculate_performance(BranchLoadBaseConLine, BranchLoadBaseConOTR, BaseBusVoltageForBranchCon, Vimax, Vimin)
                                LinePerformanceIndexList.append(loading_perf)                      
                                ReactivePIForBranchConList.append(voltage_perf)
                                if show_case == True:
                                    print_case(BranchLoadBaseConLine, BranchLoadBaseConOTR, BaseBusVoltageForBranchCon, "Line", loading_perf, voltage_perf, BranchFromNumber[i], BranchToNumber[i], BranchFromName[i], BranchToName[i], BranchID[i])
                        else:
                            LinePerformanceIndexList.append(island_check)
                            ReactivePIForBranchConList = LinePerformanceIndexList
                        psspy.branch_chng_3(BranchFromNumber[i],BranchToNumber[i],BranchID[i],[1,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
   
    psspy.bsys(7,0,[ 0.38, 400.],1,[ytim],0,[],len(regions),regions,1,[7])
    GeneratorName = psspy.agenbuschar(7, 1, 'NAME')[1][0]
    GeneratorNumber = psspy.agenbusint(7, 1, 'NUMBER')[1][0]
    RegulatedBus = psspy.agenbusint(7, 1, 'IREG')[1][0]
    GeneratorBusNumber = psspy.agenbuscount(7, 1)[1]
    burgenCount, burgenReCount = 0, 0
    #This code is created for the special situation in Bursa region. All generators in Bursa will be disconnected in N-1 security analysis.
    BursaGen = [220064, 220065, 220066]
    Line_con = np.sum(np.array(LinePerformanceIndexList))
    if fast_con == True and otr_con > 200:
        GeneratorPerformanceIndexList.append(3000.0)
    elif fast_con == True and otr_con > 100:
        GeneratorPerformanceIndexList.append(300.0)
    if fast_con == True and maj_line_con > 200:
        GeneratorPerformanceIndexList.append(3000.0)
    elif fast_con == True and maj_line_con > 100:
        GeneratorPerformanceIndexList.append(300.0)
    if fast_con == True and Line_con > 100:
        GeneratorPerformanceIndexList.append(100.0)
    if (fast_con == True and otr_con < 100 and Line_con < 100 and maj_line_con < 100) or fast_con == False:
        for i in range(GeneratorBusNumber):
            if int(str(RegulatedBus[i])[4]) <= 2:
                if search.search(GeneratorNumber[i], BursaGen) != -1:
                    if burgenCount <1:
                        for bursa in range(len(BursaGen)):
                            psspy.bsysinit(8)
                            psspy.bsyso(8,BursaGen[bursa])
                            psspy.dscn(BursaGen[bursa])
                            burgenCount += 1
                else:
                    psspy.bsysinit(8)
                    psspy.bsyso(8,GeneratorNumber[i])
                    psspy.dscn(GeneratorNumber[i])
            if int(str(RegulatedBus[i])[4]) <= 2:
                if multiple_load_flow() > 0:
                    GeneratorPerformanceIndexList.append(50)
                    if show_case == True:
                        print ("Load Flow Solution not Converge with Flat Start in Generator Contingency Situation")
                        print ("%i, %s"%(GeneratorNumber[i],GeneratorName[i]))
                else:
                    GenLoadBaseConLine = np.array(psspy.abrnreal(1,1,3,1,1,'PCTRATEA')[1][0])
                    GenLoadBaseConOTR = np.array(psspy.abrnreal(1,1,1,5,1,'PCTRATEA')[1][0])
                    BaseBusVoltageForGeneratorCon = np.array(psspy.abusreal(1, 1, "PU")[1][0])
                    loading_perf, voltage_perf = calculate_performance(GenLoadBaseConLine, GenLoadBaseConOTR, BaseBusVoltageForGeneratorCon, Vimax, Vimin)
                    GeneratorPerformanceIndexList.append(loading_perf)
                    ReactivePIGenConList.append(voltage_perf)
                    if show_case == True:
                        print_case(GenLoadBaseConLine, GenLoadBaseConOTR, BaseBusVoltageForGeneratorCon, "Generator", loading_perf, voltage_perf, GeneratorNumber[i], GeneratorNumber[i], GeneratorName[i], GeneratorName[i], '1')
                if search.search(GeneratorNumber[i], BursaGen) != -1:
                    if burgenReCount <1:
                        for bursa in range(3):
                            psspy.bsysinit(8)
                            psspy.bsyso(8,BursaGen[bursa])
                            psspy.recn(BursaGen[bursa])
                            burgenReCount += 1
                elif int(str(RegulatedBus[i])[4]) <= 2:
                    psspy.recn(GeneratorNumber[i])
    performance = base_case_load_regul + base_case_voltage + np.sum(np.array(Paralel_otr_PI_list)) + np.sum(np.array(Reactive_PI_Paralel_OTR_list)) + np.sum(np.array(LinePerformanceIndexList)) + np.sum(np.array(ReactivePIForBranchConList)) + np.sum(np.array(OTRPerformanceIndexList)) + np.sum(np.array(ReactivePIForOTRConList)) + np.sum(np.array(GeneratorPerformanceIndexList)) + np.sum(np.array(ReactivePIGenConList)) + np.sum(np.array(MajorLinePIList)) + np.sum(np.array(MajorLineReactivePIList))                    
    if show_case == True:    
        print ("BASE CASE PERFORMANCE")  
        print (base_case_load_regul, base_case_voltage)  
        print ("BRANCH OVERLOADING PERFORMANCE IN MAJOR LINE OUTAGE")
        print (MajorLinePIList)
        print ("REACTIVE POWER PERFORMANCE IN MAJOR LINE OUTAGE")
        print (MajorLineReactivePIList)
        print ("BRANCH OVERLOADING PERFORMANCE IN PARALLEL OTR CONTINGENCY")
        print (Paralel_otr_PI_list) 
        print ("REACTIVE POWER PERFORMANCE IN PARALLEL OTR CONTONGENCY")     
        print (Reactive_PI_Paralel_OTR_list)  
        print ("BRANCH OVERLOADING PERFORMANCE IN SINGLE OTR CONTINGENCY")        
        print (OTRPerformanceIndexList)
        print ("REACTIVE POWER PERFORMANCE IN SINGLE OTR CONTONGENCY")
        print (ReactivePIForOTRConList)
        print ("BRANCH OVERLOADING PERFORMANCE IN LINE CONTINGENCY")        
        print (LinePerformanceIndexList)
        print ("REACTIVE POWER PERFORMANCE IN LINE CONTONGENCY")
        print (ReactivePIForBranchConList)
        print ("BRANCH OVERLOADING PERFORMANCE IN GENERATOR CONTINGENCY")
        print (GeneratorPerformanceIndexList)
        print ("REACTIVE POWER PERFORMANCE IN GENERATOR CONTINGENCY")      
        print (ReactivePIGenConList)
        print ("-------------------------------------------------------")
        print ("POWER SYSTEM OVERALL PERFORMANCE")
        print (performance)
        print ("-------------------------------------------------------")
    return performance
#contingency_analysis(r"""20220701_1500_SN5_TR0.sav""", 2, [702], r"""C:\Users\erdidogan\Dropbox""", rate=0, tieLines = None, fast_con = False, show_case = True)
