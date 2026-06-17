"""
config/settings.py
------------------
Central configuration for the Amazon India Analytics project.
All paths, constants, and visual theme are defined here.
"""

from pathlib import Path

# ── Project Paths ─────────────────────────────────────────────────────────────
ROOT        = Path(__file__).resolve().parent.parent
DATA_DIR    = ROOT / "data"
OUTPUT_DIR  = ROOT / "outputs"
EDA_DIR     = OUTPUT_DIR / "eda"
REPORT_DIR  = OUTPUT_DIR / "cleaning_reports"
SQL_DIR     = OUTPUT_DIR / "sql"
DB_PATH     = ROOT / "amazon_india.db"

for d in [DATA_DIR, OUTPUT_DIR, EDA_DIR, REPORT_DIR, SQL_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Dataset Config ────────────────────────────────────────────────────────────
YEARS           = list(range(2015, 2026))
SYNTHETIC_ROWS  = 80_000      # demo rows when real data absent
RANDOM_SEED     = 42

# ── Brand Palette (Amazon dark theme) ────────────────────────────────────────
PALETTE = {
    "orange":       "#FF9900",
    "light_orange": "#FEBD69",
    "dark_bg":      "#0F1923",
    "card_bg":      "#1A2332",
    "mid_bg":       "#232F3E",
    "border":       "#37475A",
    "text":         "#E8EAF0",
    "muted":        "#8899AA",
    "success":      "#00C853",
    "danger":       "#FF3D3D",
    "info":         "#2979FF",
    "purple":       "#AA44FF",
    "teal":         "#00BCD4",
}

# Plotly color sequences
CAT_COLORS = [
    "#FF9900","#00C853","#2979FF","#AA44FF","#FF3D3D",
    "#00BCD4","#FEBD69","#FF6F00","#43A047","#1565C0"
]

# ── Categories & Mappings ─────────────────────────────────────────────────────
CATEGORIES = ["Electronics","Fashion","Home & Kitchen","Books",
              "Sports","Beauty","Grocery","Toys"]

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun",
          "Jul","Aug","Sep","Oct","Nov","Dec"]

FESTIVAL_MONTHS = {10: "Diwali 🪔", 7: "Prime Day ⭐",
                   1: "Republic Day 🇮🇳", 8: "Independence Day 🇮🇳",
                   11: "Big Billion 🔥"}
