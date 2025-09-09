#!/usr/bin/env python3
"""
Skrypt do budowania pliku exe z aplikacji Czas Pracy
Używa PyInstaller do stworzenia pojedynczego pliku exe
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Zainstaluj PyInstaller jeśli nie jest zainstalowany"""
    try:
        import PyInstaller
        print("✅ PyInstaller już zainstalowany")
    except ImportError:
        print("📦 Instaluję PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller zainstalowany")

def build_exe():
    """Zbuduj plik exe"""
    print("🔨 Buduję plik exe...")
    
    # Sprawdź czy plik główny istnieje
    if not os.path.exists("czas_pracy.py"):
        print("❌ Błąd: Nie znaleziono pliku czas_pracy.py")
        return False
    
    # Sprawdź czy pliki ikon istnieją
    if not os.path.exists("ready.png") or not os.path.exists("pause.png"):
        print("❌ Błąd: Nie znaleziono plików ikon (ready.png, pause.png)")
        return False
    
    # Komenda PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Pojedynczy plik exe
        "--windowed",                   # Bez konsoli (GUI)
        "--name=CzasPracy",             # Nazwa pliku exe
        "--icon=ready.png",             # Ikona aplikacji
        "--add-data=ready.png;.",       # Dodaj pliki ikon
        "--add-data=pause.png;.",       # Dodaj pliki ikon
        "--hidden-import=pystray",      # Ukryte importy
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=threading",
        "--hidden-import=datetime",
        "--hidden-import=csv",
        "--hidden-import=requests",
        "czas_pracy.py"
    ]
    
    try:
        # Uruchom PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Plik exe został pomyślnie utworzony!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas budowania: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

def cleanup():
    """Wyczyść pliki tymczasowe"""
    print("🧹 Czyszczę pliki tymczasowe...")
    
    # Usuń foldery tymczasowe
    temp_dirs = ["build", "__pycache__"]
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"   Usunięto: {dir_name}")
    
    # Usuń pliki tymczasowe
    temp_files = ["CzasPracy.spec"]
    for file_name in temp_files:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"   Usunięto: {file_name}")

def main():
    """Główna funkcja"""
    print("🚀 Budowanie aplikacji Czas Pracy...")
    print("=" * 50)
    
    # Zainstaluj PyInstaller
    install_pyinstaller()
    
    # Zbuduj exe
    if build_exe():
        print("\n✅ Budowanie zakończone pomyślnie!")
        print("📁 Plik exe znajduje się w folderze: dist/CzasPracy.exe")
        
        # Wyczyść pliki tymczasowe
        cleanup()
        
        print("\n🎉 Gotowe! Możesz teraz:")
        print("1. Skopiować dist/CzasPracy.exe do wybranego folderu")
        print("2. Uruchomić setup_autostart.py aby dodać do autostartu")
        
    else:
        print("\n❌ Budowanie nie powiodło się!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
