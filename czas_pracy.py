import tkinter  as tk 
from tkinter import ttk
from tkinter import messagebox
import time
import datetime
import threading
import requests
import sys
import pystray
from PIL import Image

#zrobić przerwę po 8h pracy
#sterowanie z traya

class CzasPracy():
    def __init__(self):
        root.geometry("384x410")
        root.title("Kontrola czasu pracy")
        root.protocol("WM_DELETE_WINDOW", lambda: self.minimalizuj_do_traya())
        root.attributes('-toolwindow', True)
        self.ikona_play = Image.open("ready.png")
        self.ikona_pauza = Image.open("pause.png")
        self.menu = (
            pystray.MenuItem('Pokaż', self.pokaz_okno, default=True),
            )
        czcionka = ('times',22,'bold')
        self.lbl_aktualny_czas_tekst=tk.Label(root,font=czcionka, text="Aktualny czas:")
        self.lbl_aktualny_czas_tekst.grid(row=0,column=0,padx=5,pady=5,sticky="W")
        self.lbl_aktualny_czas=tk.Label(root,font=czcionka)
        self.lbl_aktualny_czas.grid(row=0,column=1,padx=5,pady=5)
        self.lbl_aktualny_czas_pracy_tekst=tk.Label(root,font=czcionka, text="Bieżący czas pracy:")
        self.lbl_aktualny_czas_pracy_tekst.grid(row=1,column=0,padx=5,pady=5,sticky="W")
        self.lbl_aktualny_czas_pracy=tk.Label(root,font=czcionka)
        self.lbl_aktualny_czas_pracy.grid(row=1,column=1,padx=5,pady=5)
        self.lbl_czas_startu_pracy_tekst=tk.Label(root,font=czcionka,text="Praca start:")
        self.lbl_czas_startu_pracy_tekst.grid(row=2,column=0,padx=5,pady=5,sticky="W")
        self.lbl_czas_startu_pracy=tk.Label(root,font=czcionka)
        self.lbl_czas_startu_pracy.grid(row=2,column=1,padx=5,pady=5)
        self.lbl_pozostalo_pracy_tekst=tk.Label(root,font=czcionka,text="Pozostało pracy:")
        self.lbl_pozostalo_pracy_tekst.grid(row=3,column=0,padx=5,pady=5,sticky="W")
        self.lbl_pozostalo_pracy=tk.Label(root,font=czcionka)
        self.lbl_pozostalo_pracy.grid(row=3,column=1,padx=5,pady=5)
        self.lbl_koniec_pracy_tekst=tk.Label(root,font=czcionka,text="Koniec pracy o:")
        self.lbl_koniec_pracy_tekst.grid(row=4,column=0,padx=5,pady=5,sticky="W")
        self.lbl_koniec_pracy=tk.Label(root,font=czcionka)
        self.lbl_koniec_pracy.grid(row=4,column=1,padx=5,pady=5)
        self.lbl_czas_przerwy_tekst=tk.Label(root,font=czcionka,text="Czas przerwy:")
        self.lbl_czas_przerwy_tekst.grid(row=5,column=0,padx=5,pady=5,sticky="W")
        self.lbl_czas_przerwy=tk.Label(root,font=czcionka)
        self.lbl_czas_przerwy.grid(row=5,column=1,padx=5,pady=5)
        self.lbl_czas_do_przerwy_tekst=tk.Label(root,font=czcionka,text="Czas do przerwy:")
        self.lbl_czas_do_przerwy_tekst.grid(row=6,column=0,padx=5,pady=5,sticky="W")
        self.lbl_czas_do_przerwy=tk.Label(root,font=czcionka)
        self.lbl_czas_do_przerwy.grid(row=6,column=1,padx=5,pady=5)
        
        self.btn_wstrzymaj_czas_pracy = tk.Button(root,text='WSTRZYMAJ PRACĘ', width=15, command=lambda: self.pauza_wznowienie_pracy())
        self.btn_wstrzymaj_czas_pracy.grid(row=7,column=0,ipadx=5,ipady=5,pady=15)
        self.btn_WITHDRAW = tk.Button(root,text='ZAMKNIJ PROGRAM', width=15, command=lambda: self.wyjscie_z_programu())
        self.btn_WITHDRAW.grid(row=7,column=1,ipadx=5,ipady=5,pady=15)
        #funkcja inicjalizująca
        self.start_pracy()

    def start_pracy(self):
        #flagi startowe
        self.uruchomienie_dzisiaj = False
        self.wykorzystana_dluga_przerwa = False
        self.czy_pracuje_dluzej = False
        self.pozostalo_pracy = datetime.timedelta(seconds=1) #potrzebne do pokazania 00:00:00 jak kończy się praca w komórce "pozostało pracy"
        #sprawdzenie czy już dzisiaj byla praca, jesli tak to odczytaj dane
        with open("dane.txt") as file_read:
            for line in file_read:
                linia_tekstu = line.split(";")
                data = linia_tekstu[0]
                if data == datetime.datetime.now().strftime('%Y-%m-%d'):
                    self.uruchomienie_dzisiaj = True
                    self.stempel_czasowy_startu_pracy = datetime.datetime.strptime(linia_tekstu[1],'%H:%M:%S')
                    self.sekund_pracy_dzis = int(linia_tekstu[2])
                    if linia_tekstu[3] == "True": self.wykorzystana_dluga_przerwa = True
                    break                
        #jeśli nie było dzisiaj pracy to wyzeruj wszystkie potrzebne statusy
        if not self.uruchomienie_dzisiaj:
            self.stempel_czasowy_startu_pracy = datetime.datetime.now()
            self.sekund_pracy_dzis = 0
            with open('dane.txt', 'a') as file_write:
                file_write.write("\n" + datetime.datetime.now().strftime('%Y-%m-%d') + ";" + str(self.stempel_czasowy_startu_pracy.strftime('%H:%M:%S')) + ";" + str(self.sekund_pracy_dzis) + ";" + str(self.wykorzystana_dluga_przerwa))
        #czy była praca czy nie to zresetuj poniższe flagi
        self.lbl_czas_startu_pracy.config(text=self.stempel_czasowy_startu_pracy.strftime('%H:%M:%S'))
        self.czas_od_ostatniej_przerwy = 0
        self.licz_czas_od_ostatniej_przerwy = True
        self.czas_trwania_przerwy = 0
        self.licz_czas_przerwy = False
        self.licz_czas_pracy = True
        self.przerwa_dluzsza = False
        #start funkcji która działa co sekundę i jest wstrzymywana przez messageboxy
        self.co_sekunde()
        #start funkcji która działa co sekundę zawsze, bez względu na to czy są messageboxy czy nie
        watek_co_sekunde_zawsze = threading.Thread(target=self.co_sekunde_zawsze)
        watek_co_sekunde_zawsze.start()


    def co_sekunde_zawsze(self):
        self.lbl_aktualny_czas.config(text=time.strftime('%H:%M:%S'))
        if self.licz_czas_pracy:
            self.sekund_pracy_dzis += 1
            self.lbl_aktualny_czas_pracy.config(text=str(datetime.timedelta(seconds=self.sekund_pracy_dzis)))
            if self.pozostalo_pracy.total_seconds() >= 1: self.pozostalo_pracy = datetime.timedelta(hours=8)-datetime.timedelta(seconds = self.sekund_pracy_dzis)
            self.lbl_pozostalo_pracy.config(text=str(self.pozostalo_pracy))
            if self.licz_czas_od_ostatniej_przerwy: self.czas_od_ostatniej_przerwy += 1
        if self.licz_czas_przerwy: self.czas_trwania_przerwy +=1
        if not self.czy_pracuje_dluzej and self.pozostalo_pracy.total_seconds() > 0: 
            self.koniec_pracy = (datetime.datetime.now()+self.pozostalo_pracy).strftime('%H:%M:%S')
        else:
            self.koniec_pracy = '-'
        self.lbl_koniec_pracy.config(text=str(self.koniec_pracy))
        self.lbl_czas_przerwy.config(text=str(datetime.timedelta(seconds=self.czas_trwania_przerwy)))
        self.lbl_czas_do_przerwy.config(text=str(datetime.timedelta(hours=1)-datetime.timedelta(seconds=self.czas_od_ostatniej_przerwy)))
        self.lbl_aktualny_czas.after(1000,self.co_sekunde_zawsze)
    
    def co_sekunde(self):
        #sprawdź czy trzeba wrócić do pracy
        if self.licz_czas_pracy and ((self.czas_trwania_przerwy == 15*60 and self.przerwa_dluzsza) or (self.czas_trwania_przerwy == 5*60 and not self.przerwa_dluzsza)):
            #wstrzymuj czas pracy jeżeli przedłużasz przerwę
            self.licz_czas_pracy = False
            self.przerwa_dluzsza = False
            self.wyslij_wiadomosc_na_telegram()
            messagebox.showwarning("PRZERWA", "Czas wracać do pracy!")
            self.przerwa_dluzsza = False
            self.licz_czas_pracy = True
            self.licz_czas_od_ostatniej_przerwy = True
            self.licz_czas_przerwy = False
            self.czas_od_ostatniej_przerwy = 0
            self.czas_trwania_przerwy = 0
        #sprawdź czy trzeba zrobić przerwę
        if self.czas_od_ostatniej_przerwy == 60*60 and self.sekund_pracy_dzis < 28800:
            if not self.wykorzystana_dluga_przerwa:
                self.przerwa_dluzsza = messagebox.askyesno("PRZERWA", "Zrób przerwę! Czy to ma być długa przerwa?")
                if self.przerwa_dluzsza: self.wykorzystana_dluga_przerwa = True
            else:
                messagebox.showwarning("PRZERWA", "Zrób przerwę!")
            self.licz_czas_od_ostatniej_przerwy = False
            self.licz_czas_przerwy = True
            self.czas_od_ostatniej_przerwy = 0
            self.czas_trwania_przerwy = 0
        #sprawdź czy skończyła się praca
        if self.licz_czas_pracy and self.sekund_pracy_dzis >= 28800 and not self.czy_pracuje_dluzej:
            self.koniec_pracy = '-'
            self.czy_konczysz_prace = messagebox.askyesno("KONIEC PRACY", "Czas kończyć pracę. Czy kończysz?")
            if self.czy_konczysz_prace: 
                self.wyjscie_z_programu()
            else:
                self.czy_pracuje_dluzej = True
        root.after(1000,self.co_sekunde)

    def pauza_wznowienie_pracy(self):
        #pauza czasu pracy
        if self.licz_czas_pracy: self.pauza_czasu_pracy()
        else: self.wznowienie_czasu_pracy()
            
    def pauza_czasu_pracy(self):
        root.configure(background='gold2')
        self.licz_czas_pracy = False
        self.licz_czas_od_ostatniej_przerwy = False
        self.licz_czas_przerwy = True
        self.czas_od_ostatniej_przerwy = 0
        self.btn_wstrzymaj_czas_pracy.config(text='WZNÓW PRACĘ')

    def wznowienie_czasu_pracy(self):
        root.configure(background='#F0F0F0')
        self.licz_czas_pracy = True
        self.licz_czas_od_ostatniej_przerwy = True
        self.licz_czas_przerwy = False
        self.czas_od_ostatniej_przerwy = 0
        self.czas_trwania_przerwy = 0
        self.btn_wstrzymaj_czas_pracy.config(text='WSTRZYMAJ PRACĘ')
    
    def wyslij_wiadomosc_na_telegram(self):
        self.wiadomosc = "Czas wracać do pracy! Skończysz o " + str(self.koniec_pracy)
        self.url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={self.wiadomosc}"
        print(requests.get(self.url).json())

    def wyjscie_z_programu(self):
        lines = open("dane.txt", 'r').readlines()
        ostatnia_linia_odczytana = lines[-1].rstrip()
        czas_pracy_odczytany_podzielony = ostatnia_linia_odczytana.split(";")
        lines[-1] = czas_pracy_odczytany_podzielony[0] + ";" + czas_pracy_odczytany_podzielony[1] + ";" + str(self.sekund_pracy_dzis)+ ";" + str(self.wykorzystana_dluga_przerwa)
        open("dane.txt", 'w').writelines(lines)
        root.destroy()
        sys.exit()  

    def pokaz_okno(self):
        self.icon.stop()
        root.deiconify()

    def minimalizuj_do_traya(self):
        root.withdraw()
        if self.licz_czas_pracy:
            '''self.menu = (
            pystray.MenuItem('Wstrzymaj pracę', self.pauza_z_traya),
            pystray.MenuItem('Pokaż okno', self.pokaz_okno, default=True),
            )'''
            self.icon = pystray.Icon("name", self.ikona_play, "Czas pracy aktywny", self.menu)
            thread = threading.Thread(daemon=True, target=lambda: self.icon.run())
            thread.start()
        else:
            '''self.menu = (
            pystray.MenuItem('Wznów pracę', self.start_z_traya),
            pystray.MenuItem('Pokaż okno', self.pokaz_okno, default=True),
            )'''
            self.icon = pystray.Icon("name", self.ikona_pauza, "Czas pracy wstrzymany", self.menu)
            thread = threading.Thread(daemon=True, target=lambda: self.icon.run())
            thread.start()
        #self.icon.run()
       

    '''def start_z_traya(self):
        self.pokaz_okno()
        self.wznowienie_czasu_pracy()
        self.minimalizuj_do_traya()

    def pauza_z_traya(self):
        self.pokaz_okno()
        self.pauza_czasu_pracy()
        self.minimalizuj_do_traya()
    '''
if __name__ == "__main__":
    TOKEN = "5816344668:AAGgs9IK0iAiWG603pwetbOSdCPxL6zsia8"
    CHAT_ID = "5526684558"

    root = tk.Tk()
    czasPracy = CzasPracy()
    root.mainloop()