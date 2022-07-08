#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''

MIT License
ŞAP version 3
Copyright (c) 2022 Dr. Erdi Doğan

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
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QStackedWidget, QFileDialog, QVBoxLayout
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon
import time
from contingency import contingency
from time import perf_counter
from run_nsga import Run_NSGAII

class WelcomeScreen(QDialog): 
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("welcomescreen.ui", self)
        self.continue_1.clicked.connect(self.gotoanalysis)
    def gotoanalysis(self):
        analysis = AnalysisScreen()
        widget.addWidget(analysis)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
class AnalysisScreen(QDialog):
    def __init__(self):
        super(AnalysisScreen, self).__init__()
        loadUi("analysis_screen.ui", self)
        self.N_1_analysis.clicked.connect(self.gotoN_1analysis)
        self.sc_analysis.clicked.connect(self.sc_btn)
        self.bus_splitting.clicked.connect(self.gotoBusLayout)
    def gotoN_1analysis(self):
        N_1analysis = N_1AnalysisScreen()
        widget.addWidget(N_1analysis)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def sc_btn(self):
        SCanalysis = SCAnalysisScreen()
        widget.addWidget(SCanalysis)
        widget.setCurrentIndex(widget.currentIndex() + 1)
    def gotoBusLayout(self):
        bus_layout = BusLayoutOptScreen()
        widget.addWidget(bus_layout)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
