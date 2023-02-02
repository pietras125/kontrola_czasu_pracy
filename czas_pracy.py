import tkinter  as tk 
from tkinter import ttk
import time
import datetime


class CzasPracy():
    def __init__(self):
        czcionka = ('times',52,'bold') # display size and style
        self.lbl_aktualny_czas=tk.Label(root,font=czcionka,bg='yellow')
        self.lbl_aktualny_czas.grid(row=0,column=0,padx=5,pady=25)
        self.lbl_aktualny_czas_pracy=tk.Label(root,font=czcionka,bg='yellow')
        self.lbl_aktualny_czas_pracy.grid(row=1,column=0,padx=5,pady=25)
        self.lbl_czas_startu_pracy=tk.Label(root,font=czcionka,bg='yellow')
        self.lbl_czas_startu_pracy.grid(row=2,column=0,padx=5,pady=25)
        
        self.start_pracy()

    def start_pracy(self):
        self.stempel_czasowy_startu_pracy = datetime.datetime.now() 
        self.lbl_czas_startu_pracy.config(text=self.stempel_czasowy_startu_pracy.strftime('%H:%M:%S'))
        self.sekund_pracy_dzis = 0
        self.licz_czas_pracy = True

    def pokaz_aktualny_czas(self):
        string_aktualny_czas = time.strftime('%H:%M:%S') 
        self.lbl_aktualny_czas.config(text=string_aktualny_czas)
        #sprawdź czy dodać sekundy
        if self.licz_czas_pracy:
            self.sekund_pracy_dzis += 1
            self.lbl_aktualny_czas_pracy.config(text=self.sekund_pracy_dzis)
        
        self.lbl_aktualny_czas.after(1000,self.pokaz_aktualny_czas) # time delay of 1000 milliseconds
    
    

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("405x170")
    czasPracy = CzasPracy()

    czasPracy.pokaz_aktualny_czas()

    root.mainloop()