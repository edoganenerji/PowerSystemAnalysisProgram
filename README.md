# Power System Analysis Program (Şebeke Analiz Programı (ŞAP))
Bu program **Kuzeybatı Anadolu (KBA) Yük Tevzi** sorumluluk sınırlarında **N-1 etüdü, kısa devre analizi ve bara bölme optimizasyonu** işlemlerini gerçekleştirmek için kullanıcı dostu bir arayüz olarak geliştirilmiştir. Programın amacı KBA **iletim sistemi operatörlerine stratejik kararlarında yardımcı olmaktır**. 

This program is developed as a user friendly interface in order to implement the N-1, short-circuit contingency analyses and bus splitting optimization in the North West Anatolian Dispatching Center of Turkish Electricity Transmission System.
## Non-Dominated Sorted Genetic Algorithm-II (NSGA-II)
İletim sisteminde kısa devre akımlarını sınırlandırırken N-1 güvenliğini sürdürebilmek amacıyla uygulanan bara bölme optimizasyonu için **NSGA-II** tekniği kullanılmıştır. **[Bara bölme optimizasyonu ve NSGA-II yöntemiyle ilgili detaylı bilgileri içeren makalemize buraya tıklayarak ulaşabilirsiniz.](http://pajes.pau.edu.tr/jvi.aspx?un=PAJES-77672&volume=).**

NSGA-II technique is used to execute the bus splitting optimization restricting the short-circuit current while maintaining N-1 security in the transmission system. Please **[click](http://pajes.pau.edu.tr/jvi.aspx?un=PAJES-77672&volume=)** to reach further explanation about the designed technique.
## Programın Çalışma Koşulları
- Geliştirilen yazılım Newton Raphson güç akışları ve kısa devre analizleri için **PSS/E** programını kullanmaktadır. Dolayısıyla yazılımın çalışması için PSS/E **dongle'a** ihtiyacınız olacaktır. 
- Hali hazırda yazılım sadece **KBA Yük Tevzi İşletme Müdürlüğünde** kullanılacak şekilde oluşturulmuştur. Daha sonra uygulama bölgesi genişletilebilir.
- Program **Yük Tevzi Bilgi Sistemi ([YTBS](https://ytbs.teias.gov.tr/ytbs/frm_login.jsf))** üzerinden indirilen PSS/E .sav ve .iec dosyalarıyla çalıştırılmaktadır.

- The developed software uses PSS/E program to run Newton Raphson power flow equations and calculate short-circuit currents.
- The software is created to be used in only North West Anatolian Dispatching Center of Turkish Electricity Transmission System.
- The software is run with PSS/E .sav and .iec file that can be downloaded from Dispatching Center Information System ([YTBS]((https://ytbs.teias.gov.tr/ytbs/frm_login.jsf)).
## Başlangıç sayfası
Başlangıç sayfası (Home Page): 
![image](https://github.com/edoganenerji/PowerSystemAnalysisProgram/tree/main/images/baslangicSayfasi.PNG)

## N-1 Analiz Sayfası
N-1 etüdünü gerçekleştirmek için oluşturulan arayüz (N-1 analysis page): 
![image](https://github.com/edoganenerji/PowerSystemAnalysisProgram/tree/main/images/n_1Sayfasi.PNG)

## Kısa Devre Analiz Sayfası
Kısa devre etüdünü gerçekleştirmek için oluşturulan arayüz (Short-circuit analysis page): 
![image](https://github.com/edoganenerji/PowerSystemAnalysisProgram/tree/main/images/kisaDevreSayfasi.PNG)

## Bara Bölme Optimizasyonu Sayfası
Bara Bölme Optimizasyonunu gerçekleştirmek için oluşturulan arayüz (Bus Splitting Optimization page): 
![image](https://github.com/edoganenerji/PowerSystemAnalysisProgram/tree/main/images/barabolmeSayfasi.PNG)

# Contributing
Pull requestler kabul edilir. Lütfen önce neyi değiştirmek istediğinizi tartışmak için bir konu açınız.

Pull requests is accepted. Please open a title at first to discuss what you want to change.

# License 
[MIT](https://choosealicense.com/licenses/mit/)