class N_1AnalysisScreen(QDialog): 
    def __init__(self):
        super(N_1AnalysisScreen, self).__init__()
        self.filename_sav = ('',0)
        self.filename_iec = ('',0)
        self.check_box_control = 0
        loadUi("N_1analysis_screen.ui", self)
        self.continuetostart.setEnabled(False)
        self.pushButtonSav.clicked.connect(self.open_dialog_box_sav)
        self.pushButtonIec.clicked.connect(self.open_dialog_box_iec)
        self.checkBox_700.stateChanged.connect(self.btnstate)
        self.checkBox_702.stateChanged.connect(self.btnstate)
        self.checkBox_704.stateChanged.connect(self.btnstate)
        self.checkBox_705.stateChanged.connect(self.btnstate)
        self.checkBox_706.stateChanged.connect(self.btnstate)
        self.continuetostart.clicked.connect(self.N_1_btn)
        self.back1.clicked.connect(self.gotoanalysis_screen)
    def btnstate(self):
        self.checkbox_hepsi = self.checkBox_700.isChecked()
        self.checkbox_bursa = self.checkBox_702.isChecked()
        self.checkbox_istanbul = self.checkBox_704.isChecked()
        self.checkbox_sakarya = self.checkBox_705.isChecked()
        self.checkbox_kutahya = self.checkBox_706.isChecked()
        self.region_list = []
        self.activate_button = False
        if bool(self.checkbox_hepsi):
            self.region_list.append(702)
            self.region_list.append(704)
            self.region_list.append(705)
            self.region_list.append(706)
            self.activate_button = True
        if bool(self.checkbox_bursa):
            self.region_list.append(702)
            self.activate_button = True
        if bool(self.checkbox_istanbul):
            self.region_list.append(704)
            self.activate_button = True
        if bool(self.checkbox_sakarya):
            self.region_list.append(705)
            self.activate_button = True
        if bool(self.checkbox_kutahya):
            self.region_list.append(706)
            self.activate_button = True
        if self.activate_button == True:
            self.file_inform_text_rcb.repaint()
            self.file_inform_text_rcb.setText("")
            if bool(self.filename_sav[0]):
                self.fileLoadSit.repaint()
                self.fileLoadSit.setText("")
                self.continuetostart.setEnabled(True)
                self.continuetostart.setMouseTracking(True)
                self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                                    "background-color: rgb(158, 0, 0);\n"
                                    "font: 8pt \"MS Shell Dlg 2\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "font: 12pt \"MS Shell Dlg 2\";")
            else:
                self.continuetostart.setEnabled(False)
                self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                                    "background-color: rgb(220, 220, 220);\n"
                                    "font: 8pt \"MS Shell Dlg 2\";\n"
                                    "color: rgb(100, 100, 100);\n"
                                    "font: 12pt \"MS Shell Dlg 2\";")
                self.fileLoadSit.repaint()
                self.fileLoadSit.setText("<font color=#aa0000>Lütfen sav dosyasını yükleyiniz</font>")
        else:
            self.continuetostart.setEnabled(False)
            self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                                    "background-color: rgb(220, 220, 220);\n"
                                    "font: 8pt \"MS Shell Dlg 2\";\n"
                                    "color: rgb(100, 100, 100);\n"
                                    "font: 12pt \"MS Shell Dlg 2\";")
            self.file_inform_text_rcb.repaint()
            self.file_inform_text_rcb.setText("<font color=#aa0000>Lütfen en az bir bölge seçiniz</font>")
    def open_dialog_box_sav(self):
        self.filename_sav = QFileDialog.getOpenFileName()
        self.btnstate()
        return self.filename_sav
    def open_dialog_box_iec(self):
        self.filename_iec = QFileDialog.getOpenFileName()
        return self.filename_iec
    def goto_set_inform_tostart(self):
        self.inform_text.repaint()
        self.inform_text.setText("N-1 analizi başlamıştır, lütfen analizin bitmesini bekleyiniz")
    def do_action(self):
        # setting for loop to set value of progress bar
        for i in range(101):

            # slowing down the loop
            time.sleep(0.05)
            # setting value to progress bar
            self.sc_pbar.setValue(i)
    def gotoanalysis_screen(self):
        analysis_screen = AnalysisScreen()
        widget.addWidget(analysis_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
        
    def N_1_btn(self):
        self.ac_dc = str(self.ac_dc.currentText())
        self.lc = str(self.load_level.currentText())
        if str(self.lc) == "Evet":
            self.load_change=True
        else:
            self.load_change=False
        
        bc = str(self.base_case.currentText())
        if bc == "Evet":
            self.show_case_base=True
        else:
            self.show_case_base=False
        self.prcnt_bound = str(self.percent_bound.currentText())
        rt = str(self.rates.currentText())
        if rt == "Rate-A (Kış)":
            self.rate = "RATEA"
        elif rt == "Rate-B (Yaz)":
            self.rate = "RATEB"
        elif rt == "Rate-C (Bahar)":
            self.rate = "RATEC"
        self.do_action()
        f = open(r"n1_results\last_file_order_n1.txt",'r')
        seq = f.read()
        f.close()
        new_seq = int(seq) + 1
        f = open(r"n1_results\last_file_order_n1.txt",'w+')
        f.write(str(new_seq))
        f.close()
        sys.stdout = open(r"n1_results\n1_result"+str(new_seq)+".txt", "w")
        con = contingency(2, self.region_list, self.filename_sav[0], line_rate = self.rate, load_change=self.load_change)
        if self.ac_dc == "AC":
            con.N_1_analysis(10, int(self.prcnt_bound), show_case_base = self.show_case_base, show_case_con = True)
        else:
            con.dc_N_1_analysis()    
        if bool(self.filename_iec[0]):
            con.short_circuit(show_case_sc=True)
        sys.stdout.close()
        
        result = Result_Window("n1",str(new_seq))
        widget.addWidget(result)
        widget.setCurrentIndex(widget.currentIndex() + 1)
                
    
        
class SCAnalysisScreen(QDialog): 
    def __init__(self):
        super(SCAnalysisScreen, self).__init__()
        self.filename_sav, self.filename_iec = ('',0), ('',0)
        self.check_box_control = 0
        loadUi(r"sc_screen.ui", self)
        self.continuetostart.setEnabled(False)
        self.pushButtonSav.clicked.connect(self.open_dialog_box_sav)
        self.pushButtonIec.clicked.connect(self.open_dialog_box_iec)
        self.checkBox_702.stateChanged.connect(self.btnstate)
        self.checkBox_704.stateChanged.connect(self.btnstate)
        self.checkBox_705.stateChanged.connect(self.btnstate)
        self.checkBox_706.stateChanged.connect(self.btnstate)
        self.continuetostart.clicked.connect(self.sc_btn)
        self.back1.clicked.connect(self.gotoanalysis_screen)
    def btnstate(self):
        self.checkbox_bursa = self.checkBox_702.isChecked()
        self.checkbox_istanbul = self.checkBox_704.isChecked()
        self.checkbox_sakarya = self.checkBox_705.isChecked()
        self.checkbox_kutahya = self.checkBox_706.isChecked()
        self.region_list = []
        self.activate_button = False
        if bool(self.checkbox_bursa):
            self.region_list.append(702)
            self.activate_button = True
        if bool(self.checkbox_istanbul):
            self.region_list.append(704)
            self.activate_button = True
        if bool(self.checkbox_sakarya):
            self.region_list.append(705)
            self.activate_button = True
        if bool(self.checkbox_kutahya):
            self.region_list.append(706)
            self.activate_button = True
        if self.activate_button == True:
            self.file_inform_text_rcb.repaint()
            self.file_inform_text_rcb.setText("")
            if bool(self.filename_iec[0]) and bool(self.filename_sav[0]):
                self.file_inform_text_sc.repaint()
                self.file_inform_text_sc.setText("")
                self.continuetostart.setEnabled(True)
                self.continuetostart.setMouseTracking(True)
                self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                                    "background-color: rgb(158, 0, 0);\n"
                                    "font: 8pt \"MS Shell Dlg 2\";\n"
                                    "color: rgb(255, 255, 255);\n"
                                    "font: 12pt \"MS Shell Dlg 2\";")
            else:
                self.continuetostart.setEnabled(False)
                self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                                    "background-color: rgb(220, 220, 220);\n"
                                    "font: 8pt \"MS Shell Dlg 2\";\n"
                                    "color: rgb(100, 100, 100);\n"
                                    "font: 12pt \"MS Shell Dlg 2\";")
                self.file_inform_text_sc.repaint()
                self.file_inform_text_sc.setText("<font color=#aa0000>Lütfen dosyaları yükleyiniz</font>")
        else:
            self.continuetostart.setEnabled(False)
            self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                                    "background-color: rgb(220, 220, 220);\n"
                                    "font: 8pt \"MS Shell Dlg 2\";\n"
                                    "color: rgb(100, 100, 100);\n"
                                    "font: 12pt \"MS Shell Dlg 2\";")
            self.file_inform_text_rcb.repaint()
            self.file_inform_text_rcb.setText("<font color=#aa0000>Lütfen en az bir bölge seçiniz</font>")
            
    def open_dialog_box_sav(self):
        self.filename_sav = QFileDialog.getOpenFileName()
        self.btnstate()
        return self.filename_sav
    def open_dialog_box_iec(self):
        self.filename_iec = QFileDialog.getOpenFileName()
        self.btnstate()
        return self.filename_iec
    def goto_set_inform_tostart(self):
        self.inform_text.repaint()
        self.inform_text.setText(" Kısa devre analizi başlamıştır, lütfen analizin bitmesini bekleyiniz")
    def do_action(self):
        # setting for loop to set value of progress bar
        for i in range(101):
            # slowing down the loop
            time.sleep(0.05)
            # setting value to progress bar
            self.sc_pbar.setValue(i)
    def gotoanalysis_screen(self):
        analysis_screen = AnalysisScreen()
        widget.addWidget(analysis_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)
       
    def sc_btn(self):           
        self.do_action()
        f = open(r"sc_results\last_file_order_sc.txt",'r')
        seq = f.read()
        f.close()
        new_seq = int(seq) + 1
        f = open(r"sc_results\last_file_order_sc.txt",'w+')
        f.write(str(new_seq))
        f.close()
        sys.stdout = open(r"sc_results\sc_result"+str(new_seq)+".txt", "w")
        con = contingency(2, self.region_list, self.filename_sav[0], line_rate = "RATEA", load_change=False)
        con.short_circuit(show_case_sc=True)
        sys.stdout.close()
        result = Result_Window("sc", str(new_seq))
        widget.addWidget(result)
        widget.setCurrentIndex(widget.currentIndex() + 1)
