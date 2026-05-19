import os
import sys
from pathlib import Path
from app.app import run_app

if __name__ == "__main__":
    # Если запущено как exe, PyInstaller распаковывает данные во временную папку _MEIPASS
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.resolve()
        
    run_app()
