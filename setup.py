"""
setup.py
---------
One-click pipeline runner for Amazon India Analytics.
Runs: Data Generation → Cleaning → EDA (20 charts) → SQL DB Setup

Usage:
    python setup.py
"""

import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def banner(msg):
    print("\n" + "═"*60)
    print(f"  {msg}")
    print("═"*60)

def main():
    start = time.time()

    print("""
╔══════════════════════════════════════════════════════════╗
║   🛒  AMAZON INDIA: A DECADE OF SALES ANALYTICS          ║
║   GUVI HCL · Fullstack Data Science Program              ║
║   Full Pipeline Setup                                    ║
╚══════════════════════════════════════════════════════════╝
""")

    # ── STEP 1: Generate Data ─────────────────────────────────────────────────
    banner("STEP 1 / 4 — Generating Synthetic Dataset (80,000 transactions)")
    from utils.data_generator import make_transactions, make_catalog
    raw = make_transactions()
    cat = make_catalog()
    print(f"   ✅  Transactions : {len(raw):,} rows × {raw.shape[1]} columns")
    print(f"   ✅  Product Catalog: {len(cat):,} products")

    # ── STEP 2: Clean Data ────────────────────────────────────────────────────
    banner("STEP 2 / 4 — Running 10-Challenge Cleaning Pipeline")
    from data_cleaning.cleaning_pipeline import run_pipeline, save_cleaning_report, save_cleaned_csv
    clean, report = run_pipeline(raw, verbose=True)
    save_cleaning_report(report)
    save_cleaned_csv(clean)
    print(f"   ✅  Clean shape: {clean.shape[0]:,} rows × {clean.shape[1]} columns")

    # ── STEP 3: EDA Visualizations ────────────────────────────────────────────
    banner("STEP 3 / 4 — Generating 20 EDA Visualizations")
    from eda.eda_visualizations import run_all
    paths = run_all(clean)
    print(f"   ✅  {len(paths)} charts saved to outputs/eda/")

    # ── STEP 4: SQL Database ──────────────────────────────────────────────────
    banner("STEP 4 / 4 — Setting Up SQLite Database")
    from sql.db_integration import setup_db, export_schema
    conn = setup_db(clean, cat)
    export_schema()
    conn.close()

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed = time.time() - start
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  ✅  SETUP COMPLETE  ({elapsed:.1f}s)
║                                                          ║
║  📁  outputs/eda/          → 20 EDA charts (PNG)         ║
║  📁  outputs/              → cleaned dataset + reports   ║
║  🗄️   amazon_india.db       → SQLite database             ║
║                                                          ║
║  🚀  NEXT STEP — Launch Dashboard:                       ║
║     streamlit run dashboard/streamlit_app.py             ║
╚══════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    main()