class BusLayoutOptScreen(QDialog): 
    def __init__(self):
        super(BusLayoutOptScreen, self).__init__()
        self.manuel_definition = []
        self.filename_sav = ('',0)
        self.filename_iec = ('',0)
        self.filename_json = ('',0)
        loadUi("Bus_Layout_Optimization_Screen.ui", self)
        self.continuetostart.setEnabled(False)
        self.pushButtonSav.clicked.connect(self.open_dialog_box_sav)
        self.pushButtonIec.clicked.connect(self.open_dialog_box_iec)
        self.pushButtonJson.clicked.connect(self.open_dialog_box_json)
        self.checkBox_702.stateChanged.connect(self.btnstate)
        self.checkBox_704.stateChanged.connect(self.btnstate)
        self.checkBox_705.stateChanged.connect(self.btnstate)
        self.checkBox_706.stateChanged.connect(self.btnstate)
        self.continuetostart.clicked.connect(self.bus_layout)
        self.back1.clicked.connect(self.gotoanalysis_screen)
        self.ManuelChoose.currentTextChanged.connect(self.goto_set_manuel_definition_text)
        self.IstBus_1.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_1))
        self.IstBus_2.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_2))
        self.IstBus_3.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_3))
        self.IstBus_4.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_4))
        self.IstBus_5.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_5))
        self.IstBus_6.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_6))
        self.IstBus_7.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_7))
        self.IstBus_8.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_8))
        self.IstBus_9.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_9))
        self.IstBus_10.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_10))
        self.IstBus_11.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_11))
        self.IstBus_12.stateChanged.connect(lambda:self.manuelDefinition(self.IstBus_12))
        self.BursaBus_1.stateChanged.connect(lambda:self.manuelDefinition(self.BursaBus_1))
        self.BursaBus_2.stateChanged.connect(lambda:self.manuelDefinition(self.BursaBus_2))
        self.BursaBus_3.stateChanged.connect(lambda:self.manuelDefinition(self.BursaBus_3))
        self.BursaBus_4.stateChanged.connect(lambda:self.manuelDefinition(self.BursaBus_4))
        self.BursaBus_5.stateChanged.connect(lambda:self.manuelDefinition(self.BursaBus_5))
        self.compulsoryRegion = [False,'','']
    def activateButton(self):
        self.continuetostart.setEnabled(True)
        self.continuetostart.setMouseTracking(True)
        self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                            "background-color: rgb(158, 0, 0);\n"
                            "font: 8pt \"MS Shell Dlg 2\";\n"
                            "color: rgb(255, 255, 255);\n"
                            "font: 12pt \"MS Shell Dlg 2\";")
    def deActivateButton(self):
        self.continuetostart.setEnabled(False)
        self.continuetostart.setStyleSheet("border-radius: 20px;\n"
                            "background-color: rgb(220, 220, 220);\n"
                            "font: 8pt \"MS Shell Dlg 2\";\n"
                            "color: rgb(100, 100, 100);\n"
                            "font: 12pt \"MS Shell Dlg 2\";")
        self.fileLoadSit.repaint()
    def btnstate(self):
        #Start button will be activated if .sav and .iec file are loaded, one region is chosen at least.
        #Furthermore, if user selects buses manually, the region related to the chosen buses should be selected
        #Compulsory region check is implemented for this reason.
        self.checkbox_bursa = self.checkBox_702.isChecked()
        self.checkbox_istanbul = self.checkBox_704.isChecked()
        self.checkbox_sakarya = self.checkBox_705.isChecked()
        self.checkbox_kutahya = self.checkBox_706.isChecked()
        self.region_list = []
        self.activate_button = False
        if bool(self.checkbox_bursa):
            self.region_list.append(702)
            self.activate_button = True
        if bool(self.checkbox_istanbul):
            self.region_list.append(704)
            self.activate_button = True
        if bool(self.checkbox_sakarya):
            self.region_list.append(705)
            self.activate_button = True
        if bool(self.checkbox_kutahya):
            self.region_list.append(706)
            self.activate_button = True
        if self.activate_button == True:
            if bool(self.compulsoryRegion[0]):
                if  self.compulsoryRegion[1] == "istanbul":
                    if bool(self.checkBox_704.isChecked()) == False: 
                        self.file_inform_text_rcb.repaint()
                        self.file_inform_text_rcb.setText(self.compulsoryRegion[2])
                        self.deActivateButton()
                    else:
                        self.activateButton()
                        self.file_inform_text_rcb.repaint()
                        self.file_inform_text_rcb.setText("<font color=#aa0000>""</font>")
                elif self.compulsoryRegion[1] == "bursa":
                    if bool(self.checkBox_702.isChecked()) == False: 
                        self.file_inform_text_rcb.repaint()
                        self.file_inform_text_rcb.setText(self.compulsoryRegion[2])
                        self.deActivateButton()
                    else:
                        self.activateButton()
                        self.file_inform_text_rcb.repaint()
                        self.file_inform_text_rcb.setText("<font color=#aa0000>""</font>")
            else:
                self.file_inform_text_rcb.repaint()
                self.file_inform_text_rcb.setText("")
                if bool(self.filename_iec[0]) and bool(self.filename_sav[0]):
                    self.fileLoadSit.repaint()
                    self.fileLoadSit.setText("")
                    self.activateButton()
                    self.fileLoadSit.repaint()
                    self.fileLoadSit.setText("<font color=#aa0000>""</font>")
                    self.file_inform_text_rcb.repaint()
                    self.file_inform_text_rcb.setText("<font color=#aa0000>""</font>")
                else:
                    self.deActivateButton()
                    self.fileLoadSit.repaint()
                    self.fileLoadSit.setText("<font color=#aa0000>Lütfen dosyaları yükleyiniz</font>")
        else:
            self.deActivateButton()
            self.file_inform_text_rcb.repaint()
            self.file_inform_text_rcb.setText("<font color=#aa0000>Lütfen en az bir bölge seçiniz</font>")
            
    def open_dialog_box_sav(self):
        self.filename_sav = QFileDialog.getOpenFileName()
        self.btnstate()
        return self.filename_sav
    def open_dialog_box_iec(self):
        self.filename_iec = QFileDialog.getOpenFileName()
        self.btnstate()
        return self.filename_iec
    def open_dialog_box_json(self):
        self.filename_json = QFileDialog.getOpenFileName()
        return self.filename_json
    def goto_set_inform_tostart(self):
        self.inform_text.repaint()
        self.inform_text.setText("<font color=#aa0000>Bara dağılımı optimizasyonu başlamıştır, lütfen analizin bitmesini bekleyiniz</font>")
    def goto_set_manuel_definition_text(self):
        self.textChooseBus.repaint()
        if self.ManuelChoose.currentText() == "Evet":
            self.inform_text.setText("")
            if bool(self.manuel_definition):
                self.textChooseBus.setText("")
            else:
                self.textChooseBus.setText("Lütfen en az bir bara seçiniz")
        else:
            self.textChooseBus.setText("")
            
    def gotoanalysis_screen(self):
        analysis_screen = AnalysisScreen()
        widget.addWidget(analysis_screen)
        widget.setCurrentIndex(widget.currentIndex() + 1)    
    def manuelDefinition(self, bus):
        ist = [210021,210221,210921,211021,211221,211521,211621,211821,214321,214821,216721,214221]
        bursa = [220021,221821,228721,228621,227221]
        if self.ManuelChoose.currentText() == "Evet":  
            self.inform_text.setText("")
        else:
            self.inform_text.setText("Lütfen 'Optimize edilecek baraları kendin seçmek ister misin?' bölümünde Evet seçiniz!")
        if bool(bus.isChecked()):
            self.textChooseBus.setText("")
            self.manuel_definition.append(int(bus.text()[:6]+bus.text()[:5]+str(2)))
            if int(bus.text()[:6]) in ist:
                if bool(self.checkBox_704.isChecked())==False:
                    self.deActivateButton()
                    self.file_inform_text_rcb.repaint()
                    self.file_inform_text_rcb.setText("<font color=#aa0000>Lütfen istanbul bölgesini seçiniz</font>")
                    self.compulsoryRegion = [True,"istanbul","<font color=#aa0000>Lütfen istanbul bölgesini seçiniz</font>"]
                else:
                    self.file_inform_text_rcb.repaint()
                    self.file_inform_text_rcb.setText("<font color=#aa0000>""</font>")
            if int(bus.text()[:6]) in bursa:
                if bool(self.checkBox_702.isChecked())==False:
                    self.deActivateButton()
                    self.file_inform_text_rcb.repaint()
                    self.file_inform_text_rcb.setText("<font color=#aa0000>Lütfen bursa bölgesini seçiniz</font>")
                    self.compulsoryRegion = [True,"bursa","<font color=#aa0000>Lütfen bursa bölgesini seçiniz</font>"]
                else:
                    self.file_inform_text_rcb.repaint()
                    self.file_inform_text_rcb.setText("<font color=#aa0000>""</font>")
        else:
            self.inform_text.setText("")
            self.file_inform_text_rcb.setText("<font color=#aa0000>""</font>")
            self.manuel_definition.remove(int(bus.text()[:6]+bus.text()[:5]+str(2)))
    def bus_layout(self):
        pop_size = int(self.PopSize.currentText())
        iter_size = int(self.IterSize.currentText())
        cross_rate = float(self.CrossRate.currentText())
        mut_rate = float(self.MutRate.currentText())
        con_rate = int(self.ConRate.currentText())
        tr_include = str(self.Tr.currentText())
        if tr_include == "Evet":
            tr_include = True
        otr_include = str(self.Otr.currentText())
        if otr_include == "Evet":
            otr_include = True
        manuel_choose = self.ManuelChoose.currentText()
        if manuel_choose == 'Evet' and len(self.manuel_definition) == 0:
            self.file_inform_text_rcb.setText("<font color=#aa0000>Bara seçmeden analize başlayamazsınız. Sağ tarafta verilen bara listesinden en az bir bara seçiniz.</font>")
        else:
            self.file_inform_text_rcb.setText("")
            self.goto_set_inform_tostart()
            ytim = 2
            dfax_name = 'KBA'
            if self.net_Reduction.currentText() == "Evet":
                network_Reduction = True
            else:
                network_Reduction = False
            nsga = Run_NSGAII(self.filename_sav[0], self.region_list, ytim, dfax_name, pop_size, cross_rate, mut_rate, self.manuel_definition,rate=con_rate,networkReduction=network_Reduction, tr_include = True, atr_include = True)
            if bool(self.filename_json[0]):
                bcs = self.bcSolution.currentText()
                nsga.run_single(path=self.filename_json[0],bcs=bcs, external_file=True)
                nsga.show_result(path=self.filename_json[0])
                result = Result_Window("bl",str(0))
                widget.addWidget(result)
                widget.setCurrentIndex(widget.currentIndex() + 1)
            else:
                sys.stdout = open(r"BusLayoutResults\Results\console"+".txt", "w")
                func = []
                t0 = perf_counter() 
                for i in range(iter_size):
                    if i == 1:
                        tfirst = perf_counter()
                    self.progressBar.setValue(i/(iter_size/100))
                    func.append(nsga.run(i))
                    if i == 1:
                        tlast = perf_counter()
                        tcycle = tlast-tfirst
                    if i == 0:
                        self.remainingTime.repaint()
                        self.remainingTime.setText(f'Analiz süresi hesaplanıyor!') 
                    else:
                        remaining_time = round(((tcycle*(iter_size-i))/3600),2)
                        self.remainingTime.repaint()
                        self.remainingTime.setText(f'Analizin bitmesi için kalan süre:{remaining_time} hour')    
                t1 = perf_counter()
                print("Analysis Time:%.2f"%(t1-t0))
                f = open(r"BusLayoutResults\Results\last_file_order_bl.txt",'r')
                seq = f.read()
                f.close() 
                new_seq = int(seq) + 1
                f = open(r"BusLayoutResults\Results\last_file_order_bl.txt",'w')
                f.write(str(new_seq))
                f.close()        
                nsga.save_data(step_number=new_seq)
                nsga.run_single(step_number=new_seq)
                nsga.show_result(step_number=new_seq)
                sys.stdout.close()
                result = Result_Window("bl",str(new_seq))
                widget.addWidget(result)
                widget.setCurrentIndex(widget.currentIndex() + 1) 
        
