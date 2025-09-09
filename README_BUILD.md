# Budowanie aplikacji Czas Pracy

## Krok 1: Przygotowanie środowiska

1. **Zainstaluj Python** (jeśli nie masz):
   - Pobierz z https://python.org
   - Podczas instalacji zaznacz "Add Python to PATH"

2. **Zainstaluj wymagane biblioteki**:
   ```bash
   pip install -r requirements.txt
   ```

## Krok 2: Budowanie pliku exe

Uruchom skrypt budowania:
```bash
python build_exe.py
```

Skrypt automatycznie:
- Zainstaluje PyInstaller jeśli potrzeba
- Zbuduje plik exe w folderze `dist/`
- Wyczyści pliki tymczasowe

**Wynik**: Plik `dist/CzasPracy.exe`

## Krok 3: Dodanie do autostartu Windows

### Opcja A: Automatycznie (zalecane)
```bash
python setup_autostart.py
```

### Opcja B: Ręcznie

#### Metoda 1: Folder Startup
1. Naciśnij `Win + R`
2. Wpisz: `shell:startup`
3. Skopiuj `CzasPracy.exe` do tego folderu

#### Metoda 2: Rejestr Windows
1. Naciśnij `Win + R`
2. Wpisz: `regedit`
3. Przejdź do: `HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Run`
4. Utwórz nowy wpis:
   - Nazwa: `CzasPracy`
   - Wartość: `C:\ścieżka\do\CzasPracy.exe`

## Krok 4: Testowanie

1. **Uruchom aplikację**:
   ```bash
   dist/CzasPracy.exe
   ```

2. **Sprawdź autostart**:
   - Zrestartuj komputer
   - Aplikacja powinna uruchomić się automatycznie

## Usuwanie z autostartu

```bash
python setup_autostart.py --remove
```

## Rozwiązywanie problemów

### Błąd: "Nie znaleziono pliku exe"
- Upewnij się, że uruchomiłeś `build_exe.py`
- Sprawdź czy plik `dist/CzasPracy.exe` istnieje

### Błąd: "Brak wymaganych bibliotek"
```bash
pip install winshell pywin32
```

### Aplikacja nie uruchamia się automatycznie
- Sprawdź folder Startup: `Win + R` → `shell:startup`
- Sprawdź rejestr: `Win + R` → `regedit`
- Uruchom jako administrator

### Błąd PyInstaller
```bash
pip install --upgrade pyinstaller
```

## Struktura plików

```
czas_pracy/
├── czas_pracy.py          # Główna aplikacja
├── ready.png              # Ikona play
├── pause.png              # Ikona pause
├── dane.csv               # Dane aplikacji
├── build_exe.py           # Skrypt budowania
├── setup_autostart.py     # Skrypt autostartu
├── requirements.txt       # Wymagane biblioteki
└── dist/
    └── CzasPracy.exe      # Gotowy plik exe
```

## Funkcje aplikacji

- ⏰ **Kontrola czasu pracy** - 8 godzin dziennie
- ☕ **Automatyczne przerwy** - co godzinę
- 📊 **Statystyki** - suma przerw, czas pracy
- 🔔 **Powiadomienia** - Telegram
- 📱 **Tray** - minimalizacja do system tray
- 💾 **Zapisywanie** - dane w pliku CSV
- 🎨 **Nowoczesny interfejs** - profesjonalny wygląd

## Wsparcie

W przypadku problemów:
1. Sprawdź logi w konsoli
2. Upewnij się, że wszystkie pliki są w tym samym folderze
3. Sprawdź uprawnienia administratora
