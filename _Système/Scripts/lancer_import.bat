@echo off
cd /d "%~dp0"

:: Vérifier que Python est disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  Python n'est pas installe ou pas dans le PATH.
    echo  Telechargez Python sur : https://www.python.org
    echo.
    pause
    exit /b 1
)

:: Vérifier / installer les dépendances
for %%p in (pdfplumber Pillow ttkbootstrap) do (
    python -c "import %%p" >nul 2>&1
    if errorlevel 1 (
        echo  Installation de %%p...
        pip install %%p
    )
)

:: Lancer le script
python import_releves.py
