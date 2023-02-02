import tkinter  as tk 
from tkinter import ttk
from tkinter import messagebox
import time
import datetime
import threading
import requests


class CzasPracy():
    def __init__(self):
        root.geometry("500x500")
        czcionka = ('times',22,'bold')
        self.lbl_aktualny_czas_tekst=tk.Label(root,font=czcionka, text="Aktualny czas:")
        self.lbl_aktualny_czas_tekst.grid(row=0,column=0,padx=5,pady=5)
        self.lbl_aktualny_czas=tk.Label(root,font=czcionka)
        self.lbl_aktualny_czas.grid(row=0,column=1,padx=5,pady=5)

        self.lbl_aktualny_czas_pracy_tekst=tk.Label(root,font=czcionka, text="Bieżący czas pracy:")
        self.lbl_aktualny_czas_pracy_tekst.grid(row=1,column=0,padx=5,pady=5)
        self.lbl_aktualny_czas_pracy=tk.Label(root,font=czcionka)
        self.lbl_aktualny_czas_pracy.grid(row=1,column=1,padx=5,pady=5)
        
        self.lbl_czas_startu_pracy_tekst=tk.Label(root,font=czcionka,text="Praca start:")
        self.lbl_czas_startu_pracy_tekst.grid(row=2,column=0,padx=5,pady=5)
        self.lbl_czas_startu_pracy=tk.Label(root,font=czcionka)
        self.lbl_czas_startu_pracy.grid(row=2,column=1,padx=5,pady=5)

        self.lbl_pozostalo_pracy_tekst=tk.Label(root,font=czcionka,text="Pozostało pracy:")
        self.lbl_pozostalo_pracy_tekst.grid(row=3,column=0,padx=5,pady=5)
        self.lbl_pozostalo_pracy=tk.Label(root,font=czcionka)
        self.lbl_pozostalo_pracy.grid(row=3,column=1,padx=5,pady=5)

        self.lbl_koniec_pracy_tekst=tk.Label(root,font=czcionka,text="Koniec pracy o:")
        self.lbl_koniec_pracy_tekst.grid(row=4,column=0,padx=5,pady=5)
        self.lbl_koniec_pracy=tk.Label(root,font=czcionka)
        self.lbl_koniec_pracy.grid(row=4,column=1,padx=5,pady=5)

        self.lbl_czas_przerwy_tekst=tk.Label(root,font=czcionka,text="Czas przerwy:")
        self.lbl_czas_przerwy_tekst.grid(row=5,column=0,padx=5,pady=5)
        self.lbl_czas_przerwy=tk.Label(root,font=czcionka)
        self.lbl_czas_przerwy.grid(row=5,column=1,padx=5,pady=5)

        self.lbl_czas_do_przerwy_tekst=tk.Label(root,font=czcionka,text="Czas do przerwy:")
        self.lbl_czas_do_przerwy_tekst.grid(row=6,column=0,padx=5,pady=5)
        self.lbl_czas_do_przerwy=tk.Label(root,font=czcionka)
        self.lbl_czas_do_przerwy.grid(row=6,column=1,padx=5,pady=5)
        
        self.btn_wstrzymaj_czas_pracy = tk.Button(root,text='WSTRZYMAJ PRACĘ', width=15, command=lambda: self.pauza_wznowienie_pracy())
        self.btn_wstrzymaj_czas_pracy.grid(row=7,column=0,ipadx=5,ipady=5)
        
        self.start_pracy()
        self.co_sekunde()
        watek_co_sekunde_zawsze = threading.Thread(target=self.co_sekunde_zawsze)
        watek_co_sekunde_zawsze.start()

    def start_pracy(self):
        self.stempel_czasowy_startu_pracy = datetime.datetime.now() 
        self.lbl_czas_startu_pracy.config(text=self.stempel_czasowy_startu_pracy.strftime('%H:%M:%S'))
        self.czas_od_ostatniej_przerwy = 0
        self.licz_czas_od_ostatniej_przerwy = True
        self.czas_trwania_przerwy = 0
        self.licz_czas_przerwy = False
        self.sekund_pracy_dzis = 0
        self.licz_czas_pracy = True

    def co_sekunde_zawsze(self):
        self.lbl_aktualny_czas.config(text=time.strftime('%H:%M:%S'))
        if self.licz_czas_pracy:
            self.sekund_pracy_dzis += 1
            self.lbl_aktualny_czas_pracy.config(text=str(datetime.timedelta(seconds=self.sekund_pracy_dzis)))
            self.pozostalo_pracy = datetime.timedelta(hours=8)-datetime.timedelta(seconds = self.sekund_pracy_dzis)
            self.lbl_pozostalo_pracy.config(text=str(self.pozostalo_pracy))
            if self.licz_czas_od_ostatniej_przerwy: self.czas_od_ostatniej_przerwy += 1
        if self.licz_czas_przerwy: self.czas_trwania_przerwy +=1
        self.koniec_pracy = (datetime.datetime.now()+self.pozostalo_pracy).strftime('%H:%M:%S')
        self.lbl_koniec_pracy.config(text=str(self.koniec_pracy))
        self.lbl_czas_przerwy.config(text=str(datetime.timedelta(seconds=self.czas_trwania_przerwy)))
        self.lbl_czas_do_przerwy.config(text=str(datetime.timedelta(hours=1)-datetime.timedelta(seconds=self.czas_od_ostatniej_przerwy)))
        self.lbl_aktualny_czas.after(1000,self.co_sekunde_zawsze)
    
    def co_sekunde(self):
        if self.czas_trwania_przerwy == 10 and self.licz_czas_pracy:
            #wstrzymuj czas pracy jeżeli przedłużasz przerwę
            self.licz_czas_pracy = False
            self.wyslij_wiadomosc_na_telegram()
            messagebox.showwarning("PRZERWA", "WZNÓW PRACĘ!")
            self.licz_czas_pracy = True
            self.licz_czas_od_ostatniej_przerwy = True
            self.licz_czas_przerwy = False
            self.czas_od_ostatniej_przerwy = 0
            self.czas_trwania_przerwy = 0
        if self.czas_od_ostatniej_przerwy == 10:
            messagebox.showwarning("PRZERWA", "ZRÓB PRZERWĘ!")
            self.licz_czas_od_ostatniej_przerwy = False
            self.licz_czas_przerwy = True
            self.czas_od_ostatniej_przerwy = 0
            self.czas_trwania_przerwy = 0
        root.after(1000,self.co_sekunde)

    def pauza_wznowienie_pracy(self):
        #pauza czasu pracy
        if self.licz_czas_pracy:
            self.licz_czas_pracy = False
            self.licz_czas_od_ostatniej_przerwy = False
            self.licz_czas_przerwy = True
            self.czas_od_ostatniej_przerwy = 0
            self.btn_wstrzymaj_czas_pracy.config(text='WZNÓW PRACĘ')
        #wznowienie czasu pracy
        else:
            self.licz_czas_pracy = True
            self.licz_czas_od_ostatniej_przerwy = True
            self.licz_czas_przerwy = False
            self.czas_od_ostatniej_przerwy = 0
            self.czas_trwania_przerwy = 0
            self.btn_wstrzymaj_czas_pracy.config(text='WSTRZYMAJ PRACĘ')
    
    def wyslij_wiadomosc_na_telegram(self):
        print(requests.get(URL).json())

if __name__ == "__main__":
    TOKEN = "5816344668:AAGgs9IK0iAiWG603pwetbOSdCPxL6zsia8"
    CHAT_ID = "5526684558"
    wiadomosc = "Czas wracać do pracy!"
    URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={wiadomosc}"

    root = tk.Tk()
    czasPracy = CzasPracy()
    root.mainloop()