# 🛒 Amazon India: A Decade of Sales Analytics
### GUVI HCL · Fullstack Data Science with Generative & Agentic AI Program

---

## 📋 Project Overview

| Field | Details |
|-------|---------|
| **Domain** | E-Commerce Analytics |
| **Period** | 2015 – 2025 (10 Years) |
| **Records** | ~80,000 synthetic transactions (mirrors ~1M real dataset structure) |
| **Skills** | Python · Pandas · Matplotlib · Seaborn · SQL · Streamlit · Plotly · BI |

---

## 🏗️ Project Structure

```
amazon_india_analytics/
│
├── 📄 setup.py                        ← ONE-CLICK full pipeline runner
├── 📄 requirements.txt                ← All Python dependencies
├── 📄 README.md                       ← This guide
│
├── 📁 config/
│   └── settings.py                    ← Paths, palette, constants
│
├── 📁 utils/
│   └── data_generator.py              ← Synthetic data (80K rows, 25% dirty)
│
├── 📁 data_cleaning/
│   └── cleaning_pipeline.py           ← 10 cleaning challenges (Q1–Q10)
│
├── 📁 eda/
│   └── eda_visualizations.py          ← 20 EDA visualizations (Q1–Q20)
│
├── 📁 sql/
│   └── db_integration.py              ← SQLite schema + queries (Q1–Q5)
│
├── 📁 dashboard/
│   └── streamlit_app.py               ← 30-chart Streamlit dashboard (Q1–Q30)
│
└── 📁 outputs/
    ├── eda/                           ← 20 PNG charts (auto-generated)
    ├── cleaning_reports/              ← Cleaning summary reports
    └── sql/                           ← SQL schema export
```

---

## ⚡ STEP-BY-STEP GUIDE

### ✅ STEP 1 — Install Python

Make sure Python 3.9 or higher is installed.

```bash
python --version
# Should show: Python 3.9.x or higher
```

Download Python from: https://www.python.org/downloads/

---

### ✅ STEP 2 — Download / Unzip This Project

Unzip the downloaded file to any folder, e.g.:
```
C:\Users\YourName\amazon_india_analytics\   (Windows)
~/amazon_india_analytics/                    (Mac/Linux)
```

---

### ✅ STEP 3 — Open Terminal / Command Prompt

**Windows:** Press `Win + R` → type `cmd` → Enter

**Mac/Linux:** Open Terminal

Navigate to the project folder:
```bash
cd amazon_india_analytics
```

---

### ✅ STEP 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs: pandas, numpy, matplotlib, seaborn, plotly, streamlit, sqlalchemy, scikit-learn, scipy

> 💡 If you see permission errors, use: `pip install -r requirements.txt --user`

---

### ✅ STEP 5 — Run the Full Pipeline (One Command!)

```bash
python setup.py
```

This automatically runs all 4 steps:
1. 🔄 Generates 80,000 synthetic transactions with 25% data quality issues
2. 🧹 Runs all 10 data cleaning challenges
3. 📊 Generates all 20 EDA visualization charts (saved to `outputs/eda/`)
4. 🗄️  Sets up SQLite database with full schema and indexes

**Expected output:**
```
✅  Transactions : 80,000 rows × 30 columns
✅  Clean shape  : 79,XXX rows × 35 columns
✅  20 charts saved to outputs/eda/
✅  Database ready → amazon_india.db
```

---

### ✅ STEP 6 — Launch the Streamlit Dashboard

```bash
streamlit run dashboard/streamlit_app.py
```

Your browser will automatically open at: **http://localhost:8501**

**Dashboard has 6 pages with 30 charts:**

| Page | Charts | Topics |
|------|--------|--------|
| 📊 Executive Dashboard | 1–5 | KPIs, Revenue, Heatmap, Gauges |
| 💰 Revenue & Seasonality | 6–10 | Quarterly, Seasonal, Festival, Discounts |
| 👥 Customer Intelligence | 11–15 | RFM, CLV, Prime, Age Groups |
| 📦 Product & Brand | 16–20 | Products, Brands, Ratings, Lifecycle |
| 🚚 Operations & Logistics | 21–25 | Delivery, Payment, Returns |
| 🔬 Advanced Analytics | 26–30 | Forecast, Correlation, BI Command Centre |

---

## 📦 Run Individual Modules

You can also run each module independently:

```bash
# Data Cleaning only (saves cleaned CSV + report)
python data_cleaning/cleaning_pipeline.py

# EDA Visualizations only (saves 20 PNGs)
python eda/eda_visualizations.py

# SQL Database only
python sql/db_integration.py
```

