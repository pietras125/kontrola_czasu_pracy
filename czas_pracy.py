import tkinter  as tk
from tkinter import messagebox, ttk
import time
import datetime
import threading
import requests
import sys
import pystray
import csv
import os
from PIL import Image, ImageTk


class CzasPracy():
    def __init__(self):
        # Konfiguracja głównego okna
        root.title("Kontrola pracy i przerw")
        root.protocol("WM_DELETE_WINDOW", lambda: self.minimalizuj_do_traya())
        root.configure(bg='#f0f0f0')
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.resizable(False, False)  # Włącz możliwość zmiany rozmiaru
        # root.attributes('-toolwindow', True)  # Usuń przyciski minimalizacji/maksymalizacji - WYŁĄCZONE
        
        # Ikony dla tray
        self.ikona_play = Image.open("ready.png")
        self.ikona_pauza = Image.open("pause.png")
        self.menu = (
            pystray.MenuItem('Pokaż', self.pokaz_okno, default=True),
            )
        
        # Style i kolory
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Konfiguracja stylów
        self.style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        self.style.configure('Value.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Action.TButton', font=('Segoe UI', 10, 'bold'))
        
        # Style dla przycisków
        self.style.configure('Pause.TButton', background='#f39c12', foreground='white')
        self.style.configure('Resume.TButton', background='#27ae60', foreground='white')
        self.style.configure('Close.TButton', background='#e74c3c', foreground='white')
        
        # Style dla stanów hover i disabled - zapobiegają białemu tłu po najechaniu
        self.style.map('Pause.TButton',
                      background=[('active', '#e67e22'), ('pressed', '#d35400'), ('disabled', '#bdc3c7')],
                      foreground=[('active', 'white'), ('pressed', 'white'), ('disabled', '#7f8c8d')])
        self.style.map('Resume.TButton',
                      background=[('active', '#229954'), ('pressed', '#1e8449'), ('disabled', '#bdc3c7')],
                      foreground=[('active', 'white'), ('pressed', 'white'), ('disabled', '#7f8c8d')])
        self.style.map('Close.TButton',
                      background=[('active', '#c0392b'), ('pressed', '#a93226'), ('disabled', '#bdc3c7')],
                      foreground=[('active', 'white'), ('pressed', 'white'), ('disabled', '#7f8c8d')])
        
        # Główny kontener z paddingiem
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Konfiguracja grid weights dla responsywności
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Czcionki
        font_title = ('Segoe UI', 16, 'bold')
        font_label = ('Segoe UI', 12)
        font_value = ('Segoe UI', 14, 'bold')  # Zwiększona z 12 na 14
        font_time = ('Segoe UI', 24, 'bold')  # Jeszcze większa czcionka dla aktualnego czasu
        font_button = ('Segoe UI', 10, 'bold')
        
        # Górny rząd - dwie kolumny obok siebie
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        
        # Lewa kolumna - Aktualny czas
        time_frame = ttk.LabelFrame(top_frame, text="🕐 Aktualny czas", padding="10")
        time_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        time_frame.columnconfigure(0, weight=1)
        time_frame.rowconfigure(0, weight=1)
        
        self.lbl_aktualny_czas = ttk.Label(time_frame, font=font_time, foreground='#2c3e50')
        self.lbl_aktualny_czas.grid(row=0, column=0, pady=20, sticky=(tk.N, tk.S))
        
        # Sekcja Sterowanie - osobna sekcja pod "Aktualny czas"
        control_frame = ttk.LabelFrame(top_frame, text="🎮 Sterowanie", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=(5, 0))
        control_frame.columnconfigure(0, weight=1)
        
        # Przyciski główne - układ pionowy
        main_button_frame = ttk.Frame(control_frame)
        main_button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        main_button_frame.columnconfigure(0, weight=1)
        
        self.btn_wstrzymaj_czas_pracy = ttk.Button(main_button_frame, text='⏸️ WSTRZYMAJ PRACĘ', 
                                                  command=lambda: self.pauza_wznowienie_pracy(),
                                                  style='Pause.TButton')
        self.btn_wstrzymaj_czas_pracy.grid(row=0, column=0, pady=2, sticky=(tk.W, tk.E))
        
        self.btn_manual_break = ttk.Button(main_button_frame, text='☕ PRZERWA', 
                                         command=self.manual_break,
                                         style='Resume.TButton')
        self.btn_manual_break.grid(row=1, column=0, pady=2, sticky=(tk.W, tk.E))
        
        self.btn_WITHDRAW = ttk.Button(main_button_frame, text='❌ ZAMKNIJ PROGRAM', 
                                      command=lambda: self.wyjscie_z_programu(),
                                      style='Close.TButton')
        self.btn_WITHDRAW.grid(row=2, column=0, pady=2, sticky=(tk.W, tk.E))
        
        # Prawa kolumna - Czas pracy + Przerwy
        right_frame = ttk.Frame(top_frame)
        right_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Czas pracy
        work_frame = ttk.LabelFrame(right_frame, text="💼 Czas pracy", padding="10")
        work_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        work_frame.columnconfigure(1, weight=1)
        
        ttk.Label(work_frame, text="Bieżący czas pracy:", font=font_label).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_aktualny_czas_pracy = ttk.Label(work_frame, font=font_value, foreground='#27ae60')
        self.lbl_aktualny_czas_pracy.grid(row=0, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(work_frame, text="Praca start:", font=font_label).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_czas_startu_pracy = ttk.Label(work_frame, font=font_value, foreground='#3498db')
        self.lbl_czas_startu_pracy.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(work_frame, text="Pozostało pracy:", font=font_label).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_pozostalo_pracy = ttk.Label(work_frame, font=font_value, foreground='#e74c3c')
        self.lbl_pozostalo_pracy.grid(row=2, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(work_frame, text="Koniec pracy o:", font=font_label).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_koniec_pracy = ttk.Label(work_frame, font=font_value, foreground='#8e44ad')
        self.lbl_koniec_pracy.grid(row=3, column=1, sticky=tk.E, pady=2)
        
        # Przerwy pod czasem pracy
        break_frame = ttk.LabelFrame(right_frame, text="☕ Przerwy", padding="10")
        break_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
        break_frame.columnconfigure(1, weight=1)
        
        ttk.Label(break_frame, text="Czas przerwy:", font=font_label).grid(row=0, column=0, sticky=tk.W, pady=2)
        self.lbl_czas_przerwy = ttk.Label(break_frame, font=font_value, foreground='#f39c12')
        self.lbl_czas_przerwy.grid(row=0, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(break_frame, text="Czas do końca przerwy:", font=font_label).grid(row=1, column=0, sticky=tk.W, pady=2)
        self.lbl_czas_do_konca_przerwy = ttk.Label(break_frame, font=font_value, foreground='#e74c3c')
        self.lbl_czas_do_konca_przerwy.grid(row=1, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(break_frame, text="Czas do przerwy:", font=font_label).grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lbl_czas_do_przerwy = ttk.Label(break_frame, font=font_value, foreground='#e67e22')
        self.lbl_czas_do_przerwy.grid(row=2, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(break_frame, text="Suma przerw:", font=font_label).grid(row=3, column=0, sticky=tk.W, pady=2)
        self.lbl_suma_przerw = ttk.Label(break_frame, font=font_value, foreground='#9b59b6')
        self.lbl_suma_przerw.grid(row=3, column=1, sticky=tk.E, pady=2)
        
        ttk.Label(break_frame, text="Przerwy do zrobienia:", font=font_label).grid(row=4, column=0, sticky=tk.W, pady=2)
        self.lbl_przerwy_do_zrobienia = ttk.Label(break_frame, font=font_value, foreground='#3498db')
        self.lbl_przerwy_do_zrobienia.grid(row=4, column=1, sticky=tk.E, pady=2)
        
        # Sekcja stopera
        stopwatch_frame = ttk.LabelFrame(main_frame, text="⏱️ Stoper", padding="10")
        stopwatch_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        stopwatch_frame.columnconfigure(0, weight=1)
        stopwatch_frame.columnconfigure(1, weight=1)
        stopwatch_frame.columnconfigure(2, weight=1)
        stopwatch_frame.columnconfigure(3, weight=1)
        
        # Czas stopera i przyciski w jednej linii
        self.lbl_stopwatch_time = ttk.Label(stopwatch_frame, font=font_value, foreground='#9b59b6')
        self.lbl_stopwatch_time.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.btn_stopwatch_start = ttk.Button(stopwatch_frame, text='▶️ START', 
                                            command=self.stopwatch_start, style='Resume.TButton')
        self.btn_stopwatch_start.grid(row=0, column=1, padx=(10, 3), sticky=(tk.W, tk.E))
        
        self.btn_stopwatch_pause = ttk.Button(stopwatch_frame, text='⏸️ PAUZA', 
                                           command=self.stopwatch_stop, style='Pause.TButton')
        self.btn_stopwatch_pause.grid(row=0, column=2, padx=3, sticky=(tk.W, tk.E))
        
        self.btn_stopwatch_reset = ttk.Button(stopwatch_frame, text='🔄 RESET', 
                                            command=self.stopwatch_reset, style='Close.TButton')
        self.btn_stopwatch_reset.grid(row=0, column=3, padx=(3, 0), sticky=(tk.W, tk.E))
        
        # Konfiguracja grid weights dla main_frame
        main_frame.rowconfigure(3, weight=1)
        top_frame.rowconfigure(0, weight=1)
        
        # Automatyczne dostosowanie rozmiaru okna - WYŁĄCZONE
        # root.update_idletasks()
        # width = root.winfo_reqwidth()
        # height = root.winfo_reqheight()
        # root.geometry(f"{width}x{height}")
        
        # Ustaw domyślny rozmiar okna (możesz go zmienić)
        root.geometry("480x550")
        
        # Ustawienie ikony okna
        try:
            # Użyj ikony play jako ikony okna
            icon_image = ImageTk.PhotoImage(self.ikona_play)
            root.iconphoto(True, icon_image)
        except:
            pass  # Jeśli nie uda się ustawić ikony, kontynuuj bez niej
        
        # Inicjalizacja ikony tray
        self.icon = None
        self.icon_thread = None
        
        #funkcja inicjalizująca
        self.start_pracy()

    def start_pracy(self):
        #flagi startowe
        self.uruchomienie_dzisiaj = False
        self.wykorzystana_dluga_przerwa = False
        self.czy_pracuje_dluzej = False
        self.sekund_od_ostatniego_zapisu = 0
        self.pozostalo_pracy = datetime.timedelta(seconds=1) #potrzebne do pokazania 00:00:00 jak kończy się praca w komórce "pozostało pracy"
        self.suma_przerw_sekundy = 0  # Suma wszystkich przerw w sekundach
        #sprawdzenie czy już dzisiaj byla praca, jesli tak to odczytaj dane
        dzisiejsza_data = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Sprawdź czy plik CSV istnieje
        if os.path.exists("dane.csv"):
            with open("dane.csv", 'r', newline='', encoding='utf-8') as file_read:
                reader = csv.DictReader(file_read)
                for row in reader:
                    if row['Data'] == dzisiejsza_data:
                        self.uruchomienie_dzisiaj = True
                        self.stempel_czasowy_startu_pracy = datetime.datetime.strptime(row['Czas_startu'],'%H:%M:%S')
                        self.sekund_pracy_dzis = int(row['Sekund_pracy'])
                        if row['Wykorzystana_dluga_przerwa'] == "True": 
                            self.wykorzystana_dluga_przerwa = True
                        self.czas_od_ostatniej_przerwy = int(row['Czas_od_ostatniej_przerwy'])
                        self.suma_przerw_sekundy = int(row['Suma_przerw_sekundy'])
                        break                
        #jeśli nie było dzisiaj pracy to wyzeruj wszystkie potrzebne statusy
        if not self.uruchomienie_dzisiaj:
            # Potwierdzenie startu pracy przy pierwszym uruchomieniu danego dnia
            potwierdzenie = messagebox.askyesno("Start pracy", 
                                              f"Czy chcesz rozpocząć pracę?\n\n"
                                              f"Data: {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
                                              f"Czas: {datetime.datetime.now().strftime('%H:%M:%S')}\n\n"
                                              f"Jeśli nie pracujesz teraz, kliknij 'Nie' - aplikacja będzie działać w tle.",
                                              parent=root, icon='question')
            
            if potwierdzenie:
                self.stempel_czasowy_startu_pracy = datetime.datetime.now()
                self.sekund_pracy_dzis = 0
                self.czas_od_ostatniej_przerwy = 0
                self.zapisz_nowy_dzien_csv()
            else:
                # Jeśli nie potwierdził startu, ustaw flagi ale nie licz czasu pracy
                self.stempel_czasowy_startu_pracy = datetime.datetime.now()
                self.sekund_pracy_dzis = 0
                self.czas_od_ostatniej_przerwy = 0
                self.licz_czas_pracy = False  # Nie licz czasu pracy
                self.zapisz_nowy_dzien_csv()
                # Zmień przycisk na "Rozpocznij pracę"
                self.btn_wstrzymaj_czas_pracy.config(text='▶️ ROZPOCZNIJ PRACĘ', style='Resume.TButton')
        #czy była praca czy nie to zresetuj poniższe flagi
        self.lbl_czas_startu_pracy.config(text=self.stempel_czasowy_startu_pracy.strftime('%H:%M:%S'))
        self.licz_czas_od_ostatniej_przerwy = True
        self.czas_trwania_przerwy = 0
        self.licz_czas_przerwy = False
        self.licz_czas_pracy = True
        self.przerwa_dluzsza = False
        
        # Inicjalizacja stopera
        self.stopwatch_running = False
        self.stopwatch_seconds = 0
        self.lbl_stopwatch_time.config(text="0:00:00")
        
        # Ustawienie stanu przycisków stopera na starcie
        self.btn_stopwatch_start.config(state='normal')
        self.btn_stopwatch_pause.config(state='disabled')
        self.btn_stopwatch_reset.config(state='disabled')
        
        #start funkcji która działa co sekundę i jest wstrzymywana przez messageboxy
        self.co_sekunde()
        #start funkcji która działa co sekundę zawsze, bez względu na to czy są messageboxy czy nie
        watek_co_sekunde_zawsze = threading.Thread(target=self.co_sekunde_zawsze)
        watek_co_sekunde_zawsze.start()

    def co_sekunde_zawsze(self):
        #wyświetlenie bieżącego czasu
        self.lbl_aktualny_czas.config(text=time.strftime('%H:%M:%S'))
        #dodawanie sekundy do czasu pracy jeśli jest liczony
        if self.licz_czas_pracy:
            self.sekund_pracy_dzis += 1
            self.lbl_aktualny_czas_pracy.config(text=str(datetime.timedelta(seconds=self.sekund_pracy_dzis)))
            #wyświetlenie ile czasu zostało
            if self.pozostalo_pracy.total_seconds() >= 1: self.pozostalo_pracy = datetime.timedelta(hours=8)-datetime.timedelta(seconds = self.sekund_pracy_dzis)
            self.lbl_pozostalo_pracy.config(text=str(self.pozostalo_pracy))
            #liczenie czasu od ostatniej skończonej przerwy
            if self.licz_czas_od_ostatniej_przerwy: self.czas_od_ostatniej_przerwy += 1
        #jeśli trwa przerwa to licz jej czas
        if self.licz_czas_przerwy: self.czas_trwania_przerwy +=1
        
        # Stoper - jeśli działa, dodaj sekundę
        if self.stopwatch_running:
            self.stopwatch_seconds += 1
            self.lbl_stopwatch_time.config(text=self.format_stopwatch_time(self.stopwatch_seconds))
        #wyzerowanie licznika czasu pozostałej pracy, jeśli pracuję ponad 8h 
        if not self.czy_pracuje_dluzej and self.pozostalo_pracy.total_seconds() > 0: 
            self.koniec_pracy = (datetime.datetime.now()+self.pozostalo_pracy).strftime('%H:%M:%S')
        else:
            self.koniec_pracy = '-'
        #zapis do pliku co minutę
        if self.sekund_od_ostatniego_zapisu == 60:
            self.sekund_od_ostatniego_zapisu = 0
            self.zapis_do_pliku()
        else:
            self.sekund_od_ostatniego_zapisu += 1
        #wyświetlenie danych
        self.lbl_koniec_pracy.config(text=str(self.koniec_pracy))
        self.lbl_czas_przerwy.config(text=str(datetime.timedelta(seconds=self.czas_trwania_przerwy)))
        # Wyświetlanie czasu do przerwy - jeśli jesteśmy na pauzie lub czas przekroczył 1h, pokaż 0
        if self.licz_czas_przerwy or self.czas_od_ostatniej_przerwy >= 3600:
            self.lbl_czas_do_przerwy.config(text="0:00:00")
        else:
            czas_do_przerwy = datetime.timedelta(hours=1) - datetime.timedelta(seconds=self.czas_od_ostatniej_przerwy)
            self.lbl_czas_do_przerwy.config(text=str(czas_do_przerwy))
        
        # Wyświetlanie czasu do końca przerwy
        if self.licz_czas_przerwy:
            # Oblicz ile czasu zostało do końca przerwy
            if self.przerwa_dluzsza:
                czas_do_konca = datetime.timedelta(minutes=15) - datetime.timedelta(seconds=self.czas_trwania_przerwy)
            else:
                czas_do_konca = datetime.timedelta(minutes=5) - datetime.timedelta(seconds=self.czas_trwania_przerwy)
            
            # Upewnij się, że nie ma ujemnych wartości
            if czas_do_konca.total_seconds() < 0:
                czas_do_konca = datetime.timedelta(seconds=0)
            
            self.lbl_czas_do_konca_przerwy.config(text=str(czas_do_konca))
        else:
            self.lbl_czas_do_konca_przerwy.config(text="0:00:00")
        
        # Aktualizacja sumy przerw na bieżąco (dodaj aktualny czas przerwy)
        suma_przerw_z_aktualna = self.suma_przerw_sekundy + self.czas_trwania_przerwy
        self.lbl_suma_przerw.config(text=str(datetime.timedelta(seconds=suma_przerw_z_aktualna)))
        
        # Oblicz ile czasu przerw powinieneś mieć: 6x5 minut + 15 minut = 45 minut
        # Struktura: 5min, 5min, 5min, 5min, 5min, 5min, 15min (długa przerwa)
        # Każda przerwa co 55 minut pracy (1h pracy - 5min przerwy = 55min efektywnej pracy)
        
        # Oblicz ile przerw 5-minutowych powinieneś mieć
        przerwy_5min_do_zrobienia = self.sekund_pracy_dzis // (55 * 60)  # co 55 minut pracy
        czas_przerw_5min_do_zrobienia = przerwy_5min_do_zrobienia * 5 * 60  # 5 minut na przerwę
        
        # Dodaj 15 minut długiej przerwy (jeśli pracujesz wystarczająco długo)
        czas_dlugiej_przerwy_do_zrobienia = 15 * 60 if self.sekund_pracy_dzis >= 6 * 55 * 60 else 0
        
        # Całkowity czas przerw do zrobienia
        czas_przerw_do_zrobienia = czas_przerw_5min_do_zrobienia + czas_dlugiej_przerwy_do_zrobienia
        
        # Odejmij już wykorzystane długie przerwy (jeśli była długa przerwa, odejmij 15 minut)
        if self.wykorzystana_dluga_przerwa:
            czas_przerw_do_zrobienia -= 15 * 60
        
        # Upewnij się, że nie ma ujemnych wartości
        czas_przerw_do_zrobienia = max(0, czas_przerw_do_zrobienia)
        
        self.lbl_przerwy_do_zrobienia.config(text=str(datetime.timedelta(seconds=czas_przerw_do_zrobienia)))
        #uruchomienie tej funckji za równą minutę (w pętli root.mainloop)
        self.lbl_aktualny_czas.after(1000,self.co_sekunde_zawsze)
    
    def co_sekunde(self):
        #sprawdź czy trzeba wrócić do pracy
        if self.licz_czas_pracy and ((self.czas_trwania_przerwy == 15*60 and self.przerwa_dluzsza) or (self.czas_trwania_przerwy == 5*60 and not self.przerwa_dluzsza)):
            # Dodaj czas przerwy do sumy
            self.suma_przerw_sekundy += self.czas_trwania_przerwy
            #wstrzymuj czas pracy jeżeli przedłużasz przerwę
            #self.licz_czas_pracy = False - #dopiero po wciśnięciu przycisku w messageboxie startuje czas pracy - TUTAJ SIĘ WŁĄCZA
            self.przerwa_dluzsza = False
            self.wyslij_wiadomosc_na_telegram()
            messagebox.showwarning("PRZERWA", "Czas wracać do pracy!", parent=root)
            #dopiero po wciśnięciu przycisku w messageboxie startuje czas pracy - WYŁĄCZONE
            self.licz_czas_pracy = True
            self.licz_czas_od_ostatniej_przerwy = True
            self.licz_czas_przerwy = False
            self.czas_od_ostatniej_przerwy = 0
            self.czas_trwania_przerwy = 0
            # Zmień przycisk z powrotem na "Przerwa"
            self.btn_manual_break.config(text='☕ PRZERWA', style='Resume.TButton')
            # Odblokuj przycisk pauzy gdy przerwa się kończy
            self.btn_wstrzymaj_czas_pracy.config(state='normal')
            # Aktualizuj ikonę w tray
            if hasattr(self, 'icon') and self.icon:
                self.update_tray_icon()
        #sprawdź czy trzeba zrobić przerwę
        if self.czas_od_ostatniej_przerwy == 60*60 and self.sekund_pracy_dzis < 28800:
            self.show_break_dialog()
        #sprawdź czy skończyła się praca
        if self.licz_czas_pracy and self.sekund_pracy_dzis >= 28800 and not self.czy_pracuje_dluzej:
            self.koniec_pracy = '-'
            self.czy_konczysz_prace = messagebox.askyesno("KONIEC PRACY", "Czas kończyć pracę. Czy kończysz?", parent=root)
            if self.czy_konczysz_prace: 
                self.wyjscie_z_programu()
            else:
                self.czy_pracuje_dluzej = True
        root.after(1000,self.co_sekunde)

    def pauza_wznowienie_pracy(self):
        #pauza czasu pracy lub rozpoczęcie pracy
        if self.licz_czas_pracy: 
            self.pauza_czasu_pracy()
        else: 
            self.wznowienie_czasu_pracy()
            
    def pauza_czasu_pracy(self):
        root.configure(background='#fff3cd')  # Jasny żółty dla pauzy
        self.licz_czas_pracy = False
        self.licz_czas_od_ostatniej_przerwy = False
        self.licz_czas_przerwy = False  # NIE liczy przerwy - to jest pauza, nie przerwa
        self.czas_od_ostatniej_przerwy = 0  # Resetuj licznik czasu do przerwy
        self.czas_trwania_przerwy = 0  # Resetuj czas trwania przerwy
        
        # Anuluj przerwę i wyszarz przycisk przerwy (nie można robić przerwy podczas pauzy)
        self.btn_manual_break.config(text='☕ PRZERWA', style='Resume.TButton', state='disabled')
        
        # Zmień przycisk pauzy na "WZNÓW PRACĘ" - powinien być aktywny
        self.btn_wstrzymaj_czas_pracy.config(text='▶️ WZNÓW PRACĘ', style='Resume.TButton', state='normal')
        
        # Aktualizuj ikonę w tray
        if hasattr(self, 'icon') and self.icon:
            self.update_tray_icon()

    def wznowienie_czasu_pracy(self):
        root.configure(background='#f0f0f0')  # Standardowe tło
        self.licz_czas_pracy = True
        self.licz_czas_od_ostatniej_przerwy = True
        self.licz_czas_przerwy = False
        self.czas_od_ostatniej_przerwy = 0  # Resetuj licznik czasu do przerwy - zaczynamy od nowa
        self.czas_trwania_przerwy = 0  # Resetuj czas trwania przerwy
        
        # Odblokuj przycisk pauzy i zmień na "WSTRZYMAJ PRACĘ"
        self.btn_wstrzymaj_czas_pracy.config(text='⏸️ WSTRZYMAJ PRACĘ', style='Pause.TButton', state='normal')
        
        # Zmień przycisk z powrotem na "Przerwa" i odblokuj go
        self.btn_manual_break.config(text='☕ PRZERWA', style='Resume.TButton', state='normal')
        
        # Aktualizuj ikonę w tray
        if hasattr(self, 'icon') and self.icon:
            self.update_tray_icon()
        
        # Jeśli to pierwszy start pracy danego dnia, zaktualizuj plik
        if not self.uruchomienie_dzisiaj:
            self.zapis_do_pliku()
    
    def stopwatch_start(self):
        """Uruchom stoper"""
        self.stopwatch_running = True
        self.btn_stopwatch_start.config(state='disabled')
        self.btn_stopwatch_pause.config(state='normal')
        self.btn_stopwatch_reset.config(state='normal')
        
    def stopwatch_stop(self):
        """Zatrzymaj stoper"""
        self.stopwatch_running = False
        self.btn_stopwatch_start.config(state='normal')
        self.btn_stopwatch_pause.config(state='disabled')
        
    def stopwatch_reset(self):
        """Resetuj stoper"""
        self.stopwatch_running = False
        self.stopwatch_seconds = 0
        self.lbl_stopwatch_time.config(text="0:00:00")
        self.btn_stopwatch_start.config(state='normal')
        self.btn_stopwatch_pause.config(state='disabled')
        self.btn_stopwatch_reset.config(state='disabled')
        
    def format_stopwatch_time(self, seconds):
        """Formatuj czas stopera w formacie 0:00:00"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    
    def show_break_dialog(self):
        """Pokaż okno dialogowe z opcjami przerwy"""
        # Tworzymy własne okno dialogowe z trzema opcjami
        dialog = tk.Toplevel(root)
        dialog.title("PRZERWA")
        dialog.geometry("250x300")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()
        
        # Ustawienie koloru tła takiego samego jak główne okno
        dialog.configure(bg='#f0f0f0')
        
        # Ustawienie okna zawsze na pierwszym planie
        dialog.attributes('-topmost', True)
        
        # Centrowanie okna
        dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))
        
        # Główny kontener z paddingiem
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        title_label = ttk.Label(main_frame, text="☕ Czas na przerwę!", 
                               font=('Segoe UI', 16, 'bold'), 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Opcje
        if not self.wykorzystana_dluga_przerwa:
            info_label = ttk.Label(main_frame, text="Czy to ma być długa przerwa?", 
                                  font=('Segoe UI', 12))
            info_label.pack(pady=(0, 20))
            
            # Przyciski w układzie pionowym dla lepszego dopasowania
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=10)
            
            # Konfiguracja grid dla przycisków
            button_frame.columnconfigure(0, weight=1)
            
            btn_short = ttk.Button(button_frame, text="☕ Krótka przerwa (5 min)", 
                                  command=lambda: self.start_break(dialog, False),
                                  style='Resume.TButton')
            btn_short.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
            
            btn_long = ttk.Button(button_frame, text="☕ Długa przerwa (15 min)", 
                                 command=lambda: self.start_break(dialog, True),
                                 style='Resume.TButton')
            btn_long.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
            
            btn_postpone = ttk.Button(button_frame, text="⏰ Przełóż przerwę", 
                                     command=lambda: self.postpone_break(dialog),
                                     style='Pause.TButton')
            btn_postpone.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
        else:
            info_label = ttk.Label(main_frame, text="Zrób przerwę!", 
                                  font=('Segoe UI', 12))
            info_label.pack(pady=(0, 20))
            
            # Przyciski w układzie pionowym
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(pady=10)
            
            # Konfiguracja grid dla przycisków
            button_frame.columnconfigure(0, weight=1)
            
            btn_break = ttk.Button(button_frame, text="☕ Przerwa (5 min)", 
                                  command=lambda: self.start_break(dialog, False),
                                  style='Resume.TButton')
            btn_break.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
            
            btn_postpone = ttk.Button(button_frame, text="⏰ Przełóż przerwę", 
                                     command=lambda: self.postpone_break(dialog),
                                     style='Pause.TButton')
            btn_postpone.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
    
    def start_break(self, dialog, is_long_break):
        """Rozpocznij przerwę"""
        if is_long_break:
            self.wykorzystana_dluga_przerwa = True
        self.przerwa_dluzsza = is_long_break
        self.licz_czas_od_ostatniej_przerwy = False
        self.licz_czas_przerwy = True
        self.czas_od_ostatniej_przerwy = 0
        self.czas_trwania_przerwy = 0
        # Zmień przycisk na "Anuluj przerwę"
        self.btn_manual_break.config(text='❌ ANULUJ PRZERWĘ', style='Close.TButton')
        # Wyszarz przycisk pauzy gdy jest przerwa
        self.btn_wstrzymaj_czas_pracy.config(state='disabled')
        # Aktualizuj ikonę w tray
        if hasattr(self, 'icon') and self.icon:
            self.update_tray_icon()
        dialog.destroy()
    
    def postpone_break(self, dialog):
        """Przełóż przerwę - kontynuuj pracę"""
        # Resetujemy licznik czasu od ostatniej przerwy, żeby nie pokazywało się od razu ponownie
        self.czas_od_ostatniej_przerwy = 0
        dialog.destroy()
    
    def show_manual_break_dialog(self):
        """Pokaż okno dialogowe z pytaniem o długą przerwę dla ręcznej przerwy"""
        # Tworzymy własne okno dialogowe
        dialog = tk.Toplevel(root)
        dialog.title("PRZERWA")
        dialog.geometry("250x300")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()
        
        # Ustawienie koloru tła takiego samego jak główne okno
        dialog.configure(bg='#f0f0f0')
        
        # Ustawienie okna zawsze na pierwszym planie
        dialog.attributes('-topmost', True)
        
        # Centrowanie okna
        dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))
        
        # Główny kontener z paddingiem
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        title_label = ttk.Label(main_frame, text="☕ Ręczna przerwa", 
                               font=('Segoe UI', 16, 'bold'), 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Pytanie
        info_label = ttk.Label(main_frame, text="Czy to ma być długa przerwa?", 
                              font=('Segoe UI', 12))
        info_label.pack(pady=(0, 20))
        
        # Przyciski w układzie pionowym
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Konfiguracja grid dla przycisków
        button_frame.columnconfigure(0, weight=1)
        
        btn_short = ttk.Button(button_frame, text="☕ Krótka przerwa (5 min)", 
                              command=lambda: self.start_manual_break(dialog, False),
                              style='Resume.TButton')
        btn_short.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
        
        btn_long = ttk.Button(button_frame, text="☕ Długa przerwa (15 min)", 
                             command=lambda: self.start_manual_break(dialog, True),
                             style='Resume.TButton')
        btn_long.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
        
        btn_cancel = ttk.Button(button_frame, text="❌ Anuluj", 
                               command=dialog.destroy,
                               style='Close.TButton')
        btn_cancel.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E), padx=10)
    
    def start_manual_break(self, dialog, is_long_break):
        """Rozpocznij ręczną przerwę"""
        if is_long_break:
            self.wykorzystana_dluga_przerwa = True
        self.przerwa_dluzsza = is_long_break
        
        # Uruchom przerwę - NIE zatrzymuj liczenia czasu pracy (jak automatyczna przerwa)
        self.licz_czas_od_ostatniej_przerwy = False
        self.licz_czas_przerwy = True
        self.czas_od_ostatniej_przerwy = 0
        self.czas_trwania_przerwy = 0
        # Zmień przycisk na "Anuluj przerwę"
        self.btn_manual_break.config(text='❌ ANULUJ PRZERWĘ', style='Close.TButton')
        # Wyszarz przycisk pauzy gdy jest przerwa
        self.btn_wstrzymaj_czas_pracy.config(state='disabled')
        # Aktualizuj ikonę w tray
        if hasattr(self, 'icon') and self.icon:
            self.update_tray_icon()
        
        dialog.destroy()

    def manual_break(self):
        """Ręczne uruchomienie przerwy - działa jak automatyczna przerwa po 1h"""
        if self.licz_czas_pracy and not self.licz_czas_przerwy:  # Jeśli pracujemy i nie jesteśmy na przerwie
            if not self.wykorzystana_dluga_przerwa:
                # Użyj stylowego okna dialogowego zamiast messagebox
                self.show_manual_break_dialog()
            else:
                # Długa przerwa już była wykorzystana, więc automatycznie krótka przerwa
                self.przerwa_dluzsza = False
                # Uruchom przerwę - NIE zatrzymuj liczenia czasu pracy (jak automatyczna przerwa)
                self.licz_czas_od_ostatniej_przerwy = False
                self.licz_czas_przerwy = True
                self.czas_od_ostatniej_przerwy = 0
                self.czas_trwania_przerwy = 0
                # Zmień przycisk na "Anuluj przerwę"
                self.btn_manual_break.config(text='❌ ANULUJ PRZERWĘ', style='Close.TButton')
                # Wyszarz przycisk pauzy gdy jest przerwa
                self.btn_wstrzymaj_czas_pracy.config(state='disabled')
            
        elif self.licz_czas_przerwy:  # Jeśli jesteś na przerwie - anuluj przerwę
            # Dodaj czas przerwy do sumy przed anulowaniem
            self.suma_przerw_sekundy += self.czas_trwania_przerwy
            # Anuluj przerwę - wróć do pracy
            self.licz_czas_od_ostatniej_przerwy = True
            self.licz_czas_przerwy = False
            self.czas_od_ostatniej_przerwy = 1  # Ustaw na 1, żeby nie resetować całkowicie
            self.czas_trwania_przerwy = 0
            # Zmień przycisk z powrotem na "Przerwa"
            self.btn_manual_break.config(text='☕ PRZERWA', style='Resume.TButton')
            # Odblokuj przycisk pauzy gdy anulujesz przerwę
            self.btn_wstrzymaj_czas_pracy.config(state='normal')
            # Aktualizuj ikonę w tray
            if hasattr(self, 'icon') and self.icon:
                self.update_tray_icon()
    
    def wyslij_wiadomosc_na_telegram(self):
        # Oblicz pozostały czas pracy
        if self.pozostalo_pracy.total_seconds() > 0:
            pozostalo_tekst = str(self.pozostalo_pracy)
        else:
            pozostalo_tekst = "0:00:00"
        
        self.wiadomosc = (f"☕ Czas wracać do pracy!\n\n"
                         f"⏰ Pozostało pracy: {pozostalo_tekst}\n"
                         f"🏁 Koniec pracy o: {str(self.koniec_pracy)}")
        self.url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={self.wiadomosc}"
        print(requests.get(self.url).json())

    def show_close_dialog(self):
        """Pokaż okno dialogowe potwierdzenia zamknięcia"""
        # Tworzymy własne okno dialogowe
        dialog = tk.Toplevel(root)
        dialog.title("ZAMKNIJ PROGRAM")
        dialog.geometry("400x190")
        dialog.resizable(False, False)
        dialog.transient(root)
        dialog.grab_set()
        
        # Ustawienie koloru tła takiego samego jak główne okno
        dialog.configure(bg='#f0f0f0')
        
        # Ustawienie okna zawsze na pierwszym planie
        dialog.attributes('-topmost', True)
        
        # Centrowanie okna
        dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))
        
        # Wymuś wyświetlenie okna
        dialog.lift()
        dialog.focus_set()
        
        # Główny kontener z paddingiem
        main_frame = ttk.Frame(dialog, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tytuł
        title_label = ttk.Label(main_frame, text="❌ Zamknąć program?", 
                               font=('Segoe UI', 14, 'bold'), 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 10))
        
        # Pytanie
        info_label = ttk.Label(main_frame, text="Czy na pewno chcesz zamknąć program?\nWszystkie dane zostaną zapisane.", 
                              font=('Segoe UI', 11))
        info_label.pack(pady=(0, 15))
        
        # Przyciski w układzie poziomym
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        # Konfiguracja grid dla przycisków
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        btn_yes = ttk.Button(button_frame, text="✅ TAK, ZAMKNIJ", 
                            command=lambda: self.confirm_close(dialog),
                            style='Close.TButton')
        btn_yes.grid(row=0, column=0, pady=5, padx=(0, 5), sticky=(tk.W, tk.E))
        
        btn_no = ttk.Button(button_frame, text="❌ NIE, ANULUJ", 
                           command=dialog.destroy,
                           style='Resume.TButton')
        btn_no.grid(row=0, column=1, pady=5, padx=(5, 0), sticky=(tk.W, tk.E))
    
    def confirm_close(self, dialog):
        """Potwierdź zamknięcie programu"""
        self.zapis_do_pliku()
        dialog.destroy()
        root.destroy()
        sys.exit()

    def wyjscie_z_programu(self):
        """Wywołaj okno potwierdzenia zamknięcia"""
        self.show_close_dialog()  

    def zapisz_nowy_dzien_csv(self):
        """Zapisz nowy dzień do pliku CSV"""
        dzisiejsza_data = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Sprawdź czy plik CSV istnieje
        file_exists = os.path.exists("dane.csv")
        
        with open("dane.csv", 'a', newline='', encoding='utf-8') as file_write:
            fieldnames = ['Data', 'Czas_startu', 'Sekund_pracy', 'Wykorzystana_dluga_przerwa', 'Czas_od_ostatniej_przerwy', 'Suma_przerw_sekundy']
            writer = csv.DictWriter(file_write, fieldnames=fieldnames)
            
            # Napisz nagłówek tylko jeśli plik nie istnieje
            if not file_exists:
                writer.writeheader()
            
            # Zapisz nowy wiersz
            writer.writerow({
                'Data': dzisiejsza_data,
                'Czas_startu': self.stempel_czasowy_startu_pracy.strftime('%H:%M:%S'),
                'Sekund_pracy': str(self.sekund_pracy_dzis),
                'Wykorzystana_dluga_przerwa': str(self.wykorzystana_dluga_przerwa),
                'Czas_od_ostatniej_przerwy': str(self.czas_od_ostatniej_przerwy),
                'Suma_przerw_sekundy': str(self.suma_przerw_sekundy)
            })

    def zapis_do_pliku(self):
        dzisiejsza_data = datetime.datetime.now().strftime('%Y-%m-%d')
        
        # Odczytaj wszystkie dane z CSV
        rows = []
        if os.path.exists("dane.csv"):
            with open("dane.csv", 'r', newline='', encoding='utf-8') as file_read:
                reader = csv.DictReader(file_read)
                rows = list(reader)
        
        # Znajdź i zaktualizuj dzisiejszy wpis
        znaleziono = False
        for row in rows:
            if row['Data'] == dzisiejsza_data:
                row['Sekund_pracy'] = str(self.sekund_pracy_dzis)
                row['Wykorzystana_dluga_przerwa'] = str(self.wykorzystana_dluga_przerwa)
                row['Czas_od_ostatniej_przerwy'] = str(self.czas_od_ostatniej_przerwy)
                row['Suma_przerw_sekundy'] = str(self.suma_przerw_sekundy)
                znaleziono = True
                break
        
        # Zapisz zaktualizowane dane
        with open("dane.csv", 'w', newline='', encoding='utf-8') as file_write:
            fieldnames = ['Data', 'Czas_startu', 'Sekund_pracy', 'Wykorzystana_dluga_przerwa', 'Czas_od_ostatniej_przerwy', 'Suma_przerw_sekundy']
            writer = csv.DictWriter(file_write, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def pokaz_okno(self):
        # Zatrzymaj ikonę w tray
        if hasattr(self, 'icon') and self.icon:
            try:
                self.icon.stop()
                time.sleep(0.1)  # Daj czas na zatrzymanie
            except:
                pass
        root.deiconify()
    
    def update_tray_icon(self):
        """Aktualizuj ikonę w tray na podstawie aktualnego stanu"""
        # Zatrzymaj starą ikonę jeśli istnieje
        if hasattr(self, 'icon') and self.icon:
            try:
                self.icon.stop()
                # Daj czas na zatrzymanie
                time.sleep(0.1)
            except:
                pass
        
        # Logika ikon: ikona pauzy gdy jest przerwa, ikona play gdy pracujesz
        if self.licz_czas_przerwy:
            # Jest przerwa - ikona pauzy
            self.icon = pystray.Icon("CzasPracy", self.ikona_pauza, "Przerwa aktywna", self.menu)
            self.icon_thread = threading.Thread(daemon=True, target=lambda: self.icon.run())
            self.icon_thread.start()
        elif self.licz_czas_pracy:
            # Pracujesz - ikona play
            self.icon = pystray.Icon("CzasPracy", self.ikona_play, "Czas pracy aktywny", self.menu)
            self.icon_thread = threading.Thread(daemon=True, target=lambda: self.icon.run())
            self.icon_thread.start()
        else:
            # Praca wstrzymana - ikona pauzy
            self.icon = pystray.Icon("CzasPracy", self.ikona_pauza, "Czas pracy wstrzymany", self.menu)
            self.icon_thread = threading.Thread(daemon=True, target=lambda: self.icon.run())
            self.icon_thread.start()

    def minimalizuj_do_traya(self):
        root.withdraw()
        # Użyj funkcji update_tray_icon() żeby uniknąć duplikowania kodu
        self.update_tray_icon()
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