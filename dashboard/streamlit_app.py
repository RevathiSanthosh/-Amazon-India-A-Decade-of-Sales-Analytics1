"""
dashboard/streamlit_app.py
---------------------------
Amazon India: A Decade of Sales Analytics
Multi-page Streamlit dashboard — 30 Plotly charts across 6 pages.

Launch:
    streamlit run dashboard/streamlit_app.py
"""

import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.settings import PALETTE as P, CAT_COLORS, MONTHS, FESTIVAL_MONTHS

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="🛒 Amazon India Analytics",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
  /* ── page background ── */
  .stApp {{ background-color:{P['dark_bg']}; }}
  .block-container {{ padding-top:0.8rem; padding-bottom:1rem; }}
  section[data-testid="stSidebar"] {{ background:{P['mid_bg']}; }}
  section[data-testid="stSidebar"] * {{ color:{P['text']} !important; }}

  /* ── KPI card ── */
  .kpi {{
    background:linear-gradient(135deg,{P['mid_bg']},{P['card_bg']});
    border:1px solid {P['border']};
    border-radius:14px; padding:18px 14px; text-align:center;
    box-shadow:0 4px 18px rgba(0,0,0,.45);
  }}
  .kpi-val {{ font-size:2rem; font-weight:800; color:{P['orange']}; margin:0; line-height:1.1; }}
  .kpi-lbl {{ font-size:.72rem; color:{P['muted']}; margin-top:5px;
               letter-spacing:.6px; text-transform:uppercase; }}

  /* ── section header ── */
  .sh {{ border-left:4px solid {P['orange']}; padding-left:10px;
         color:{P['orange']}; font-weight:700; font-size:1rem; margin-bottom:4px; }}

  /* ── tabs ── */
  .stTabs [data-baseweb="tab"] {{ color:{P['muted']}; }}
  .stTabs [aria-selected="true"] {{ color:{P['orange']} !important; border-bottom-color:{P['orange']} !important; }}
