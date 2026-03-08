@echo off
REM ============================================================
REM  build.bat — Compilation de Cursor en .exe standalone
REM  Prérequis : pip install -r requirements.txt pyinstaller
REM ============================================================

echo [Cursor Build] Installation des dependances Python...
pip install -r requirements.txt
pip install pyinstaller

echo [Cursor Build] Compilation avec PyInstaller...
pyinstaller ^
    --onefile ^
    --noconsole ^
    --name Cursor ^
    --icon assets\icon.ico ^
    --add-data "assets;assets" ^
    main.py

echo [Cursor Build] Termine ! Executable disponible dans le dossier dist\
pause
