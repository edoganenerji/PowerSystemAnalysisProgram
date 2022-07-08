'''
Created on 9 May 2021

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
_i=psspy.getdefaultint()
_f=psspy.getdefaultreal()
_s=psspy.getdefaultchar()
psspy.psseinit(150000)
KBA, istanbul, bursa, sakarya, kutahya = 2, 704, 702, 705, 706

genbuslst = [213261,224361,225261,225961,226061,226661,226662,227661,311062,311064,
            311163,311265,311362,311661,311761,311961,312363,312661,313361,313461,
            313861,314061,314361,314362,314461,314561,314562,314661,314662,314761,
            314861,314862,315061,315161,315661,315861,316161,316361,316461,316462,
            317061,317062,317161,317361,317561,317661,317761,318861,318961,319561,
            320167,320261,320562,320861,320964,322670,322766,323461,323462,323761,
            324061,324561,325061,325561,325562,325761,325961,325962,325963,325964,
            325965,325966,326061,326062,326063,326064,326065,326161,326261,326661,
            326662,326663,326664,326665,327861,330162,330661,331261,331861,332161,
            332665,334361,334561,334562,335561,336461,336661,221562,224062]
genregbl = [213242,224341,225241,225941,226041,226642,226641,227641,311041,311041,
            311141,311241,311341,311641,311741,311941,312341,312641,313341,313451,
            313841,314051,314351,314352,314451,314552,314551,314651,314652,314751,
            314841,314842,315041,315141,315651,315841,316141,316341,316441,316442,
            317041,317042,317141,317341,317541,317641,317741,318841,318941,319551,
            320142,320241,320541,320842,320941,322642,322743,323452,323451,323741,
            324041,324541,325041,325541,325541,325741,325942,325942,325942,325942,
            325941,325942,326041,326041,326041,326041,326041,326142,326241,326641,
            326642,326641,326643,326642,327841,330141,330641,331242,331841,332141,
            332642,334341,334541,334542,335541,336441,336641,221541,224041]

def uretmiktar(sav_ismi):
    psspy.bsys(0,0,[ 0.38, 400.],2,[3,2],len(genbuslst),genbuslst,0,[],0,[])
    psspy.case("C:\\Users\erdidogan\Downloads\\"+sav_ismi+".sav")
    psspy.progress_output(6,"",[0,0])
    gensum = psspy.amachreal(0, 1, 'MVA')[1]
    genbase = psspy.amachreal(0, 4, 'MBASE')[1]
    GorBur_MVA = psspy.brnmsc(221621,220121,r'''1''','MVA')[1]
    GobMKP_MVA = psspy.brnmsc(311121,221521,r'''1''','MVA')[1]
    GobDev_MVA = psspy.brnmsc(311121,227121,r'''1''','MVA')[1]
    GobKar_MVA = psspy.brnmsc(311121,224022,r'''1''','MVA')[1]
    sayserv = psspy.abuscount(0, 1)[1]
    saymachs = psspy.amachcount(0, 4)[1]
    gentop, genbaz, outservis, machsof, gentoplat, regbussit = 0, 0, 0, 0, 0, 0
    giveup = []
    for i in range(len(gensum[0])):
        gentop = gentop + gensum[0][i]
    for i in range(len(genbase[0])):
        genbaz = genbaz + genbase[0][i]
    for i in range(len(genbuslst)):
        psspy.bsysinit(9)
        psspy.bsyso(9,genbuslst[i])
        ierr, sayservtek = psspy.abuscount(9, 1)
        if sayservtek == 0:
            outservis += 1
    print("Bildigin uzere Bursa bolgesi ruzgar uretimlerinden oldukca etkilenmektedir. Analize baslamadan once asagidaki bilgileri incelemeni tavsiye ediyorum..")           
    print(("Gorukle - Bursa Sanayi: %3.2f MVA, Gobel - MKemal Pasa: %3.2f MVA, Gobel - Deveci Konagi: %3.2f MVA, Gobel - Karacabey: %3.2f MVA "%(GorBur_MVA,GobMKP_MVA,GobDev_MVA,GobKar_MVA)))
    print(("KBA ve BA sinirlari icerisinde su anda toplam %i unitenin %i'i serviste degil. Santrallerin kurulu gucu %3.2f MVA. Ruzgar santrallerindeki mevcut toplam uretim miktari ise %3.2f MVA'dir."%(len(genbuslst),outservis,genbaz,gentop)))
    user = int(eval(input("Ruzgar santrallerinde degisiklik yapmak ister misin? Istersen 1 yaz, istemezsen 2 yaz entera bas: ")))
    if user == 1:
        oran = int(eval(input("Serviste olmayan santralleri servise alip tum gruplarin aktif guc uretim miktarlarini degisterecegiz. Gruplarin uretim miktari % kac olsun. %20 ile %80 arasinda bir rakam girmelisin. Ornegin 60 yazip entera\
 basarsan tum gruplarin kurulu gucunun %60i uretilecek: ")))
        for i in range(len(genregbl)):
            psspy.bsysinit(9)
            psspy.bsyso(9,genregbl[i])
            ierr, regbussit = psspy.abuscount(9, 1)
            if regbussit == 0:
                psspy.recn(genregbl[i])
                ierr = psspy.fdns([0,0,0,1,1,1,0,0])
                if ierr > 0:
                    giveup.append(i)
                    psspy.dscn(genregbl[i])
                    #print(giveup)
        for i in range(len(giveup)):
            genbuslst.pop(giveup[-i-1])
        #print("------------------")
            
        for i in range(len(genbuslst)):
            psspy.bsysinit(9)
            psspy.bsyso(9,genbuslst[i])
            ierr, sayservtek = psspy.abuscount(9, 1)
            if sayservtek == 0:
                psspy.recn(genbuslst[i])
                #print(i)
                #psspy.fdns([0,0,0,1,1,1,0,0])
                if ierr > 0:
                    giveup.append(i)
                    #print(giveup)
        
        for i in range(len(genbuslst)):
            carp = (float(oran)/100)
            psspy.machine_chng_2(genbuslst[i],r"""1""",[1,_i,_i,_i,_i,_i],[carp*(genbase[0][i]),_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])
            #print(i)
            #psspy.fdns([0,0,0,1,1,1,0,0])
        psspy.fdns([0,0,0,1,1,1,0,0])

        
    if user == 1:
        psspy.machine_chng_2(311064,r"""1""",[0,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])   #KMENDERES 
        psspy.machine_chng_2(314562,r"""1""",[0,_i,_i,_i,_i,_i],[_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f,_f])   #SAYALARRES
        #Kmenderes ve sayalarres ruzgar uretimlerini artirinca acilari cok dengesiz cikiyor. Bu sebeple sh edildi.
        ierr, gensumlat = psspy.amachreal(0, 1, 'MVA')
        for i in range(len(gensumlat[0])):
            gentoplat = gentoplat + gensumlat[0][i]
        ierr, secsaymachs = psspy.amachcount(0, 1)
        print("----------------------------------------------------------------------------------------------")
        print(("Su anda KBA ve BA da mevcut %i grup serviste ve uretim miktarlari %3.2f MVA ya ayarlanmistir."%(secsaymachs,gentoplat)))
        print("----------------------------------------------------------------------------------------------")
        psspy.fdns([0,0,0,1,1,1,0,0])
        ierr, GorBur_MVAl = psspy.brnmsc(221621,220121,r'''1''','MVA')
        ierr, GobMKP_MVAl = psspy.brnmsc(311121,221521,r'''1''','MVA')
        ierr, GobDev_MVAl = psspy.brnmsc(311121,227121,r'''1''','MVA')
        ierr, GobKar_MVAl = psspy.brnmsc(311121,224022,r'''1''','MVA')
        print(("Gorukle - Bursa Sanayi: %3.2f MVA, Gobel - MKemal Pasa: %3.2f MVA, Gobel - Deveci Konagi: %3.2f MVA, Gobel - Karacabey: %3.2f MVA "%(GorBur_MVAl,GobMKP_MVAl,GobDev_MVAl,GobKar_MVAl)))
        psspy.save("C:\\Users\erdidogan\Downloads\\"+sav_ismi+".sav")
    else:
        print("----------------------------------------------------------------------------------------------")
        print("Ruzgar santrallerinin uretim miktarlari mevcut haliyle birakilmistir.")
        print("----------------------------------------------------------------------------------------------")
        

#34.5 kV Bara Servise Alma
psspy.bsysinit(1)
siddik = 217241
kroman1 = 211441
kroman2 = 211442
colak1 = 211541
colak2 = 211542
colak3 = 211545
asilcelik1 = 220641
asilcelik2 = 220642
asilcelik3 = 220643
erdemir11 = 231351
erdemir12 = 231352
erdemir13 = 231353
erdemir21 = 231451
erdemir22 = 231452
orhangazi1 = 220841
orhangazi2 = 220842
sav_ismi = ''

def yukdegistir(tm,guc,sav_ismi,file_directory, show_case=True):
    # Open Folder
    psspy.case(file_directory+"\\"+sav_ismi+".sav")
    psspy.progress_output(6,"",[0,0])
    if tm == siddik or tm == kroman1 or tm == kroman2 or tm == colak1 or tm == colak2 \
       or tm == colak3 or tm == asilcelik1 or tm == asilcelik2 or tm == asilcelik3\
       or tm == erdemir11 or tm == erdemir12 or tm == erdemir13 or tm == erdemir21\
       or tm == erdemir22 or tm == orhangazi1 or tm == orhangazi2:
        psspy.bsysinit(1)
        psspy.bsyso(1,tm)
    
    ierr, yuk_bus_co = psspy.abuscount(1, 1)
    if yuk_bus_co == 0:
        psspy.recn(tm)
        psspy.load_chng_5(tm,r"""1""",[1,_i,_i,_i,_i,_i,_i],[guc,_f,_f,_f,_f,_f,_f,_f])
        psspy.fdns([0,0,0,1,1,1,0,0])
        ierr, yuk_load_f = psspy.aloadreal(1, 1, 'MVAACT')
        ierr, yuk_bus_co2 = psspy.abuscount(1, 1)
        ierr, loadbus_name = psspy.abuschar(1, 1, 'NAME')
        if show_case == True:
            print(("%d numarali %sTM'de servis harici olan bara servise alinmis ve 1 adet yuk %.1f MVA'ya ayarlanmistir."%(tm,loadbus_name[0][0],yuk_load_f[0][0])))
    else:
        psspy.load_chng_5(tm,r"""1""",[1,_i,_i,_i,_i,_i,_i],[guc,_f,_f,_f,_f,_f,_f,_f])
        psspy.fdns([0,0,0,1,1,1,0,0])
        ierr, yuk_load_f2 = psspy.aloadreal(1, 1, 'MVAACT')
        ierr, loadbus_name = psspy.abuschar(1, 1, 'NAME')
        if show_case == True:
            print(("%d numarali %sTM'de 1 adet yuk %.1f MVA'ya ayarlanmistir."%(tm,loadbus_name[0][0], yuk_load_f2[0][0])))
    psspy.save(file_directory+"\\"+sav_ismi+".sav")       
def min_load_col_sid(sav_ismi,file_directory): 
    subst_list = [211541,211542,211545,217241]      #[colak1,colak2,colak3,siddik]
    power_list = [15, 30, 0, 0]
    [psspy.load_chng_5(subst_list[i],r"""1""",[1,_i,_i,_i,_i,_i,_i],[power_list[i],_f,_f,_f,_f,_f,_f,_f]) for i in range(len(subst_list))]
    psspy.save(file_directory+"\\"+sav_ismi+".sav")
def max_load_col_sid(sav_ismi,file_directory):
    subst_list = [211541,211542,211545,217241]      #[colak1,colak2,colak3,siddik]
    power_list = [15, 110, 225, 90]
    [psspy.load_chng_5(subst_list[i],r"""1""",[1,_i,_i,_i,_i,_i,_i],[power_list[i],_f,_f,_f,_f,_f,_f,_f]) for i in range(len(subst_list))]
    psspy.save(file_directory+"\\"+sav_ismi+".sav")
#uretmiktar('20210507_1400_SN5_TR0')