class Result_Window(QtWidgets.QMainWindow):
    def __init__(self, contingency, sequence):
        self.contingency, self.sequence = contingency, sequence
        super(Result_Window, self).__init__()
        self.button = QtWidgets.QPushButton("Geri Dön", self)
        self.label = QtWidgets.QLabel("console output")
        self.textedit = QtWidgets.QTextEdit(readOnly=True)
        self.textedit.setStyleSheet ('''QTextEdit {font: 10pt "Consolas";}''')   
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        layout.addWidget(self.textedit)
        self.setCentralWidget(widget)
        self.show_result()
        self.button.clicked.connect(self.goto_analysis)

    def show_result(self):
        if self.contingency == "n1":
            f = open(r"n1_results\n1_result"+self.sequence+".txt",'r')
            data = f.read()
            self.textedit.setText(data)
            f.close()
        elif self.contingency == "sc":
            f = open(r"sc_results\sc_result"+self.sequence+".txt",'r')
            data = f.read()
            self.textedit.setText(data)
            f.close()
        elif self.contingency == "bl":
            if self.sequence == "0":
                f = open(r"BusLayoutResults\Results\layout_result_from_json.txt",'r')
                data = f.read()
                self.textedit.setText(data)
            else:
                f = open(r"BusLayoutResults\Results\layout_result"+self.sequence+".txt",'r')
                data = f.read()
                self.textedit.setText(data)
            
       
    def goto_analysis(self):
        analysis = AnalysisScreen()
        widget.addWidget(analysis)
        widget.setCurrentIndex(widget.currentIndex() + 1)

if __name__ == "__main__":
    #setup
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("teias.png"))
    welcome = WelcomeScreen()
    widget = QStackedWidget()
    widget.addWidget(welcome)
    widget.setWindowTitle("Şebeke Analiz Programı")
    widget.adjustSize()
    widget.show()  
    sys.exit(app.exec_())

