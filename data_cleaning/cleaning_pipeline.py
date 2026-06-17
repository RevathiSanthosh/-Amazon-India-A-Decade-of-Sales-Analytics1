"""
data_cleaning/cleaning_pipeline.py
------------------------------------
All 10 data-cleaning challenges — production-ready with detailed
per-question reports saved to outputs/cleaning_reports/.

Run standalone:
    python data_cleaning/cleaning_pipeline.py
"""

import sys, os, re, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from pathlib import Path
from config.settings import REPORT_DIR, OUTPUT_DIR


# ══════════════════════════════════════════════════════════════════════════════
# Q1 — DATE STANDARDIZATION
# ══════════════════════════════════════════════════════════════════════════════

def clean_dates(series: pd.Series) -> tuple[pd.Series, dict]:
    """Standardize order_date to YYYY-MM-DD. Returns (cleaned_series, report)."""
    counts = {"dmy_slash": 0, "dmy_dash": 0, "iso": 0, "invalid": 0, "null": 0}

    def _parse(val):
        if pd.isnull(val):
            counts["null"] += 1
            return pd.NaT

        s = str(val).strip()

        # DD/MM/YYYY
        m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
        if m:
            d, mo, yr = int(m[1]), int(m[2]), int(m[3])
            if 1 <= d <= 31 and 1 <= mo <= 12:
                try:
                    counts["dmy_slash"] += 1
                    return pd.Timestamp(yr, mo, d)
                except ValueError:
                    pass
            counts["invalid"] += 1
            return pd.NaT

        # DD-MM-YY
        m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{2})$", s)
        if m:
            d, mo, yr = int(m[1]), int(m[2]), int(m[3]) + (2000 if int(m[3]) <= 30 else 1900)
            if 1 <= d <= 31 and 1 <= mo <= 12:
                try:
                    counts["dmy_dash"] += 1
                    return pd.Timestamp(yr, mo, d)
                except ValueError:
                    pass
            counts["invalid"] += 1
            return pd.NaT

        # ISO / pandas fallback
        try:
            t = pd.Timestamp(s)
            counts["iso"] += 1
            return t
        except Exception:
            counts["invalid"] += 1
            return pd.NaT

    cleaned = series.apply(_parse)
    modal   = cleaned.dropna().mode()[0] if cleaned.notna().any() else pd.Timestamp("2020-01-01")
    filled  = cleaned.fillna(modal).dt.strftime("%Y-%m-%d")

    report = {**counts,
              "total": len(series),
              "filled_with_modal": counts["invalid"] + counts["null"],
              "modal_date": str(modal.date())}
    return filled, report


# ══════════════════════════════════════════════════════════════════════════════
# Q2 — PRICE CLEANING
# ══════════════════════════════════════════════════════════════════════════════

def clean_prices(series: pd.Series) -> tuple[pd.Series, dict]:
    counts = {"numeric": 0, "symbol_stripped": 0, "text_fallback": 0}

    def _parse(val):
        if pd.isnull(val):
            counts["text_fallback"] += 1
            return np.nan
        s = str(val).strip()
        if re.search(r"(request|call|contact|na)", s, re.I):
            counts["text_fallback"] += 1
            return np.nan
        cleaned = re.sub(r"[₹,\s]", "", s)
        orig_had_symbol = "₹" in s or "," in s
        try:
            v = float(cleaned)
            if orig_had_symbol:
                counts["symbol_stripped"] += 1
            else:
                counts["numeric"] += 1
            return v
        except ValueError:
            counts["text_fallback"] += 1
            return np.nan

    numeric = series.apply(_parse)
    median  = numeric.median()
    filled  = numeric.fillna(median)
    report  = {**counts, "total": len(series),
               "nan_filled": numeric.isna().sum(), "fill_value": round(median, 2)}
    return filled, report


# ══════════════════════════════════════════════════════════════════════════════
# Q3 — RATINGS STANDARDIZATION
# ══════════════════════════════════════════════════════════════════════════════