---

## 📂 Using Your Own Real Dataset

If you have the GUVI dataset from Google Drive:

1. Create a `data/` folder inside the project
2. Place these files inside:
   ```
   data/
   ├── amazon_india_products_catalog.csv
   ├── amazon_india_2015.csv
   ├── amazon_india_2016.csv
   ├── ...
   └── amazon_india_2025.csv
   ```
3. Run `python setup.py` — it will auto-detect and use the real data

---

## 🧹 Data Cleaning Challenges Covered

| Q# | Challenge | Method |
|----|-----------|--------|
| Q1 | Date Standardization | Regex multi-format parser → YYYY-MM-DD |
| Q2 | Price Cleaning | Strip ₹, commas, handle "Price on Request" |
| Q3 | Rating Standardization | Parse "4 stars", "3/5", "2.5/5.0" → float |
| Q4 | City Name Standardization | Canonical map: Mumbai/Bombay → Mumbai |
| Q5 | Boolean Columns | True/False/Yes/No/1/0/Y/N → True/False |
| Q6 | Category Standardization | ELECTRONICS/electronic → Electronics |
| Q7 | Delivery Days | Handle negatives, "Same Day", ranges, extremes |
| Q8 | Duplicate Detection | Exact + semantic duplicates, bulk order flagging |
| Q9 | Price Outlier Correction | 100× decimal-shift detection per category |
| Q10 | Payment Method | UPI/PhonePe/GooglePay → UPI (canonical map) |

---

## 📊 EDA Visualizations (20 Charts)

| Q# | Chart | Type |
|----|-------|------|
| Q1 | Revenue Trend 2015-2025 | Bar + Line (dual axis) |
| Q2 | Seasonal Heatmap | Heatmap (Year × Month) |
| Q3 | RFM Segmentation | Scatter + Donut |
| Q4 | Payment Evolution | Stacked Area |
| Q5 | Category Performance | Bar + Pie + Bar |
| Q6 | Prime Impact | Grouped Bar |
| Q7 | Geographic Analysis | Horizontal Bar (x2) |
| Q8 | Festival Impact | Bar + Monthly pattern |
| Q9 | Age Group Behavior | Stacked Bar + Bar |
| Q10 | Price vs Demand | Bar (x2) |
| Q11 | Delivery Performance | Histogram + Bar |
| Q12 | Return Rate | Horizontal Bar + Bar |
| Q13 | Brand Performance | Bar |
| Q14 | Customer Lifetime Value | Line + Histogram |
| Q15 | Discount Effectiveness | Bar (x3) |
| Q16 | Ratings Impact | Bar (x2) |
| Q17 | Purchase Frequency | Histogram |
| Q18 | Category Lifecycle | Multi-line |
| Q19 | Competitive Pricing | Box plots |
| Q20 | Executive Dashboard | Multi-panel (8 charts) |

---

## 🗄️ SQL Database Schema

```sql
-- 3 tables, 13 indexes
transactions  → 32 columns, PRIMARY KEY on transaction_id
products      → 10 columns, PRIMARY KEY on product_id
time_dim      → 9 columns, full date dimension 2015-2025
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Core language |
| Pandas | Data manipulation |
| NumPy | Numerical operations |
| Matplotlib + Seaborn | Static EDA charts |
| Plotly | Interactive dashboard charts |
| Streamlit | Web dashboard framework |
| SQLite + SQLAlchemy | Database |
| Scikit-learn | Statistical utilities |

---

## ❓ Troubleshooting

**Problem:** `ModuleNotFoundError`
**Fix:** Run `pip install -r requirements.txt`

**Problem:** `streamlit: command not found`
**Fix:** Run `pip install streamlit` then try again

**Problem:** Port already in use
**Fix:** `streamlit run dashboard/streamlit_app.py --server.port 8502`

**Problem:** Charts not displaying in dashboard
**Fix:** Make sure you ran `python setup.py` first

---

## 📞 GUVI Support Sessions

- **Doubt Clarification:** Monday–Saturday, 3:00 PM – 4:00 PM
- **Live Evaluation:** Monday–Saturday, 5:30 PM – 7:00 PM
- **Booking:** https://forms.gle/1m2Gsro41fLtZurRA

---

*Built for GUVI HCL Fullstack Data Science with Generative & Agentic AI Program*
*Subhash Govindharaj · Shadiya P P · Nehlath Harmain*
