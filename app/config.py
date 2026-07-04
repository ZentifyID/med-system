"""Центральная конфигурация приложения.

Все пути и настройки — в одном месте. При переходе на сетевую БД
(PostgreSQL) достаточно будет поменять настройки только здесь.
"""
import sys
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))

if FROZEN:
    # Скомпилированный .exe: данные (БД) лежат рядом с exe,
    # ресурсы (иконки) PyInstaller распаковывает во временную папку _MEIPASS
    BASE_DIR = Path(sys.executable).parent
    RESOURCE_DIR = Path(sys._MEIPASS)
else:
    # Запуск из исходников: всё в корне проекта
    BASE_DIR = Path(__file__).resolve().parent.parent
    RESOURCE_DIR = BASE_DIR

DB_PATH = BASE_DIR / "med_system.db"
ICONS_DIR = RESOURCE_DIR / "assets" / "icons"

# ── Окно ─────────────────────────────────────────────────────────────
APP_TITLE = "Med System"
WINDOW_GEOMETRY = "1280x820"
WINDOW_MIN_SIZE = (1024, 640)

# ── Эффекты окна (стиль macOS) ───────────────────────────────────────
# Цветной заголовок окна через pywinstyles (Windows).
# Если мешает — поставить False.
ENABLE_WINDOW_EFFECTS = True

# ── Бизнес-правила ───────────────────────────────────────────────────
# Порог "мало лекарства" (штук)
LOW_QUANTITY_THRESHOLD = 5
# За сколько дней предупреждать об истечении сроков
EXPIRY_WARNING_DAYS = 14
# Дата автоматического перевода групп на следующий курс (месяц, день)
ACADEMIC_YEAR_ROLLOVER = (8, 15)