def clean_ratings(series: pd.Series) -> tuple[pd.Series, dict]:
    counts = {"direct_float": 0, "stars_format": 0, "fraction_format": 0,
              "invalid": 0, "null": 0}

    def _parse(val):
        if pd.isnull(val):
            counts["null"] += 1
            return np.nan
        s = str(val).strip().lower()

        m = re.match(r"^(\d+(?:\.\d+)?)\s*star", s)
        if m:
            counts["stars_format"] += 1
            return min(float(m[1]), 5.0)

        m = re.match(r"^(\d+(?:\.\d+)?)\s*/\s*5(?:\.0)?$", s)
        if m:
            counts["fraction_format"] += 1
            return min(float(m[1]), 5.0)

        try:
            v = float(s)
            if 1.0 <= v <= 5.0:
                counts["direct_float"] += 1
                return round(v, 1)
            counts["invalid"] += 1
            return np.nan
        except ValueError:
            counts["invalid"] += 1
            return np.nan

    numeric = series.apply(_parse)
    median  = round(numeric.median(), 1)
    filled  = numeric.fillna(median).clip(1.0, 5.0).round(1)
    report  = {**counts, "total": len(series),
               "null_filled": numeric.isna().sum(), "fill_value": median}
    return filled, report


# ══════════════════════════════════════════════════════════════════════════════
# Q4 — CITY NAME STANDARDIZATION
# ══════════════════════════════════════════════════════════════════════════════

_CITY_CANONICAL = {
    "Mumbai":    ["mumbai","bombay","mum","mumbai city"],
    "Bangalore": ["bangalore","bengaluru","b'lore","blr","bengaluru city"],
    "Delhi":     ["delhi","new delhi","delhi ncr","dilli","ndls"],
    "Chennai":   ["chennai","madras","chn"],
    "Hyderabad": ["hyderabad","hyd","secunderabad"],
    "Kolkata":   ["kolkata","calcutta","cal","kolkatta"],
    "Pune":      ["pune","poona","pun"],
    "Ahmedabad": ["ahmedabad","amdavad","ahd","ahmadabad"],
    "Jaipur":    ["jaipur","pink city","jai"],
    "Lucknow":   ["lucknow","lko"],
    "Surat":     ["surat","srt"],
    "Kochi":     ["kochi","cochin"],
    "Chandigarh":["chandigarh","chd","chandigar"],
    "Indore":    ["indore","idr"],
    "Nagpur":    ["nagpur","ngp"],
}
_CITY_REV = {v: k for k, vs in _CITY_CANONICAL.items() for v in vs}
for k in _CITY_CANONICAL: _CITY_REV[k.lower()] = k

def clean_cities(series: pd.Series) -> tuple[pd.Series, dict]:
    changed = 0
    def _map(val):
        nonlocal changed
        if pd.isnull(val): return "Unknown"
        s = re.sub(r"[/\\|]", " ", str(val)).strip().lower()
        if s in _CITY_REV:
            out = _CITY_REV[s]
            if out.lower() != str(val).lower(): changed += 1
            return out
        for k, v in _CITY_REV.items():
            if k in s:
                changed += 1
                return v
        return str(val).title().strip()

    cleaned = series.apply(_map)
    return cleaned, {"total": len(series), "standardized": changed,
                     "unique_after": cleaned.nunique()}


# ══════════════════════════════════════════════════════════════════════════════
# Q5 — BOOLEAN STANDARDIZATION
# ══════════════════════════════════════════════════════════════════════════════

_TRUE  = {"true","yes","1","y","t"}
_FALSE = {"false","no","0","n","f"}

