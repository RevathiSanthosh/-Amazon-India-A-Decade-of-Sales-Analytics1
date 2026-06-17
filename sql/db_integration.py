"""
sql/db_integration.py
----------------------
SQLite schema creation, data loading, indexing,
and a full library of dashboard-ready queries.

Run standalone:
    python sql/db_integration.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from config.settings import DB_PATH, SQL_DIR


# ══════════════════════════════════════════════════════════════════════════════
# DDL
# ══════════════════════════════════════════════════════════════════════════════

_DDL = """
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id          TEXT PRIMARY KEY,
    customer_id             TEXT NOT NULL,
    product_id              TEXT,
    order_date              TEXT,
    order_year              INTEGER,
    order_month             INTEGER,
    order_quarter           INTEGER,
    order_week              INTEGER,
    is_weekend              INTEGER DEFAULT 0,
    product_name            TEXT,
    category                TEXT,
    subcategory             TEXT,
    brand                   TEXT,
    product_rating          REAL,
    original_price_inr      REAL,
    discount_percent        REAL,
    final_amount_inr        REAL,
    delivery_charges        REAL,
    customer_city           TEXT,
    customer_state          TEXT,
    city_tier               TEXT,
    age_group               TEXT,
    is_prime_member         INTEGER DEFAULT 0,
    is_prime_eligible       INTEGER DEFAULT 0,
    is_festival_sale        INTEGER DEFAULT 0,
    festival_name           TEXT,
    payment_method          TEXT,
    delivery_days           INTEGER,
    return_status           TEXT,
    customer_rating         REAL,
    customer_spending_tier  TEXT,
    is_bulk_order           INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
    product_id          TEXT PRIMARY KEY,
    product_name        TEXT,
    category            TEXT,
    subcategory         TEXT,
    brand               TEXT,
    base_price_2015     REAL,
    weight_kg           REAL,
    rating              REAL,
    is_prime_eligible   INTEGER DEFAULT 0,
    launch_year         INTEGER
);

