@echo off
chcp 65001 >nul
setlocal

rem ── Ищем Python: сначала py-launcher, потом python ──────────────────
set "PY=py -3"
%PY% --version >nul 2>&1
if errorlevel 1 (
    set "PY=python"
    %PY% --version >nul 2>&1
)
if errorlevel 1 (
    echo [ОШИБКА] Python не найден. Установите его с https://www.python.org/downloads/
    echo При установке отметьте галочку "Add Python to PATH".
    pause
    exit /b 1
)

echo Используется:
%PY% --version

echo.
echo [1/2] Установка зависимостей...
rem Через "python -m pip" — работает даже если pip/pyinstaller нет в PATH
%PY% -m pip install --upgrade pip >nul
%PY% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo [ОШИБКА] Не удалось установить зависимости. Проверьте интернет.
    pause
    exit /b 1
)

echo.
echo [2/2] Сборка EXE...
rem "python -m PyInstaller" вместо "pyinstaller" — не зависит от PATH
%PY% -m PyInstaller --noconfirm --onedir --windowed --name "MedSystem" ^
    --add-data "assets;assets" --collect-all customtkinter main.py
if errorlevel 1 (
    echo [ОШИБКА] Сборка не удалась. Текст ошибки выше.
    pause
    exit /b 1
)

echo.
echo ────────────────────────────────────────────────────────────
echo Готово! Приложение собрано в папке: dist\MedSystem\
echo.
echo Для установки на другой компьютер (Python там НЕ нужен):
echo   1. Скопируйте ВСЮ папку dist\MedSystem на целевой ПК
echo   2. Запустите MedSystem.exe
echo   3. База med_system.db создастся сама рядом с exe
echo ────────────────────────────────────────────────────────────
pause
