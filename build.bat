@echo off
echo Установка зависимостей (PyInstaller, customtkinter, Pillow)...
pip install pyinstaller customtkinter pillow

echo.
echo Сборка проекта в EXE файл...
pyinstaller --noconfirm --onedir --windowed --name "MedSystem" --add-data "assets;assets" --collect-all customtkinter main.py

echo.
echo Сборка завершена!
echo Ваш файл находится в папке: dist\MedSystem\MedSystem.exe
pause
