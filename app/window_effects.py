"""Эффекты окна в стиле macOS: цветной заголовок и рамка.

Использует pywinstyles (Windows). Если библиотеки нет — молча
пропускается. Настройка — в app/config.py.

Примечание: acrylic/mica-размытие здесь сознательно НЕ используется:
в tkinter оно делает светлые области окна прозрачными и сквозь
приложение просвечивает содержимое экрана.
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
