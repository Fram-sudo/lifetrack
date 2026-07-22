@echo off
cd /d "%~dp0"

:: Verifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python n'est pas installe ou pas dans le PATH.
    echo  Telechargez Python sur : https://www.python.org
    echo  ^(coche bien "Add Python to PATH" a l'installation^)
    echo.
    pause
    exit /b 1
)

:: Verifier tkinter (inclus par defaut avec Python sur Windows)
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Le module tkinter est manquant dans ton installation Python.
    echo  Reinstalle Python depuis https://www.python.org en gardant
    echo  l'option "tcl/tk and IDLE" cochee.
    echo.
    pause
    exit /b 1
)

:: Lancer le script
python import_hevy.py
