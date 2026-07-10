from __future__ import annotations

from pathlib import Path

from . import PROJECT_ROOT

CSV_DIR = PROJECT_ROOT / "csv"
EXPORT_DIR = PROJECT_ROOT / "plc_export"
CONTEXT_DIR = EXPORT_DIR / "context"
ST_DIR = EXPORT_DIR / "st"
LADDER_DIR = EXPORT_DIR / "ladder"
LADDER_AI_DIR = EXPORT_DIR / "ladder_ai"
PDF_CANDIDATES = (PROJECT_ROOT / "12314.pdf", PROJECT_ROOT / "12314_extracted.txt")
ENV_FILE = PROJECT_ROOT / ".env"
