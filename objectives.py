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
import ConAn
import SC_Weight 
import LoadChange
import Transportv3
class Objectives():
    def __init__(self,file, regions,rate,min_load_con=False):
        r'''
        this class responsible for evaluating objectives
        :param str file:
            file is the sav file path added by user 
        :param list regions:
            regions of network chosen by user in order to optimize
        :param int rate:
            rate is permissible loading level 
        r'''
        txt = file.split("/")
        self.sav_ismi = txt[-1][:-4]
        st = ''
        del txt[-1]
        for i in txt:
            st += str(i)+"/"
        self.file_directory = st[:-1]
        self.regions = regions
        self.min_load_con = min_load_con
        self.rate = rate
    #First function to optimize
    def short_circuit(self, sol, tieLines=None):
        r'''
        this class responsible for evaluating the short-circuit performance of the network
        :param int sol:
            sol is the result of the power flow equations. If sol is 0, it means that convergence met tolerances 
        :param object tieLines:
            tieLines is used when the reduced version of network is created
        r'''
        if sol > 0:
            value = 44444444444444444444.0
        else:
            SC = SC_Weight.ShortCircuit(self.sav_ismi, self.file_directory, tieLines=tieLines, location=self.regions[0])
            value = SC.shortcircuit()
        return value
    #Second function to optimize
    def Contingency(self, sol, tieLines=None):
        r'''
        this class responsible for evaluating the short-circuit performance of the network
        :param int sol:
            sol is the result of the power flow equations. If sol is 0, it means that convergence met tolerances 
        :param object tieLines:
            tieLines is used when the reduced version of network is created
        r'''
        #Open file
        if sol > 0:
            TotalCost = 44444444444444444444.0
        else:
            if self.regions == [704] and self.min_load_con == True:
                LoadChange.min_load_col_sid(self.sav_ismi, self.file_directory)
                MinLoadCost = ConAn.contingency_analysis(self.sav_ismi, 2, self.regions, self.file_directory, rate=self.rate, fast_con = True, show_case=False)
                LoadChange.max_load_col_sid(self.sav_ismi, self.file_directory)
            else:
                MinLoadCost = 0
            TotalCost = ConAn.contingency_analysis(self.sav_ismi, 2, self.regions, self.file_directory, rate=self.rate, tieLines=tieLines, fast_con = False, show_case=False) + MinLoadCost
        return TotalCost
    