</style>
""", unsafe_allow_html=True)

T = "plotly_dark"   # Plotly template alias

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING (cached)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="⏳ Loading & cleaning 80 000 transactions…")
def _load():
    from utils.data_generator import make_transactions, make_catalog
    from data_cleaning.cleaning_pipeline import run_pipeline
    from sql.db_integration import setup_db, get_conn, DB_PATH
    raw  = make_transactions()
    df, _ = run_pipeline(raw, verbose=False)
    cat  = make_catalog()
    conn = setup_db(df, cat)
    return df, cat, conn

df_all, catalog, conn = _load()

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR  — global filters
# ══════════════════════════════════════════════════════════════════════════════
def sidebar(df):
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg", width=130)
        st.markdown(f"<h3 style='color:{P['orange']};margin:4px 0 2px'>A Decade of Analytics</h3>", unsafe_allow_html=True)
        st.caption("Amazon India  ·  2015 – 2025")
        st.divider()

        years = sorted(df["order_year"].dropna().unique().astype(int))
        yr_range = st.slider("📅 Year Range", int(min(years)), int(max(years)),
                             (int(min(years)), int(max(years))))

        cats = ["All"] + sorted(df["category"].dropna().unique().tolist())
        sel_cat = st.selectbox("🛍️ Category", cats)

        prime_opt = st.radio("⭐ Prime Filter", ["All","Prime Only","Non-Prime Only"])

        st.divider()
        pages_list = [
            "📊 Executive Dashboard",
            "💰 Revenue & Seasonality",
            "👥 Customer Intelligence",
            "📦 Product & Brand",
            "🚚 Operations & Logistics",
            "🔬 Advanced Analytics",
        ]
        page = st.radio("📄 Page", pages_list, label_visibility="collapsed")

        st.divider()
        st.markdown(f"""<div style='font-size:.72rem;color:{P['muted']};text-align:center;'>
        {len(df):,} transactions<br>{int(min(years))}–{int(max(years))}<br><br>
        <em>GUVI HCL DS Program</em></div>""", unsafe_allow_html=True)

    # Apply filters
    f = df[(df["order_year"] >= yr_range[0]) & (df["order_year"] <= yr_range[1])]
    if sel_cat != "All":
        f = f[f["category"] == sel_cat]
    if prime_opt == "Prime Only":
        f = f[f["is_prime_member"] == True]
    elif prime_opt == "Non-Prime Only":
        f = f[f["is_prime_member"] == False]
    return f, page

# ── Helpers ───────────────────────────────────────────────────────────────────
def kpi(label, value, col=None):
    html = f'<div class="kpi"><p class="kpi-val">{value}</p><p class="kpi-lbl">{label}</p></div>'
    if col: col.markdown(html, unsafe_allow_html=True)
    else:   st.markdown(html, unsafe_allow_html=True)

def sh(title):
    st.markdown(f'<div class="sh">{title}</div>', unsafe_allow_html=True)

def layout(fig, h=420):
    fig.update_layout(template=T, paper_bgcolor=P["dark_bg"],
                      plot_bgcolor=P["card_bg"], height=h,
                      margin=dict(l=10,r=10,t=40,b=10),
                      font_color=P["text"])
    return fig

def pc(fig, **kw):   # plotly chart shortcut
    st.plotly_chart(fig, use_container_width=True, **kw)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — EXECUTIVE DASHBOARD  (Charts 1-5)
# ══════════════════════════════════════════════════════════════════════════════
def page_executive(df):
    st.title("📊 Executive Dashboard")
    st.caption("High-level KPIs and strategic business overview")

    # ── KPI Row ───────────────────────────────────────────────────────────────
    total_rev = df["final_amount_inr"].sum()
    n_orders  = len(df)
    n_cust    = df["customer_id"].nunique()
    aov       = df["final_amount_inr"].mean()
    prime_pct = (df["is_prime_member"] == True).mean() * 100

    c1,c2,c3,c4,c5 = st.columns(5)
    kpi("💰 Total Revenue",   f"₹{total_rev/1e7:.1f} Cr", c1)
    kpi("📦 Total Orders",    f"{n_orders:,}",             c2)
    kpi("👥 Customers",       f"{n_cust:,}",               c3)
    kpi("🛒 Avg Order Value", f"₹{aov:,.0f}",              c4)
    kpi("⭐ Prime Members",   f"{prime_pct:.1f}%",         c5)

    st.markdown("---")

    # ── Chart 1 — Revenue trend + YoY ────────────────────────────────────────
    sh("📈 Chart 1 — Annual Revenue + YoY Growth Rate")
    yr = df.groupby("order_year")["final_amount_inr"].sum().reset_index()
    yr["growth"] = yr["final_amount_inr"].pct_change() * 100
    yr["rev_cr"] = yr["final_amount_inr"] / 1e7

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=yr["order_year"], y=yr["rev_cr"],
                         name="Revenue (₹ Cr)", marker_color=P["orange"],
                         marker_line_color=P["dark_bg"], opacity=0.88), secondary_y=False)
    fig.add_trace(go.Scatter(x=yr["order_year"], y=yr["growth"],
                             name="YoY Growth %", mode="lines+markers",
                             line=dict(color=P["success"], width=2.5),
                             marker=dict(size=8)), secondary_y=True)
    fig.update_yaxes(title_text="Revenue (₹ Crore)", secondary_y=False)
    fig.update_yaxes(title_text="Growth %", secondary_y=True)
    fig.update_xaxes(tickmode="linear")
    pc(layout(fig, 420))

    c1, c2 = st.columns(2)

    # ── Chart 2 — Category donut ──────────────────────────────────────────────
    with c1:
        sh("🥧 Chart 2 — Category Revenue Mix")
        cat = df.groupby("category")["final_amount_inr"].sum().reset_index()
        fig2 = px.pie(cat, values="final_amount_inr", names="category",
                      hole=0.46, color_discrete_sequence=px.colors.sequential.Oranges_r)
        fig2.update_traces(textposition="outside", textinfo="percent+label",
                           marker=dict(line=dict(color=P["dark_bg"], width=1.5)))
        pc(layout(fig2, 400))

    # ── Chart 3 — Top cities bar ──────────────────────────────────────────────
    with c2:
        sh("🏙️ Chart 3 — Top 10 Cities by Revenue")
        city = df.groupby("customer_city")["final_amount_inr"].sum().nlargest(10).reset_index()
        fig3 = px.bar(city, x="final_amount_inr", y="customer_city",
                      orientation="h", color="final_amount_inr",
                      color_continuous_scale="Oranges",
                      labels={"final_amount_inr":"Revenue (₹)","customer_city":"City"})
        fig3.update_layout(showlegend=False, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        pc(layout(fig3, 400))

    # ── Chart 4 — Heatmap ────────────────────────────────────────────────────
    sh("🗓️ Chart 4 — Monthly Revenue Heatmap (Year × Month)")
    pivot = (df.groupby(["order_year","order_month"])["final_amount_inr"]
               .sum().reset_index()
               .pivot(index="order_year", columns="order_month", values="final_amount_inr")
               .fillna(0))
    pivot.columns = [MONTHS[m-1] for m in pivot.columns]
    fig4 = px.imshow(pivot/1e5, color_continuous_scale="YlOrRd", aspect="auto",
                     labels=dict(color="₹ Lakhs"), text_auto=".1f")
    fig4.update_traces(textfont_size=9)
    pc(layout(fig4, 360))

    # ── Chart 5 — Gauge indicators ───────────────────────────────────────────
    sh("🎯 Chart 5 — Business Health Gauges")
    ret_rate = (df["return_status"].str.lower().str.contains("return", na=False).mean() * 100
                if "return_status" in df.columns else 8.0)
    avg_del  = pd.to_numeric(df.get("delivery_days", pd.Series([3])), errors="coerce").mean()
    avg_crat = pd.to_numeric(df.get("customer_rating", pd.Series([4.0])), errors="coerce").mean()

    g1, g2, g3 = st.columns(3)
    for gcol, (label, val, mx, clr) in zip([g1,g2,g3],[
        ("Return Rate %",     ret_rate, 20, P["danger"]),
        ("Avg Delivery Days", avg_del,  10, P["orange"]),
        ("Avg Customer Rating", avg_crat, 5, P["success"]),
    ]):
        gfig = go.Figure(go.Indicator(
            mode="gauge+number", value=round(val, 1),
            title={"text": label, "font": {"color": clr, "size": 14}},
            gauge={"axis":{"range":[0,mx]}, "bar":{"color":clr},
                   "bgcolor":P["card_bg"], "bordercolor":P["border"]},
            number={"font":{"color":clr}},
        ))
        gfig.update_layout(paper_bgcolor=P["dark_bg"], height=230,
                           margin=dict(t=60,b=0,l=30,r=30))
        gcol.plotly_chart(gfig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — REVENUE & SEASONALITY  (Charts 6-10)
# ══════════════════════════════════════════════════════════════════════════════
def page_revenue(df):
    st.title("💰 Revenue & Seasonality")
    st.caption("Quarterly trends, seasonality patterns, festival impact and discount analytics")

    # ── Chart 6 — Quarterly trend ─────────────────────────────────────────────
    sh("📅 Chart 6 — Quarterly Revenue Trend")
    qtr = df.groupby(["order_year","order_quarter"])["final_amount_inr"].sum().reset_index()
    qtr["period"] = qtr["order_year"].astype(str) + " Q" + qtr["order_quarter"].astype(str)
    fig6 = px.line(qtr, x="period", y="final_amount_inr", markers=True,
                   color_discrete_sequence=[P["orange"]],
                   labels={"final_amount_inr":"Revenue (₹)","period":"Quarter"})
    fig6.update_traces(line_width=2.5, marker_size=8)
    fig6.update_xaxes(tickangle=45)
    pc(layout(fig6, 400))

    c1, c2 = st.columns(2)

    # ── Chart 7 — Multi-year monthly overlay ─────────────────────────────────
    with c1:
        sh("📆 Chart 7 — Multi-Year Monthly Revenue Overlay")
        mo_yr = df.groupby(["order_year","order_month"])["final_amount_inr"].sum().reset_index()
        mo_yr["month_name"] = mo_yr["order_month"].apply(lambda m: MONTHS[m-1])
        mo_yr["month_name"] = pd.Categorical(mo_yr["month_name"], categories=MONTHS, ordered=True)
        fig7 = px.line(mo_yr, x="month_name", y="final_amount_inr",
                       color="order_year", markers=True,
                       color_discrete_sequence=px.colors.sequential.Oranges[1:],
                       labels={"final_amount_inr":"Revenue (₹)","month_name":"Month","order_year":"Year"})
        pc(layout(fig7, 400))

    # ── Chart 8 — Category YoY ────────────────────────────────────────────────
    with c2:
        sh("📊 Chart 8 — Category Revenue Growth YoY")
        yr_cat = df.groupby(["order_year","category"])["final_amount_inr"].sum().reset_index()
        fig8 = px.line(yr_cat, x="order_year", y="final_amount_inr",
                       color="category", markers=True,
                       color_discrete_sequence=CAT_COLORS,
                       labels={"final_amount_inr":"Revenue (₹)","order_year":"Year"})
        pc(layout(fig8, 400))

    # ── Chart 9 — Festival impact ─────────────────────────────────────────────
    sh("🎉 Chart 9 — Festival vs Regular Sales Impact")
    df2 = df.copy()
    df2["fest_label"] = df2["is_festival_sale"].apply(
        lambda x: "🎊 Festival" if str(x).lower() in ["true","1","yes"] else "Regular")

    t9a, t9b = st.columns(2)
    with t9a:
        agg9 = df2.groupby("fest_label")["final_amount_inr"].agg(["sum","mean","count"]).reset_index()
        fig9a = go.Figure()
        for i,(col,ytitle) in enumerate([("sum","Total Revenue (₹)"),("mean","Avg Order (₹)")]):
            fig9a.add_trace(go.Bar(x=agg9["fest_label"], y=agg9[col],
                                   name=ytitle, marker_color=[P["orange"],P["teal"]][i],
                                   opacity=0.9))
        fig9a.update_layout(barmode="group")
        pc(layout(fig9a, 360))

    with t9b:
        mo9 = df.groupby("order_month")["final_amount_inr"].mean().reset_index()
        colors_mo = [P["orange"] if m in FESTIVAL_MONTHS else P["teal"] for m in mo9["order_month"]]
        mo9["month"] = mo9["order_month"].apply(lambda m: MONTHS[m-1])
        fig9b = go.Figure(go.Bar(x=mo9["month"], y=mo9["final_amount_inr"]/1000,
                                  marker_color=colors_mo, name="Avg Revenue"))
        fig9b.update_layout(title="Monthly Avg Revenue  |  🟠 Festival Months")
        pc(layout(fig9b, 360))

    # ── Chart 10 — Discount effectiveness ────────────────────────────────────
    sh("🏷️ Chart 10 — Discount Effectiveness")
    df3 = df.copy()
    df3["disc_bucket"] = pd.cut(
        pd.to_numeric(df3["discount_percent"], errors="coerce").fillna(0),
        bins=[-1,0,10,20,30,50,100],
        labels=["0%","1-10%","11-20%","21-30%","31-50%","51%+"])
    disc_agg = df3.groupby("disc_bucket", observed=True).agg(
        orders=("transaction_id","count"),
        revenue=("final_amount_inr","sum"),
        aov=("final_amount_inr","mean")).reset_index()

    fig10 = make_subplots(rows=1, cols=3,
                          subplot_titles=["Orders by Discount","Revenue by Discount","AOV by Discount"])
    for i,(col,sc) in enumerate([("orders","Reds"),("revenue","Oranges"),("aov","Greens")],1):
        vals = disc_agg[col] if col=="orders" else disc_agg[col]/(1e5 if col=="revenue" else 1)
        colors = getattr(px.colors.sequential, sc)[2:]
        fig10.add_trace(go.Bar(x=disc_agg["disc_bucket"].astype(str), y=vals,
                               marker_color=colors[i % len(colors)], name=col), row=1, col=i)
    fig10.update_layout(showlegend=False)
    pc(layout(fig10, 400))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CUSTOMER INTELLIGENCE  (Charts 11-15)
# ══════════════════════════════════════════════════════════════════════════════
def page_customers(df):
    st.title("👥 Customer Intelligence")
    st.caption("RFM segmentation, lifetime value, prime analysis and age group behaviour")

    # ── Chart 11 — Spending tier ──────────────────────────────────────────────
    sh("💎 Chart 11 — Customer Spending Tier Analysis")
    tier = df.groupby("customer_spending_tier").agg(
        customers=("customer_id","nunique"),
        revenue=("final_amount_inr","sum"),
        aov=("final_amount_inr","mean")).reset_index()

    t11a, t11b = st.columns(2)
    with t11a:
        fig11a = px.pie(tier, values="customers", names="customer_spending_tier",
                        hole=0.46, color_discrete_sequence=px.colors.sequential.Plasma_r,
                        title="Customer Count by Tier")
        fig11a.update_traces(marker=dict(line=dict(color=P["dark_bg"],width=1.5)))
        pc(layout(fig11a, 380))
    with t11b:
        fig11b = px.bar(tier, x="customer_spending_tier", y="aov",
                        color="customer_spending_tier",
                        color_discrete_sequence=px.colors.sequential.Plasma_r,
                        labels={"aov":"Avg Order Value (₹)","customer_spending_tier":"Tier"},
                        title="Average Order Value by Tier")
        fig11b.update_layout(showlegend=False)
        pc(layout(fig11b, 380))

    # ── Chart 12 — RFM scatter ────────────────────────────────────────────────
    sh("🎯 Chart 12 — RFM Segmentation Scatter")
    snap = df["order_date_dt"].max()
    rfm = df.groupby("customer_id").agg(
        R=("order_date_dt", lambda x: (snap-x.max()).days),
        F=("transaction_id","count"),
        M=("final_amount_inr","sum"),
    ).reset_index()
    def _seg(r,f,m):
        score = 0
        score += 3 if r<200 else (2 if r<400 else 1)
        score += 3 if f>=4  else (2 if f>=2  else 1)
        score += 3 if m>10000 else (2 if m>3000 else 1)
        return "Champions" if score==9 else ("Loyal" if score>=7 else ("At Risk" if score>=5 else "Dormant"))
    rfm["segment"] = rfm.apply(lambda row: _seg(row.R, row.F, row.M), axis=1)
    sample = rfm.sample(min(3000, len(rfm)), random_state=42)
    seg_c = {"Champions":P["orange"],"Loyal":P["success"],"At Risk":P["info"],"Dormant":P["danger"]}

    fig12 = px.scatter(sample, x="F", y="M", color="segment",
                       color_discrete_map=seg_c, opacity=0.55, size_max=8,
                       labels={"F":"Frequency (Orders)","M":"Monetary (₹)","segment":"Segment"},
                       title="Customer Segments: Frequency vs Monetary Value")
    pc(layout(fig12, 450))

    # ── Chart 13 — Prime deep dive ────────────────────────────────────────────
    sh("⭐ Chart 13 — Prime Membership Deep Dive")
    df2 = df.copy()
    df2["Prime"] = (df2["is_prime_member"]==True).map({True:"⭐ Prime",False:"Non-Prime"})

    t13a, t13b = st.columns(2)
    with t13a:
        prime_rev = df2.groupby("Prime")["final_amount_inr"].agg(["mean","sum"]).reset_index()
        fig13a = go.Figure()
        fig13a.add_trace(go.Bar(x=prime_rev["Prime"], y=prime_rev["mean"],
                                name="Avg Order ₹", marker_color=[P["orange"],P["teal"]]))
        fig13a.update_layout(title="Avg Order Value: Prime vs Non-Prime")
        pc(layout(fig13a, 360))
    with t13b:
        prime_yr = df2.groupby(["order_year","Prime"])["final_amount_inr"].sum().reset_index()
        fig13b = px.line(prime_yr, x="order_year", y="final_amount_inr",
                         color="Prime", markers=True,
                         color_discrete_map={"⭐ Prime":P["orange"],"Non-Prime":P["teal"]},
                         labels={"final_amount_inr":"Revenue (₹)","order_year":"Year"},
                         title="Prime vs Non-Prime Revenue Trend")
        pc(layout(fig13b, 360))

    # ── Chart 14 — CLV cohort ─────────────────────────────────────────────────
    sh("💰 Chart 14 — Customer Lifetime Value by Cohort Year")
    first_yr = df.groupby("customer_id")["order_year"].min().reset_index()
    first_yr.columns = ["customer_id","cohort"]
    clv_df = df.merge(first_yr, on="customer_id")
    cohort = clv_df.groupby("cohort")["final_amount_inr"].agg(
        median="median", mean="mean").reset_index()

    fig14 = go.Figure()
    fig14.add_trace(go.Bar(x=cohort["cohort"], y=cohort["median"],
                           name="Median CLV", marker_color=P["teal"], opacity=0.82))
    fig14.add_trace(go.Scatter(x=cohort["cohort"], y=cohort["mean"],
                               name="Mean CLV", mode="lines+markers",
                               line=dict(color=P["orange"],width=2.5), marker=dict(size=9)))
    fig14.update_layout(title="Median & Mean CLV by Customer Acquisition Year",
                        xaxis_title="Cohort Year", yaxis_title="CLV (₹)")
    pc(layout(fig14, 400))

    # ── Chart 15 — Age group ──────────────────────────────────────────────────
    sh("👶 Chart 15 — Age Group Spending Behaviour")
    if "age_group" in df.columns:
        age = df.groupby("age_group").agg(
            orders=("transaction_id","count"),
            aov=("final_amount_inr","mean"),
            revenue=("final_amount_inr","sum"),
        ).reset_index()

        fig15 = make_subplots(rows=1, cols=2,
                              subplot_titles=["Order Volume by Age","Avg Spend by Age"])
        fig15.add_trace(go.Bar(x=age["age_group"], y=age["orders"],
                               marker_color=P["teal"], name="Orders"), row=1, col=1)
        fig15.add_trace(go.Bar(x=age["age_group"], y=age["aov"],
                               marker_color=P["orange"], name="AOV (₹)"), row=1, col=2)
        fig15.update_layout(showlegend=False)
        pc(layout(fig15, 380))
    else:
        st.info("age_group column not available in filtered data.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PRODUCT & BRAND  (Charts 16-20)
# ══════════════════════════════════════════════════════════════════════════════
def page_products(df):
    st.title("📦 Product & Brand Analytics")
    st.caption("Product performance, brand revenue, pricing intelligence and ratings")

    # ── Chart 16 — Top products ───────────────────────────────────────────────
    sh("🏆 Chart 16 — Top 15 Products by Revenue")
    prod = df.groupby("product_name")["final_amount_inr"].sum().nlargest(15).reset_index()
    fig16 = px.bar(prod, x="final_amount_inr", y="product_name",
                   orientation="h", color="final_amount_inr",
                   color_continuous_scale="Oranges",
                   labels={"final_amount_inr":"Revenue (₹)","product_name":"Product"})
    fig16.update_layout(showlegend=False, coloraxis_showscale=False,
                        yaxis=dict(autorange="reversed"))
    pc(layout(fig16, 520))

    c1, c2 = st.columns(2)

    # ── Chart 17 — Brand bar ──────────────────────────────────────────────────
    with c1:
        sh("🏷️ Chart 17 — Top 10 Brands by Revenue")
        brand = df.groupby("brand")["final_amount_inr"].sum().nlargest(10).reset_index()
        fig17 = px.bar(brand, x="brand", y="final_amount_inr",
                       color="final_amount_inr", color_continuous_scale="Viridis",
                       labels={"final_amount_inr":"Revenue (₹)","brand":"Brand"})
        fig17.update_layout(showlegend=False, coloraxis_showscale=False)
        fig17.update_xaxes(tickangle=30)
        pc(layout(fig17, 400))

    # ── Chart 18 — Ratings box plot ───────────────────────────────────────────
    with c2:
        sh("⭐ Chart 18 — Rating Distribution by Category")
        top6 = df.groupby("category")["transaction_id"].count().nlargest(6).index
        df_box = df[df["category"].isin(top6)].copy()
        df_box["product_rating"] = pd.to_numeric(df_box["product_rating"], errors="coerce")
        fig18 = px.box(df_box.dropna(subset=["product_rating"]),
                       x="category", y="product_rating",
                       color="category", color_discrete_sequence=CAT_COLORS,
                       notched=True,
                       labels={"product_rating":"Rating (1–5)","category":"Category"})
        fig18.update_layout(showlegend=False)
        pc(layout(fig18, 400))

    # ── Chart 19 — Category lifecycle ────────────────────────────────────────
    sh("📈 Chart 19 — Category Revenue Lifecycle (2015-2025)")
    yr_cat = df.groupby(["order_year","category"])["final_amount_inr"].sum().reset_index()
    top6c  = df.groupby("category")["final_amount_inr"].sum().nlargest(6).index
    fig19  = px.line(yr_cat[yr_cat["category"].isin(top6c)],
                     x="order_year", y="final_amount_inr",
                     color="category", markers=True,
                     color_discrete_sequence=CAT_COLORS,
                     labels={"final_amount_inr":"Revenue (₹)","order_year":"Year"})
    pc(layout(fig19, 400))

    # ── Chart 20 — Price vs demand scatter ────────────────────────────────────
    sh("💲 Chart 20 — Price Range vs Demand")
    df4 = df.copy()
    df4["price_bucket"] = pd.cut(
        pd.to_numeric(df4["original_price_inr"], errors="coerce"),
        bins=[0,500,1000,2000,5000,10000,50000,1e9],
        labels=["<₹500","₹500-1K","₹1K-2K","₹2K-5K","₹5K-10K","₹10K-50K","₹50K+"])
    dem = df4.groupby("price_bucket", observed=True).agg(
        orders=("transaction_id","count"),
        revenue=("final_amount_inr","sum")).reset_index()

    fig20 = px.scatter(dem, x="orders", y="revenue",
                       size="orders", color="price_bucket",
                       text="price_bucket",
                       color_discrete_sequence=px.colors.sequential.Oranges[1:],
                       labels={"orders":"Order Volume","revenue":"Revenue (₹)"},
                       title="Order Volume vs Revenue by Price Bucket")
    fig20.update_traces(textposition="top center")
    pc(layout(fig20, 420))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — OPERATIONS & LOGISTICS  (Charts 21-25)
# ══════════════════════════════════════════════════════════════════════════════
def page_operations(df):
    st.title("🚚 Operations & Logistics")
    st.caption("Delivery, returns, payment trends and customer satisfaction analysis")

    # ── Chart 21 — Delivery distribution ─────────────────────────────────────
    sh("📦 Chart 21 — Delivery Time Distribution")
    d_col = pd.to_numeric(df["delivery_days"], errors="coerce").dropna()

    c21a, c21b = st.columns(2)
    with c21a:
        fig21a = px.histogram(d_col.clip(upper=d_col.quantile(0.97)),
                              nbins=30, color_discrete_sequence=[P["orange"]],
                              labels={"value":"Delivery Days"},
                              title="Delivery Days Frequency")
        fig21a.add_vline(x=d_col.mean(), line_dash="dash", line_color=P["success"],
                         annotation_text=f"Mean {d_col.mean():.1f}d")
        pc(layout(fig21a, 360))

    with c21b:
        cd = df.groupby("customer_city").agg(
            avg=("delivery_days","mean"), n=("transaction_id","count")).reset_index()
        cd = cd[cd["n"]>30].nsmallest(10,"avg")
        fig21b = px.bar(cd, x="avg", y="customer_city", orientation="h",
                        color="avg", color_continuous_scale="Greens",
                        labels={"avg":"Avg Delivery Days","customer_city":"City"},
                        title="Fastest Delivery Cities")
        fig21b.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
        pc(layout(fig21b, 360))

    # ── Chart 22 — Payment trend stacked area ─────────────────────────────────
    sh("💳 Chart 22 — Payment Method Market Share Over Time")
    py = df.groupby(["order_year","payment_method"]).size().reset_index(name="cnt")
    py["pct"] = py.groupby("order_year")["cnt"].transform(lambda x: x/x.sum()*100)
    top_p = py.groupby("payment_method")["cnt"].sum().nlargest(5).index
    py5 = py[py["payment_method"].isin(top_p)]

    fig22 = px.area(py5, x="order_year", y="pct", color="payment_method",
                    color_discrete_sequence=CAT_COLORS,
                    labels={"pct":"Share %","order_year":"Year","payment_method":"Method"},
                    title="UPI vs Card vs COD — Evolution 2015-2025")
    pc(layout(fig22, 420))

    c1, c2 = st.columns(2)

    # ── Chart 23 — Return rate by category ────────────────────────────────────
    with c1:
        sh("↩️ Chart 23 — Return Rate by Category")
        if "return_status" in df.columns:
            ret = df.groupby("category").apply(
                lambda x: pd.Series({
                    "rate": x["return_status"].str.lower().str.contains("return",na=False).mean()*100,
                    "n": len(x)
                })).reset_index()
            ret = ret[ret["n"]>50].sort_values("rate", ascending=False)
            fig23 = px.bar(ret, x="rate", y="category", orientation="h",
                           color="rate", color_continuous_scale="Reds",
                           labels={"rate":"Return Rate %","category":"Category"})
            fig23.update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
            pc(layout(fig23, 360))

    # ── Chart 24 — Rating vs Delivery scatter ─────────────────────────────────
    with c2:
        sh("😊 Chart 24 — Customer Rating vs Delivery Speed")
        if "customer_rating" in df.columns:
            s = df.sample(min(2500,len(df)), random_state=42).copy()
            s["customer_rating"] = pd.to_numeric(s["customer_rating"], errors="coerce")
            s["del_n"] = pd.to_numeric(s.get("delivery_days",0), errors="coerce")
            s = s.dropna(subset=["customer_rating","del_n"])
            fig24 = px.scatter(s, x="del_n", y="customer_rating", color="category",
                               opacity=0.45, color_discrete_sequence=CAT_COLORS,
                               labels={"del_n":"Delivery Days","customer_rating":"Rating"},
                               title="Faster Delivery → Higher Rating?")
            fig24.update_layout(showlegend=False)
            pc(layout(fig24, 360))

    # ── Chart 25 — Free vs Paid delivery ──────────────────────────────────────
    sh("💸 Chart 25 — Free vs Paid Delivery Impact on AOV")
    if "delivery_charges" in df.columns:
        df5 = df.copy()
        df5["del_type"] = df5["delivery_charges"].apply(
            lambda x: "🚀 Free Delivery" if float(str(x) if str(x).replace(".","").isdigit() else 0)==0 else "💰 Paid Delivery")
        dc_agg = df5.groupby("del_type").agg(
            orders=("transaction_id","count"),
            aov=("final_amount_inr","mean"),
            rev=("final_amount_inr","sum")).reset_index()

        fig25 = make_subplots(rows=1,cols=2,
                              subplot_titles=["Order Volume","Avg Order Value (₹)"])
        for i,col in enumerate(["orders","aov"],1):
            fig25.add_trace(go.Bar(x=dc_agg["del_type"], y=dc_agg[col],
                                   marker_color=[P["success"],P["danger"]],
                                   opacity=0.88, name=col), row=1, col=i)
        fig25.update_layout(showlegend=False)
        pc(layout(fig25, 380))


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — ADVANCED ANALYTICS  (Charts 26-30)
# ══════════════════════════════════════════════════════════════════════════════
def page_advanced(df):
    st.title("🔬 Advanced Analytics")
    st.caption("Revenue forecast, correlation matrix, market penetration and BI command centre")

    # ── Chart 26 — Revenue Forecast ───────────────────────────────────────────
    sh("🔮 Chart 26 — Revenue Trend + 3-Year Projection")
    yr = df.groupby("order_year")["final_amount_inr"].sum().reset_index()
    yr.columns = ["year","revenue"]
    x, y = yr["year"].values, yr["revenue"].values
    coefs = np.polyfit(x, y, 1)
    fut = np.array([2026,2027,2028])
    pred = np.polyval(coefs, fut)

    fig26 = go.Figure()
    fig26.add_trace(go.Scatter(x=x, y=y/1e7, mode="lines+markers",
                               name="Actual", line=dict(color=P["orange"],width=2.5),
                               marker=dict(size=9)))
    trend_x = np.concatenate([x, fut])
    fig26.add_trace(go.Scatter(x=trend_x, y=np.polyval(coefs,trend_x)/1e7,
                               mode="lines", name="Trend",
                               line=dict(color=P["success"],dash="dash",width=2)))
    fig26.add_trace(go.Scatter(x=fut, y=pred/1e7, mode="markers",
                               name="Forecast", marker=dict(color=P["danger"],size=12,symbol="diamond")))
    fig26.add_vrect(x0=2025.5,x1=2028.5,fillcolor=P["danger"],opacity=0.05,
                    annotation_text="Projected",annotation_position="top left")
    fig26.update_layout(title="Revenue Forecast (Linear Trend)",
                        xaxis_title="Year", yaxis_title="Revenue (₹ Crore)")
    pc(layout(fig26, 420))

    c1, c2 = st.columns(2)

    # ── Chart 27 — Digital payment adoption ──────────────────────────────────
    with c1:
        sh("📡 Chart 27 — Digital Payment Adoption Curve")
        py = df.groupby(["order_year","payment_method"]).size().reset_index(name="cnt")
        py["pct"] = py.groupby("order_year")["cnt"].transform(lambda x: x/x.sum()*100)
        dig = py[py["payment_method"].isin(["UPI","Credit Card","Amazon Pay"])]
        fig27 = px.line(dig, x="order_year", y="pct", color="payment_method",
                        markers=True,
                        color_discrete_map={"UPI":P["orange"],"Credit Card":P["info"],"Amazon Pay":P["success"]},
                        labels={"pct":"Share %","order_year":"Year"})
        pc(layout(fig27, 400))

    # ── Chart 28 — Category correlation heatmap ───────────────────────────────
    with c2:
        sh("🔗 Chart 28 — Category Revenue Correlation")
        yr_cat_piv = (df.groupby(["order_year","category"])["final_amount_inr"]
                        .sum().reset_index()
                        .pivot(index="order_year",columns="category",values="final_amount_inr")
                        .fillna(0))
        corr = yr_cat_piv.corr()
        fig28 = px.imshow(corr, text_auto=".2f", aspect="auto",
                          color_continuous_scale="RdYlGn",
                          title="Cross-Category Revenue Correlation")
        pc(layout(fig28, 400))

    # ── Chart 29 — State revenue map (bar) ────────────────────────────────────
    sh("🗺️ Chart 29 — Revenue by State")
    state_rev = df.groupby("customer_state")["final_amount_inr"].sum().nlargest(12).reset_index()
    fig29 = px.bar(state_rev, x="customer_state", y="final_amount_inr",
                   color="final_amount_inr", color_continuous_scale="Oranges",
                   labels={"final_amount_inr":"Revenue (₹)","customer_state":"State"},
                   title="Top 12 States by Revenue")
    fig29.update_layout(coloraxis_showscale=False)
    fig29.update_xaxes(tickangle=30)
    pc(layout(fig29, 400))

    # ── Chart 30 — BI Command Centre ──────────────────────────────────────────
    sh("🎛️ Chart 30 — BI Command Centre: 4-Panel Business Health")
    yr_data = df.groupby("order_year").agg(
        revenue=("final_amount_inr","sum"),
        orders=("transaction_id","count"),
        customers=("customer_id","nunique"),
        aov=("final_amount_inr","mean"),
    ).reset_index()

    fig30 = make_subplots(rows=2, cols=2,
                          subplot_titles=["Revenue (₹ Cr)","Order Volume",
                                          "Unique Customers","Avg Order Value (₹)"])
    colors30 = [P["orange"],P["teal"],P["success"],P["purple"]]
    scales30  = [1e7, 1, 1, 1]
    for idx,(col,sc,clr) in enumerate(zip(["revenue","orders","customers","aov"],scales30,colors30)):
        r,c = divmod(idx,2)
        fig30.add_trace(go.Scatter(
            x=yr_data["order_year"], y=yr_data[col]/sc,
            mode="lines+markers",
            line=dict(color=clr,width=2.5), marker=dict(size=8),
            name=col, fill="tozeroy", fillcolor=clr.replace("#","") and clr+"22",
        ), row=r+1, col=c+1)
    fig30.update_layout(showlegend=False, title_text="Complete Business Overview 2015-2025")
    pc(layout(fig30, 560))

    # Summary stats table
    st.markdown("---")
    sh("📋 Key Metrics Summary Table")
    summary = df.groupby("order_year").agg(
        Revenue=("final_amount_inr","sum"),
        Orders=("transaction_id","count"),
        Customers=("customer_id","nunique"),
        AOV=("final_amount_inr","mean"),
        Avg_Rating=("product_rating","mean"),
        Avg_Delivery=("delivery_days","mean"),
    ).reset_index()
    summary["Revenue"] = summary["Revenue"].apply(lambda x: f"₹{x/1e7:.2f} Cr")
    summary["AOV"] = summary["AOV"].apply(lambda x: f"₹{x:,.0f}")
    summary["Avg_Rating"] = summary["Avg_Rating"].apply(lambda x: f"{x:.2f} ⭐")
    summary["Avg_Delivery"] = summary["Avg_Delivery"].apply(lambda x: f"{x:.1f} days")
    summary.columns = ["Year","Revenue","Orders","Customers","Avg Order","Avg Rating","Avg Delivery"]
    st.dataframe(summary, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    df, page = sidebar(df_all)

    router = {
        "📊 Executive Dashboard"   : page_executive,
        "💰 Revenue & Seasonality" : page_revenue,
        "👥 Customer Intelligence" : page_customers,
        "📦 Product & Brand"       : page_products,
        "🚚 Operations & Logistics": page_operations,
        "🔬 Advanced Analytics"    : page_advanced,
    }
    router[page](df)

    st.markdown("---")
    st.markdown(f"""<div style='text-align:center;color:{P['muted']};font-size:.72rem;padding:8px 0'>
    🛒 <strong style='color:{P['orange']}'>Amazon India: A Decade of Sales Analytics</strong>
     · GUVI HCL Fullstack Data Science Program · Built with Streamlit + Plotly
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