CREATE TABLE IF NOT EXISTS time_dim (
    date_key    TEXT PRIMARY KEY,
    year        INTEGER,
    quarter     INTEGER,
    month       INTEGER,
    month_name  TEXT,
    week        INTEGER,
    day_of_week INTEGER,
    is_weekend  INTEGER,
    is_festival_month INTEGER
);
"""

_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_tx_cust   ON transactions(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_tx_prod   ON transactions(product_id);",
    "CREATE INDEX IF NOT EXISTS idx_tx_date   ON transactions(order_date);",
    "CREATE INDEX IF NOT EXISTS idx_tx_year   ON transactions(order_year);",
    "CREATE INDEX IF NOT EXISTS idx_tx_cat    ON transactions(category);",
    "CREATE INDEX IF NOT EXISTS idx_tx_city   ON transactions(customer_city);",
    "CREATE INDEX IF NOT EXISTS idx_tx_state  ON transactions(customer_state);",
    "CREATE INDEX IF NOT EXISTS idx_tx_pay    ON transactions(payment_method);",
    "CREATE INDEX IF NOT EXISTS idx_tx_prime  ON transactions(is_prime_member);",
    "CREATE INDEX IF NOT EXISTS idx_tx_fest   ON transactions(is_festival_sale);",
    "CREATE INDEX IF NOT EXISTS idx_tx_tier   ON transactions(customer_spending_tier);",
    "CREATE INDEX IF NOT EXISTS idx_prod_cat  ON products(category);",
    "CREATE INDEX IF NOT EXISTS idx_prod_brand ON products(brand);",
]


# ══════════════════════════════════════════════════════════════════════════════
# CONNECTION
# ══════════════════════════════════════════════════════════════════════════════

def get_conn(path: str = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA cache_size=-65536;")
    return conn


def create_schema(conn: sqlite3.Connection):
    for stmt in _DDL.strip().split(";"):
        s = stmt.strip()
        if s:
            conn.execute(s + ";")
    for idx in _INDEXES:
        conn.execute(idx)
    conn.commit()
    print("   ✓ Schema + indexes created")


# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════

def _bool_to_int(val) -> int:
    if isinstance(val, bool): return int(val)
    v = str(val).strip().lower()
    return 1 if v in {"true","1","yes","y"} else 0


def load_transactions(conn: sqlite3.Connection, df: pd.DataFrame, chunk: int = 10_000):
    keep = [c for c in [
        "transaction_id","customer_id","product_id","order_date","order_year",
        "order_month","order_quarter","order_week","is_weekend","product_name",
        "category","subcategory","brand","product_rating","original_price_inr",
        "discount_percent","final_amount_inr","delivery_charges","customer_city",
        "customer_state","city_tier","age_group","is_prime_member","is_prime_eligible",
        "is_festival_sale","festival_name","payment_method","delivery_days",
        "return_status","customer_rating","customer_spending_tier","is_bulk_order"
    ] if c in df.columns]

    load = df[keep].copy()

    for col in ["is_prime_member","is_prime_eligible","is_festival_sale",
                "is_weekend","is_bulk_order"]:
        if col in load.columns:
            load[col] = load[col].apply(_bool_to_int)

    for col in ["product_rating","original_price_inr","final_amount_inr",
                "delivery_charges","discount_percent","customer_rating"]:
        if col in load.columns:
            load[col] = pd.to_numeric(load[col], errors="coerce")

    conn.execute("DELETE FROM transactions;")
    conn.commit()

    total = len(load)
    for start in range(0, total, chunk):
        load.iloc[start:start+chunk].to_sql(
            "transactions", conn, if_exists="append", index=False)

    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    print(f"   ✓ transactions: {n:,} rows loaded")


def load_products(conn: sqlite3.Connection, df: pd.DataFrame):
    df.to_sql("products", conn, if_exists="replace", index=False)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"   ✓ products: {n:,} rows loaded")


def build_time_dim(conn: sqlite3.Connection):
    dates = pd.date_range("2015-01-01", "2025-12-31", freq="D")
    festival_months = {1,7,8,10,11}
    rows = [{"date_key": d.strftime("%Y-%m-%d"), "year": d.year, "quarter": d.quarter,
             "month": d.month, "month_name": d.strftime("%B"), "week": d.isocalendar()[1],
             "day_of_week": d.dayofweek, "is_weekend": int(d.dayofweek >= 5),
             "is_festival_month": int(d.month in festival_months)} for d in dates]
    conn.execute("DELETE FROM time_dim;")
    conn.executemany("""INSERT OR REPLACE INTO time_dim VALUES
        (:date_key,:year,:quarter,:month,:month_name,:week,:day_of_week,:is_weekend,:is_festival_month)
    """, rows)
    conn.commit()
    print(f"   ✓ time_dim: {len(rows):,} rows")


# ══════════════════════════════════════════════════════════════════════════════
# QUERY LIBRARY
# ══════════════════════════════════════════════════════════════════════════════

def Q(conn, sql, params=()):
    return pd.read_sql_query(sql, conn, params=params)


def kpis(conn):
    return Q(conn, """SELECT
        COUNT(*) orders, SUM(final_amount_inr) revenue,
        AVG(final_amount_inr) aov, COUNT(DISTINCT customer_id) customers,
        COUNT(DISTINCT product_id) products,
        ROUND(100.0*SUM(is_prime_member)/COUNT(*),1) prime_pct,
        ROUND(100.0*SUM(is_festival_sale)/COUNT(*),1) festival_pct
    FROM transactions""")


def yearly_revenue(conn):
    return Q(conn, """SELECT order_year year,
        SUM(final_amount_inr) revenue, COUNT(*) orders,
        COUNT(DISTINCT customer_id) customers, AVG(final_amount_inr) aov,
        AVG(discount_percent) avg_discount
    FROM transactions GROUP BY order_year ORDER BY order_year""")


def monthly_revenue(conn, year=None):
    where = f"WHERE order_year={year}" if year else ""
    return Q(conn, f"""SELECT order_year, order_month,
        SUM(final_amount_inr) revenue, COUNT(*) orders
    FROM transactions {where} GROUP BY order_year, order_month ORDER BY 1,2""")


def category_perf(conn):
    return Q(conn, """SELECT category,
        SUM(final_amount_inr) revenue, COUNT(*) orders,
        AVG(final_amount_inr) aov, AVG(product_rating) avg_rating,
        ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(),2) share_pct
    FROM transactions GROUP BY category ORDER BY revenue DESC""")


def brand_perf(conn, top=15):
    return Q(conn, f"""SELECT brand,
        SUM(final_amount_inr) revenue, COUNT(*) orders, AVG(product_rating) avg_rating
    FROM transactions GROUP BY brand ORDER BY revenue DESC LIMIT {top}""")


def city_perf(conn, top=15):
    return Q(conn, f"""SELECT customer_city city, customer_state state,
        city_tier tier, SUM(final_amount_inr) revenue,
        COUNT(*) orders, AVG(delivery_days) avg_delivery,
        AVG(final_amount_inr) aov
    FROM transactions GROUP BY customer_city ORDER BY revenue DESC LIMIT {top}""")


def prime_analysis(conn):
    return Q(conn, """SELECT
        CASE WHEN is_prime_member=1 THEN 'Prime' ELSE 'Non-Prime' END label,
        COUNT(DISTINCT customer_id) customers, COUNT(*) orders,
        AVG(final_amount_inr) aov, SUM(final_amount_inr) revenue
    FROM transactions GROUP BY is_prime_member""")


def payment_trend(conn):
    return Q(conn, """SELECT order_year, payment_method,
        COUNT(*) cnt,
        ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER (PARTITION BY order_year),2) share_pct
    FROM transactions GROUP BY order_year, payment_method ORDER BY 1,3 DESC""")


def festival_impact(conn):
    return Q(conn, """SELECT
        COALESCE(NULLIF(TRIM(festival_name),''),'Regular') festival,
        COUNT(*) orders, SUM(final_amount_inr) revenue,
        AVG(final_amount_inr) aov, AVG(discount_percent) avg_discount
    FROM transactions GROUP BY festival ORDER BY revenue DESC""")


def return_analysis(conn):
    return Q(conn, """SELECT category,
        COUNT(*) total,
        SUM(CASE WHEN return_status='Returned' THEN 1 ELSE 0 END) returned,
        ROUND(100.0*SUM(CASE WHEN return_status='Returned' THEN 1 ELSE 0 END)/COUNT(*),2) rate
    FROM transactions GROUP BY category ORDER BY rate DESC""")


def delivery_perf(conn):
    return Q(conn, """SELECT customer_city, city_tier,
        ROUND(AVG(delivery_days),1) avg_days, COUNT(*) orders,
        ROUND(100.0*SUM(CASE WHEN delivery_days<=3 THEN 1 ELSE 0 END)/COUNT(*),1) fast_pct
    FROM transactions WHERE delivery_days IS NOT NULL
    GROUP BY customer_city HAVING orders>30 ORDER BY avg_days""")


def age_behavior(conn):
    return Q(conn, """SELECT age_group,
        COUNT(DISTINCT customer_id) customers, COUNT(*) orders,
        AVG(final_amount_inr) aov, SUM(final_amount_inr) revenue
    FROM transactions GROUP BY age_group ORDER BY aov DESC""")


def rfm(conn):
    return Q(conn, """SELECT customer_id,
        JULIANDAY('now') - JULIANDAY(MAX(order_date))  recency_days,
        COUNT(*) frequency,
        SUM(final_amount_inr) monetary
    FROM transactions GROUP BY customer_id""")


def discount_effectiveness(conn):
    return Q(conn, """SELECT
        CASE
            WHEN discount_percent = 0 THEN '0%'
            WHEN discount_percent <= 10 THEN '1-10%'
            WHEN discount_percent <= 20 THEN '11-20%'
            WHEN discount_percent <= 30 THEN '21-30%'
            WHEN discount_percent <= 50 THEN '31-50%'
            ELSE '51%+'
        END disc_bucket,
        COUNT(*) orders, SUM(final_amount_inr) revenue, AVG(final_amount_inr) aov
    FROM transactions GROUP BY disc_bucket ORDER BY MIN(discount_percent)""")


def cohort_clv(conn):
    return Q(conn, """SELECT first_year cohort,
        COUNT(DISTINCT t.customer_id) customers,
        AVG(total_spend) avg_clv, MEDIAN(total_spend) median_clv
    FROM (SELECT customer_id, MIN(order_year) first_year FROM transactions GROUP BY customer_id) c
    JOIN (SELECT customer_id, SUM(final_amount_inr) total_spend FROM transactions GROUP BY customer_id) t
    ON c.customer_id=t.customer_id
    GROUP BY first_year ORDER BY first_year""")


def tier_revenue(conn):
    return Q(conn, """SELECT customer_spending_tier tier,
        COUNT(DISTINCT customer_id) customers, COUNT(*) orders,
        SUM(final_amount_inr) revenue, AVG(final_amount_inr) aov
    FROM transactions GROUP BY customer_spending_tier ORDER BY aov DESC""")


# ══════════════════════════════════════════════════════════════════════════════
# SETUP
# ══════════════════════════════════════════════════════════════════════════════

def setup_db(transactions_df: pd.DataFrame,
             products_df: pd.DataFrame,
             db_path: str = None) -> sqlite3.Connection:
    print("\n" + "═"*55)
    print("   🗄️   SQL DATABASE SETUP")
    print("═"*55)
    conn = get_conn(db_path)
    create_schema(conn)
    build_time_dim(conn)
    load_transactions(conn, transactions_df)
    load_products(conn, products_df)

    k = kpis(conn)
    print(f"\n   📊 Verification:")
    print(f"      Revenue : ₹{float(k['revenue'].iloc[0]):>15,.2f}")
    print(f"      Orders  : {int(k['orders'].iloc[0]):>15,}")
    print(f"      Customers: {int(k['customers'].iloc[0]):>14,}")
    print(f"      AOV     : ₹{float(k['aov'].iloc[0]):>15,.2f}")
    print("═"*55)
    print(f"   ✅  DB ready → {DB_PATH}\n")
    return conn


def export_schema():
    path = SQL_DIR / "schema.sql"
    path.write_text(_DDL + "\n\n" + "\n".join(_INDEXES))
    print(f"   💾 Schema exported → {path}")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    from utils.data_generator import make_transactions, make_catalog
    from data_cleaning.cleaning_pipeline import run_pipeline

    raw   = make_transactions()
    clean, _ = run_pipeline(raw)
    cat   = make_catalog()

    conn = setup_db(clean, cat)
    export_schema()

    print("\n── Sample: Yearly Revenue ──")
    print(yearly_revenue(conn).to_string(index=False))
    print("\n── Sample: Category Performance ──")
    print(category_perf(conn).to_string(index=False))
    conn.close()
    print("\n✅  SQL integration done!")
