import os
import ctypes
from pathlib import Path
from app.app import run_app

def load_fonts(font_dir: str) -> None:
    """Load all .ttf fonts from a directory for the current process on Windows."""
    if os.name != 'nt':
        return  # Only works for Windows

    font_path = Path(font_dir)
    if not font_path.exists():
        print(f"Font directory not found: {font_dir}")
        return

    # Constants for AddFontResourceExW
    FR_PRIVATE = 0x10
    
    # Load each .ttf file (recursive search)
    for font_file in font_path.rglob("*.ttf"):
        path_str = str(font_file.resolve())
        res = ctypes.windll.gdi32.AddFontResourceExW(path_str, FR_PRIVATE, 0)
        if res:
            print(f"Loaded font: {font_file.name}")
        else:
            print(f"Failed to load font: {font_file.name}")

if __name__ == "__main__":
    import sys
    # Если запущено как exe, PyInstaller распаковывает данные во временную папку _MEIPASS
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).parent.resolve()
        
    font_dir = base_path / "assets" / "fonts"
    load_fonts(str(font_dir))
    
    run_app()
