#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

MIT License

Copyright (c) 2022 Dr. Erdi DO�AN

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
import os, sys
import requests
sys.path.append(r"C:\Program Files\PTI\PSSE35\35.2\PSSPY37")
os.environ['PATH'] = r"C:\Program Files\PTI\PSSE35\35.2\PSSBIN;" + os.environ['PATH']
import psse35
psse35.set_minor(2)
import psspy
_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()
import numpy as np
from problem import Problem
from evolution import Evolution
from objectives import Objectives
import Transportv3
from tools import _save_step
from tools import _determine_best_sol
class Run_NSGAII(Objectives):
    def __init__(self, file_name, regions, ytim, dfax_name, pop_size, cross_rate, mut_rate, manuel_definition, rate=30, networkReduction=None, tr_include = True, atr_include = True):
        print("Non Dominated Sorted Genetic Algorithm-II started to investigate the best solutions")
        self.ytim = ytim
        self.tr_include = tr_include
        self.atr_include = atr_include
        self.manuel_definition = manuel_definition
        self.dfax_name = dfax_name
        self.pop_size = pop_size
        self.cross_rate = cross_rate
        self.mut_rate = mut_rate
        self.file_name = file_name
        self.regions = regions
        self.rate = rate
        self.obj = Objectives(file_name, regions, rate=rate, min_load_con=False)
        if 702 in regions:
            Transportv3.prepare_busbars(self.obj.sav_ismi, ytim, regions, self.obj.file_directory)
        self.num_of_variables, self.each_of_bus_len, self.start_position, self.buses_included_zil_and_enough_line = self.bus_structure()
        if bool(networkReduction):  
            netReduction = Transportv3.networkReduction(ytim, regions, self.obj.file_directory, self.obj.sav_ismi)
            tieLines = netReduction.runNetReduction()
        else:
            tieLines = None
        self.problem = Problem(num_of_variables=self.num_of_variables, objectives=[self.obj.short_circuit, self.obj.Contingency], variables_range=[(1, 2)], tieLines=tieLines, same_range=True, expand=False)
        self.evo = Evolution(self.problem, self.start_position, self.each_of_bus_len, self.buses_included_zil_and_enough_line, self.obj.sav_ismi, self.ytim, self.regions, self.dfax_name, self.obj.file_directory, self.tr_include, self.atr_include, self.manuel_definition, num_of_individuals=self.pop_size, crossover_param=self.cross_rate, mutation_param=self.mut_rate)

    def bus_structure(self):
        buses_included_zil_and_enough_line= Transportv3.bus_selection_to_split(self.obj.sav_ismi, self.ytim, self.regions, self.obj.file_directory, manuel_definition=self.manuel_definition)
        if self.regions[0] == 705:
            #remove adapazari and bolucek from the list
            buses_included_zil_and_enough_line.remove(210321210322)
            buses_included_zil_and_enough_line.remove(230021230022)
        subs_buses_to_split = [int(str(bus)[:4]) for bus in buses_included_zil_and_enough_line]
        #Label correction
        psspy.bsys(7,0,[ 0.38, 400.],1,[self.ytim],0,[],len(self.regions),self.regions,1,[7])
        GeneratorName = psspy.agenbuschar(7, 1, 'NAME')[1][0]
        GeneratorNumber = psspy.agenbusint(7, 1, 'NUMBER')[1][0]
        RegulatedBus = psspy.agenbusint(7, 1, 'IREG')[1][0]
        GeneratorBusNumber = psspy.agenbuscount(7, 1)[1]
        for i in range(GeneratorBusNumber):
            if int(str(RegulatedBus[i])[:4]) in subs_buses_to_split:                
                err, string = psspy.xfrnam(int(str(RegulatedBus[i])[:4]+"21"), GeneratorNumber[i], r"""1""")
                if err == 0:
                    arg = string.find(":")
                    if arg == 3:
                        psspy.two_winding_chng_6(int(str(RegulatedBus[i])[:4]+'21'),
                        GeneratorNumber[i],r"""1""",
                        [_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],
                        [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],
                        [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],
                        string[:3]+"9"+string[3:],_s)
                elif err == 2:
                    err, string = psspy.xfrnam(int(str(RegulatedBus[i])[:4]+"22"), GeneratorNumber[i], r"""1""")
                    if err == 0:
                        arg = string.find(":")
                        if arg == 3:
                            psspy.two_winding_chng_6(int(str(RegulatedBus[i])[:4]+'22'),
                            GeneratorNumber[i],r"""1""",
                            [_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i,_i],
                            [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],
                            [_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f],
                            string[:3]+"9"+string[3:],_s)
        psspy.save(self.obj.file_directory+'\\'+self.obj.sav_ismi)
        fr_to_nmb_selected_buses, self.name_dict, current_number_of_name = Transportv3.branches_in_slctd_bus(buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include = self.atr_include)
        ind = Transportv3.individual_structure(self.name_dict)
        start_pos = Transportv3.initial_position(buses_included_zil_and_enough_line, fr_to_nmb_selected_buses, ind, current_number_of_name)
        zil_control_for_start_pos = [psspy.brnint(int(str(buses)[:6]),int(str(buses)[6:]),r'''1''','STATUS')[1] for buses in buses_included_zil_and_enough_line]
        start_pos = [np.ones((len(start_pos[i])), dtype=int).tolist() if zil_control_for_start_pos[i] == 1 else start_pos[i] for i in range(len(zil_control_for_start_pos))]
        each_of_bus_len = [len(bus) for bus in start_pos]
        start_pos = [start_pos[i][j] for i in range(len(start_pos)) for j in range(len(start_pos[i]))]
        num_of_var = len(start_pos)
        return num_of_var, each_of_bus_len, start_pos, buses_included_zil_and_enough_line
    def run(self, current_iteration):
        out = [i.objectives for i in self.evo.evolve(current_iteration)]
        return out
    def save_data(self, step_number=1):
        historical = dict(best_cost_lists=None, best_position_lists=None, list_epoch_time=None, all_position_list=None, all_cost_list=None)
        historical["best_cost_lists"] = self.evo.best_cost_front_list_each_epoch
        historical["best_position_lists"] = self.evo.best_pos_front_list_each_epoch
        historical["list_epoch_time"] = self.evo.epoch_time
        historical["all_position_list"] = self.evo.all_population_list
        historical["all_cost_list"] = self.evo.all_cost_list
        _save_step(step_number, historical, self.regions)
        
    def run_single(self, step_number=1, bcs = '1', path=None, external_file = False):

        if bool(external_file):
            if bool(path):
                txt = path.split("/")
                json_name = txt[-1]
                st = ''
                del txt[-1]
                for i in txt:
                    st += str(i)+"/"
                folder_name = st[:-1]
            else:
                print(r'Please provide .json file path into run_single function.')
                raise Exception(r'Please provide .json file path into run_single function.')
        else:
            folder_name = r'BusLayoutResults\NSGA-II-' + str(self.regions)
            json_name = f'/{step_number}-' + str(self.regions) + '.json'
        position, objectives = _determine_best_sol(folder_name, json_name, bcs = bcs, verbose=False)
        self.individual = self.problem.generate_individual()
        self.individual.features = position
        self.individual.objectives = objectives
        if np.sum(np.array(self.each_of_bus_len)) != len(position):
            print (r'Sav dosyasında bulunan fider sayısı ile json dosyasından çekilen optimal bara dağılımı fider sayısı eşit değil!')
            raise ValueError(r'Sav dosyasında bulunan fider sayısı ile json dosyasından çekilen optimal bara dağılımı fider sayısı eşit değil!')
        turn_to_bus_format_pre = self.evo.utils.turn_bus_structure(self.individual, self.each_of_bus_len)
        self.turn_to_bus_format = Transportv3.position_control(self.buses_included_zil_and_enough_line,turn_to_bus_format_pre, tr_include=self.tr_include, atr_include=self.atr_include)
        #implement position into .sav file
        _ = Transportv3.move_branch(self.turn_to_bus_format, self.buses_included_zil_and_enough_line, tr_include = self.tr_include, atr_include=self.atr_include)
        psspy.save(self.obj.file_directory+'\\'+self.obj.sav_ismi)
        psspy.progress_output(6,"",[0,0])
        psspy.fdns([0,1,0,1,1,1,0,0])
    def show_result(self, step_number=1, path=False):
        sorted_name_dict = [dict(sorted(name_dictionaries.items())) for name_dictionaries in self.name_dict]
        #store related feeder position in substations
        self.bus_name_list = []
        for bus in self.buses_included_zil_and_enough_line:
            psspy.bsysinit(5)
            psspy.bsyso(5,int(str(bus)[:6]))
            ierr, bus_name = psspy.abuschar(5,1,'NAME')
            if ierr == 0:
                self.bus_name_list.append(bus_name[0][0])
            else:
                print("Bara ismi eklenemedi!")
        
        self.bus1_list, self.bus2_list = [], []
        feeder_name = [[value for _, value in bus.items()] for bus in sorted_name_dict]
        for i in range(len(self.turn_to_bus_format)):
            bus1, bus2 = [], []
            for j in range(len(self.turn_to_bus_format[i])):
                if self.turn_to_bus_format[i][j] == 1:
                    bus1.append(feeder_name[i][j])
                else:
                    bus2.append(feeder_name[i][j])
            self.bus1_list.append(bus1)
            self.bus2_list.append(bus2)
        if bool(path):
            f = open(r"BusLayoutResults\Results\layout_result_from_json.txt",'w')
        else:
            f = open(r"BusLayoutResults\Results\layout_result"+str(step_number)+".txt",'w')
        f.write("Optimal bara düzeni analizin yapıldığı dosyaya kaydedilmiştir.\
            \nLütfen ilgili sav. dosyasında yine ŞAP programı üzerinden N-1 ve kısa devre etüdü yapınız.\n")
        f.write("Bara Düzeni Yapılan Bolge (owner):\n")
        f.write(str(self.regions))
        f.write("\nBara Düzeni Yapılan TM Sayısı:\n")
        f.write(str(len(self.bus_name_list)))
        f.write("\nBara Düzeni Yapılan TM Listesi:\n")
        f.write(str(self.bus_name_list)+"\n")
        f.write("--------------------------------------------------\n")
        f.write("Bara Düzeni Yapılan TM'lerde fider dağılımı:\n")
        f.write("--------------------------------------------------\n")
        for i in range(len(self.bus_name_list)):
            f.write(self.bus_name_list[i]+"\n")
            f.write("--------------------------\n")
            f.write("Bara-1:\n")
            f.write("-------\n")
            for j in range(len(self.bus1_list[i])):
                f.write(self.bus1_list[i][j]+"\n")
            f.write("\nBara-2:\n")
            f.write("-------\n")
            for j in range(len(self.bus2_list[i])):
                f.write(self.bus2_list[i][j]+"\n")
            f.write("--------------------------\n")
            f.write("\n")
        f.close()        
