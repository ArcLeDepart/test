@echo off
REM ============================================================
REM  build.bat — Compilation de Cursor en .exe standalone
REM  Détecte automatiquement Python même si le PATH est mal configuré
REM ============================================================

echo.
echo ========================================
echo   Cursor - Build Script
echo ========================================
echo.

REM --- Détection automatique de Python ---
set "PYTHON_EXE="

REM Essai 1 : commande "py" (Python Launcher Windows)
where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_EXE=py"
    goto :found
)

REM Essai 2 : commande "python"
where python >nul 2>&1
if %errorlevel%==0 (
    REM Vérifier que ce n'est pas le faux alias Microsoft Store
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_EXE=python"
        goto :found
    )
)

REM Essai 3 : Chemins courants d'installation
for %%P in (
    "%LOCALAPPDATA%\Python\bin\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
) do (
    if exist %%P (
        set "PYTHON_EXE=%%~P"
        goto :found
    )
)

REM Python non trouvé
echo [ERREUR] Python n'a pas ete trouve sur ce systeme !
echo.
echo Installez Python depuis https://www.python.org/downloads/
echo IMPORTANT : Cochez "Add python.exe to PATH" pendant l'installation !
echo.
pause
exit /b 1

:found
echo [OK] Python trouve : %PYTHON_EXE%
%PYTHON_EXE% --version
echo.

REM --- Installation des dépendances ---
echo [1/3] Installation des dependances...
%PYTHON_EXE% -m pip install --upgrade pip >nul 2>&1
%PYTHON_EXE% -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)
echo [OK] Dependances installees.
echo.

REM --- Installation de PyInstaller ---
echo [2/3] Installation de PyInstaller...
%PYTHON_EXE% -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'installation de PyInstaller.
    pause
    exit /b 1
)
echo [OK] PyInstaller installe.
echo.

REM --- Compilation ---
echo [3/3] Compilation de Cursor.exe...
%PYTHON_EXE% -m PyInstaller ^
    --onefile ^
    --noconsole ^
    --name Cursor ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [ERREUR] La compilation a echoue.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   [OK] Compilation reussie !
echo   Executable : dist\Cursor.exe
echo ========================================
echo.
pause
