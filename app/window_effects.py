"""Эффекты окна в стиле macOS: полупрозрачность и цвет заголовка.

Использует pywinstyles (только Windows 11). Если библиотеки нет или
система не поддерживает — молча пропускается, приложение работает
как обычно. Настройки — в app/config.py.
"""
import sys
import tkinter as tk

from app import config
from app.ui import BG_SIDEBAR, SIDEBAR_BORDER


def apply_window_effects(root: tk.Tk) -> None:
    if not config.ENABLE_WINDOW_EFFECTS:
        return
    if not sys.platform.startswith("win"):
        return
    try:
        import pywinstyles
    except ImportError:
        return

    try:
        # Заголовок окна в цвет сайдбара — единая «шапка», как в macOS
        pywinstyles.change_header_color(root, BG_SIDEBAR)
        pywinstyles.change_border_color(root, SIDEBAR_BORDER)
        pywinstyles.change_title_color(root, "#1D1D1F")
    except Exception:
        pass

    try:
        # Acrylic-размытие фона окна — только Windows 11 (build 22000+)
        if sys.getwindowsversion().build >= 22000:
            pywinstyles.apply_style(root, "acrylic")
            # Лёгкая полупрозрачность всего окна для эффекта «материала»
            root.attributes("-alpha", config.WINDOW_ALPHA)
    except Exception:
        pass
