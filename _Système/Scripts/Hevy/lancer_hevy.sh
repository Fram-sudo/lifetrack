#!/bin/bash
cd "$(dirname "$0")"

# Vérifier Python 3
if ! command -v python3 &>/dev/null; then
    zenity --error --text="Python3 n'est pas installé.\nInstallez-le avec :\n\nsudo apt install python3" 2>/dev/null \
    || echo "Python3 n'est pas installé. Lancez : sudo apt install python3"
    exit 1
fi

# Vérifier tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    zenity --error --text="Le module tkinter est manquant.\nInstallez-le avec :\n\nsudo apt install python3-tk" 2>/dev/null \
    || (echo ""; echo "  ❌ tkinter manquant."; echo "  Installez-le avec : sudo apt install python3-tk"; echo ""; read -p "Appuyez sur Entrée...")
    exit 1
fi

# Lancer le script
python3 import_hevy.py