def clean_booleans(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    cols = [c for c in ["is_prime_member","is_prime_eligible","is_festival_sale"] if c in df.columns]
    report = {}
    for col in cols:
        before = df[col].astype(str).str.lower()
        def _b(v):
            s = str(v).strip().lower()
            return True if s in _TRUE else False
        df[col] = df[col].apply(_b)
        report[col] = {"true_count": int(df[col].sum()),
                       "false_count": int((~df[col]).sum())}
    return df, report


# ══════════════════════════════════════════════════════════════════════════════
# Q6 — CATEGORY STANDARDIZATION
# ══════════════════════════════════════════════════════════════════════════════

_CAT_CANONICAL = {
    "Electronics":   ["electronics","electronic","electronics & accessories","gadgets","elec"],
    "Fashion":       ["fashion","clothing","apparel","clothes","garments"],
    "Home & Kitchen":["home & kitchen","home and kitchen","home","kitchen","household"],
    "Books":         ["books","book","literature","stationery"],
    "Sports":        ["sports","sports & outdoors","fitness","outdoor"],
    "Beauty":        ["beauty","beauty & personal care","personal care","cosmetics","skincare"],
    "Grocery":       ["grocery","groceries","food","food & grocery","gourmet"],
    "Toys":          ["toys","toys & games","games","kids toys"],
}
_CAT_REV = {v: k for k, vs in _CAT_CANONICAL.items() for v in vs}
for k in _CAT_CANONICAL: _CAT_REV[k.lower()] = k

def clean_categories(series: pd.Series) -> tuple[pd.Series, dict]:
    changed = 0
    def _map(val):
        nonlocal changed
        if pd.isnull(val): return "Other"
        s = str(val).strip().lower()
        if s in _CAT_REV:
            out = _CAT_REV[s]
            if out.lower() != str(val).strip().lower(): changed += 1
            return out
        for k, v in _CAT_REV.items():
            if k in s:
                changed += 1
                return v
        return str(val).title().strip()

    cleaned = series.apply(_map)
    return cleaned, {"total": len(series), "standardized": changed,
                     "unique_after": cleaned.nunique()}


# ══════════════════════════════════════════════════════════════════════════════
# Q7 — DELIVERY DAYS
# ══════════════════════════════════════════════════════════════════════════════

def clean_delivery_days(series: pd.Series) -> tuple[pd.Series, dict]:
    counts = {"numeric": 0, "same_day": 0, "range": 0, "invalid": 0}

    def _parse(val):
        if pd.isnull(val):
            counts["invalid"] += 1
            return np.nan
        s = str(val).strip().lower()
        if "same" in s or "next" in s:
            counts["same_day"] += 1
            return 0.0
        m = re.match(r"^(\d+)\s*[-–]\s*(\d+)", s)
        if m:
            counts["range"] += 1
            return (int(m[1]) + int(m[2])) / 2
        m = re.match(r"^(-?\d+)", s)
        if m:
            v = int(m[1])
            if v < 0 or v > 30:
                counts["invalid"] += 1
                return np.nan
            counts["numeric"] += 1
            return float(v)
        counts["invalid"] += 1
        return np.nan

    numeric = series.apply(_parse)
    median  = numeric.median()
    filled  = numeric.fillna(median).clip(0, 30).round(0).astype(int)
    return filled, {**counts, "total": len(series),
                    "invalid_filled": numeric.isna().sum(),
                    "fill_value": int(median)}


# ══════════════════════════════════════════════════════════════════════════════
# Q8 — DUPLICATE DETECTION
# ══════════════════════════════════════════════════════════════════════════════

def handle_duplicates(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    before = len(df)

    # Exact row dupes
    df = df.drop_duplicates()
    after_exact = len(df)

    # Same transaction_id
    if "transaction_id" in df.columns:
        df = df.drop_duplicates(subset=["transaction_id"], keep="first")
    after_txnid = len(df)

    # Semantic dupes (same customer+product+date+amount but different IDs = bulk order)
    sem_cols = [c for c in ["customer_id","product_id","order_date","final_amount_inr"]
                if c in df.columns]
    if sem_cols:
        df["is_bulk_order"] = df.duplicated(subset=sem_cols, keep=False).astype(int)
        bulk_count = int(df["is_bulk_order"].sum())
    else:
        df["is_bulk_order"] = 0
        bulk_count = 0

    return df, {
        "before": before,
        "exact_removed": before - after_exact,
        "txnid_removed": after_exact - after_txnid,
        "bulk_orders_flagged": bulk_count,
        "final_rows": len(df),
    }


# ══════════════════════════════════════════════════════════════════════════════
# Q9 — PRICE OUTLIER CORRECTION
# ══════════════════════════════════════════════════════════════════════════════

def correct_price_outliers(df: pd.DataFrame,
                           col: str = "original_price_inr") -> tuple[pd.DataFrame, dict]:
    if col not in df.columns:
        return df, {}

    decimal_fixed = extreme_fixed = 0
    cat_col = "category" if "category" in df.columns else None

    def _fix_group(idx, values, cat):
        nonlocal decimal_fixed, extreme_fixed
        if len(values) == 0: return
        med = values.median()
        if med <= 0: return

        # Decimal-shift: value is 100× too high
        mask_dec = df.index.isin(idx) & (df[col] > med * 80)
        df.loc[mask_dec, col] = df.loc[mask_dec, col] / 100
        decimal_fixed += mask_dec.sum()

        # Re-compute after fix
        updated = df.loc[df.index.isin(idx), col]
        q1, q3 = updated.quantile(0.25), updated.quantile(0.75)
        upper   = q3 + 3 * (q3 - q1)
        mask_ext = df.index.isin(idx) & (df[col] > upper)
        df.loc[mask_ext, col] = updated.median()
        extreme_fixed += mask_ext.sum()

    if cat_col:
        for cat, grp in df.groupby(cat_col):
            _fix_group(grp.index, grp[col], cat)
    else:
        _fix_group(df.index, df[col], "all")

    return df, {"decimal_shift_corrected": decimal_fixed,
                "extreme_capped": extreme_fixed,
                "total_corrected": decimal_fixed + extreme_fixed}


# ══════════════════════════════════════════════════════════════════════════════
# Q10 — PAYMENT METHOD STANDARDIZATION
# ══════════════════════════════════════════════════════════════════════════════

_PAY_CANONICAL = {
    "UPI":              ["upi","phonepe","googlepay","google pay","paytm","bhim",
                         "upi/phonepe","upi/googlepay","phone pe"],
    "Credit Card":      ["credit card","credit_card","cc","creditcard","visa credit",
                         "mastercard credit","credit"],
    "Debit Card":       ["debit card","debit_card","dc","debitcard","visa debit",
                         "mastercard debit","debit"],
    "Cash on Delivery": ["cash on delivery","cod","c.o.d","cash","cod/cash"],
    "Net Banking":      ["net banking","netbanking","internet banking","neft","rtgs"],
    "EMI":              ["emi","equated monthly","no cost emi","emi/credit"],
    "Amazon Pay":       ["amazon pay","wallet","mobikwik","freecharge","amazon_pay"],
}
_PAY_REV = {v: k for k, vs in _PAY_CANONICAL.items() for v in vs}
for k in _PAY_CANONICAL: _PAY_REV[k.lower()] = k

def clean_payments(series: pd.Series) -> tuple[pd.Series, dict]:
    changed = 0
    def _map(val):
        nonlocal changed
        if pd.isnull(val): return "Other"
        s = str(val).strip().lower()
        if s in _PAY_REV:
            out = _PAY_REV[s]
            if out.lower() != str(val).strip().lower(): changed += 1
            return out
        for k, v in _PAY_REV.items():
            if k in s:
                changed += 1
                return v
        return "Other"

    cleaned = series.apply(_map)
    return cleaned, {"total": len(series), "standardized": changed,
                     "unique_after": cleaned.nunique(),
                     "distribution": cleaned.value_counts().to_dict()}


# ══════════════════════════════════════════════════════════════════════════════
# MASTER PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

def run_pipeline(df: pd.DataFrame, verbose: bool = True) -> tuple[pd.DataFrame, dict]:
    """Execute all 10 cleaning challenges. Returns (clean_df, full_report)."""
    report = {}
    df = df.copy()

    def _log(msg):
        if verbose: print(msg)

    _log("\n" + "═"*65)
    _log("   🧹  AMAZON INDIA — DATA CLEANING PIPELINE")
    _log("═"*65)
    _log(f"   Input : {len(df):,} rows × {df.shape[1]} columns")
    _log("─"*65)

    # Q1
    if "order_date" in df.columns:
        df["order_date"], r = clean_dates(df["order_date"])
        report["Q1_dates"] = r
        _log(f"   ✓ Q1  Dates      — {r['invalid']+r['null']:,} invalid/null → modal ({r['modal_date']})")

    # Q2
    if "original_price_inr" in df.columns:
        df["original_price_inr"], r = clean_prices(df["original_price_inr"])
        report["Q2_prices"] = r
        _log(f"   ✓ Q2  Prices     — {r['nan_filled']:,} non-numeric → median ₹{r['fill_value']:,}")

    # Q3
    if "product_rating" in df.columns:
        df["product_rating"], r = clean_ratings(df["product_rating"])
        report["Q3_ratings"] = r
        _log(f"   ✓ Q3  Ratings    — {r['null_filled']:,} null/invalid → {r['fill_value']} | "
             f"stars:{r['stars_format']} fracs:{r['fraction_format']}")

    # Q4
    if "customer_city" in df.columns:
        df["customer_city"], r = clean_cities(df["customer_city"])
        report["Q4_cities"] = r
        _log(f"   ✓ Q4  Cities     — {r['standardized']:,} standardized → {r['unique_after']} unique")

    # Q5
    df, r = clean_booleans(df)
    report["Q5_booleans"] = r
    for col, cr in r.items():
        _log(f"   ✓ Q5  Boolean    — {col}: True={cr['true_count']:,} False={cr['false_count']:,}")

    # Q6
    if "category" in df.columns:
        df["category"], r = clean_categories(df["category"])
        report["Q6_categories"] = r
        _log(f"   ✓ Q6  Categories — {r['standardized']:,} standardized → {r['unique_after']} unique")

    # Q7
    if "delivery_days" in df.columns:
        df["delivery_days"], r = clean_delivery_days(df["delivery_days"])
        report["Q7_delivery"] = r
        _log(f"   ✓ Q7  Delivery   — {r['invalid_filled']:,} invalid → median {r['fill_value']}d | "
             f"same_day:{r['same_day']} range:{r['range']}")

    # Q8
    df, r = handle_duplicates(df)
    report["Q8_duplicates"] = r
    _log(f"   ✓ Q8  Duplicates — {r['exact_removed']+r['txnid_removed']:,} removed, "
         f"{r['bulk_orders_flagged']:,} bulk orders flagged")

    # Q9
    df, r = correct_price_outliers(df)
    report["Q9_outliers"] = r
    _log(f"   ✓ Q9  Outliers   — {r.get('total_corrected',0):,} price outliers corrected")

    # Q10
    if "payment_method" in df.columns:
        df["payment_method"], r = clean_payments(df["payment_method"])
        report["Q10_payments"] = r
        _log(f"   ✓ Q10 Payments  — {r['standardized']:,} standardized → {r['unique_after']} unique")

    # ── Derived columns ───────────────────────────────────────────────────────
    df["order_date_dt"]  = pd.to_datetime(df["order_date"], errors="coerce")
    df["order_year"]     = df["order_date_dt"].dt.year.fillna(df.get("order_year",2020)).astype(int)
    df["order_month"]    = df["order_date_dt"].dt.month.fillna(df.get("order_month",6)).astype(int)
    df["order_quarter"]  = df["order_date_dt"].dt.quarter.fillna(2).astype(int)
    df["order_week"]     = df["order_date_dt"].dt.isocalendar().week.astype(int)
    df["is_weekend"]     = df["order_date_dt"].dt.dayofweek.isin([5,6]).astype(int)

    df["discount_percent"] = pd.to_numeric(df.get("discount_percent",0), errors="coerce").fillna(0)
    if "final_amount_inr" not in df.columns:
        df["final_amount_inr"] = (df["original_price_inr"] * (1 - df["discount_percent"]/100)).round(2)

    _log("─"*65)
    _log(f"   Output: {len(df):,} rows × {df.shape[1]} columns")
    _log("═"*65 + "\n")

    return df, report


def save_cleaning_report(report: dict, path: Path = None):
    """Save cleaning summary as text file."""
    path = path or (REPORT_DIR / "cleaning_report.txt")
    lines = ["AMAZON INDIA — DATA CLEANING REPORT", "="*55, ""]
    for qname, r in report.items():
        lines.append(f"[{qname}]")
        for k, v in r.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    path.write_text("\n".join(lines))
    print(f"   📄 Cleaning report → {path}")


def save_cleaned_csv(df: pd.DataFrame, path: Path = None):
    """Save the production-ready cleaned dataset."""
    path = path or (OUTPUT_DIR / "amazon_india_cleaned.csv")
    df.to_csv(path, index=False)
    print(f"   💾 Cleaned CSV saved → {path}")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from utils.data_generator import make_transactions, make_catalog

    print("⏳ Generating synthetic data…")
    raw = make_transactions()
    print(f"   Raw shape: {raw.shape}")

    clean, rpt = run_pipeline(raw)
    save_cleaning_report(rpt)
    save_cleaned_csv(clean)
    print("✅  Cleaning complete!")
