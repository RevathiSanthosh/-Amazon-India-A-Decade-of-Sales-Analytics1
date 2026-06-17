"""
eda/eda_visualizations.py
--------------------------
All 20 EDA visualization challenges.
Every chart saved as a high-res PNG in outputs/eda/.

Run standalone:
    python eda/eda_visualizations.py
"""

import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
import matplotlib.patheffects as pe
import seaborn as sns
from pathlib import Path

from config.settings import EDA_DIR, PALETTE, MONTHS, FESTIVAL_MONTHS, CAT_COLORS

P = PALETTE
EDA_DIR.mkdir(parents=True, exist_ok=True)

# ── Global Matplotlib theme ────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": P["dark_bg"],  "axes.facecolor"  : P["card_bg"],
    "axes.edgecolor"  : P["border"],   "axes.labelcolor" : P["text"],
    "xtick.color"     : P["muted"],    "ytick.color"     : P["muted"],
    "text.color"      : P["text"],     "grid.color"      : P["border"],
    "grid.linestyle"  : "--",          "grid.linewidth"  : 0.4,
    "font.family"     : "DejaVu Sans", "axes.titlesize"  : 13,
    "axes.titleweight": "bold",        "axes.titlecolor" : P["orange"],
    "legend.facecolor": P["card_bg"],  "legend.edgecolor": P["border"],
    "figure.dpi"      : 120,
})

def _save(fig, name):
    p = EDA_DIR / name
    fig.savefig(p, dpi=150, bbox_inches="tight", facecolor=P["dark_bg"])
    plt.close(fig)
    print(f"   💾 {name}")
    return p

def _ax_style(ax, title="", xlabel="", ylabel=""):
    if title:  ax.set_title(title, color=P["orange"], pad=10)
    if xlabel: ax.set_xlabel(xlabel, color=P["muted"])
    if ylabel: ax.set_ylabel(ylabel, color=P["muted"])
    ax.grid(axis="y", alpha=0.25)
    ax.spines[["top","right"]].set_visible(False)

def _fig(w=14, h=7, title=""):
    fig = plt.figure(figsize=(w, h))
    fig.patch.set_facecolor(P["dark_bg"])
    if title:
        fig.suptitle(title, fontsize=15, color=P["orange"], fontweight="bold", y=1.02)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Q1 — REVENUE TREND 2015-2025
# ══════════════════════════════════════════════════════════════════════════════
def q1_revenue_trend(df):
    yr = df.groupby("order_year")["final_amount_inr"].sum().reset_index()
    yr["growth"] = yr["final_amount_inr"].pct_change() * 100
    yr["rev_cr"] = yr["final_amount_inr"] / 1e7

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9),
                                    gridspec_kw={"height_ratios":[2.5,1]}, facecolor=P["dark_bg"])
    fig.suptitle("📈  Annual Revenue Trend — Amazon India 2015-2025",
                 fontsize=15, color=P["orange"], fontweight="bold")

    colors = [P["orange"] if y >= 2020 else P["teal"] for y in yr["order_year"]]
    bars = ax1.bar(yr["order_year"], yr["rev_cr"], color=colors, edgecolor=P["dark_bg"],
                   linewidth=1.2, alpha=0.9, width=0.65)
    ax1.plot(yr["order_year"], yr["rev_cr"], "o-", color=P["light_orange"],
             lw=2, ms=8, zorder=6)

    for bar, val in zip(bars, yr["rev_cr"]):
        ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1,
                 f"₹{val:.1f}Cr", ha="center", va="bottom", fontsize=8.5,
                 color="white", fontweight="bold")

    ax1.fill_between(yr["order_year"], yr["rev_cr"], alpha=0.07, color=P["orange"])
    ax1.set_facecolor(P["card_bg"]); ax1.set_ylabel("Revenue (₹ Crore)", color=P["muted"])
    ax1.set_title("Yearly Revenue (₹ Crore)  |  Orange = post-2020", color=P["orange"])
    ax1.grid(axis="y", alpha=0.2); ax1.spines[["top","right"]].set_visible(False)

    col_g = [P["success"] if x >= 0 else P["danger"] for x in yr["growth"].fillna(0)]
    ax2.bar(yr["order_year"], yr["growth"].fillna(0), color=col_g, alpha=0.85, width=0.65)
    ax2.axhline(0, color="white", lw=0.8, ls="--")
    ax2.set_facecolor(P["card_bg"]); ax2.set_ylabel("YoY Growth %", color=P["muted"])
    ax2.set_title("Year-over-Year Growth Rate", color=P["orange"])
    ax2.grid(axis="y", alpha=0.2); ax2.spines[["top","right"]].set_visible(False)

    fig.tight_layout()
    return _save(fig, "q01_revenue_trend.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q2 — SEASONAL HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
def q2_seasonal_heatmap(df):
    pivot = (df.groupby(["order_year","order_month"])["final_amount_inr"]
               .sum().reset_index()
               .pivot(index="order_year", columns="order_month", values="final_amount_inr")
               .fillna(0))
    pivot.columns = MONTHS[:len(pivot.columns)]

    fig, ax = plt.subplots(figsize=(15, 7), facecolor=P["dark_bg"])
    fig.suptitle("🗓️  Seasonal Revenue Heatmap — Monthly Patterns by Year",
                 fontsize=14, color=P["orange"], fontweight="bold")

    sns.heatmap(pivot/1e5, annot=True, fmt=".1f", cmap="YlOrRd",
                linewidths=0.5, linecolor=P["dark_bg"], ax=ax, cbar=True,
                cbar_kws={"label":"Revenue (₹ Lakhs)","shrink":0.7},
                annot_kws={"size":9,"color":"black"})
    ax.set_xlabel("Month", color=P["muted"])
    ax.set_ylabel("Year", color=P["muted"])
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    return _save(fig, "q02_seasonal_heatmap.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q3 — RFM SEGMENTATION
# ══════════════════════════════════════════════════════════════════════════════
def q3_rfm_segmentation(df):
    snap = df["order_date_dt"].max()
    rfm = df.groupby("customer_id").agg(
        R=("order_date_dt", lambda x: (snap-x.max()).days),
        F=("transaction_id","count"),
        M=("final_amount_inr","sum"),
    ).reset_index()

    def safe_qcut(series, n, ascending=True):
        try:
            lbls = list(range(1,n+1)) if ascending else list(range(n,0,-1))
            return pd.qcut(series, n, labels=lbls, duplicates="drop")
        except Exception:
            # fallback: rank-based ntile
            n_bins = min(n, series.nunique())
            lbls = list(range(1, n_bins+1)) if ascending else list(range(n_bins,0,-1))
            return pd.qcut(series.rank(method="first"), n_bins, labels=lbls, duplicates="drop")

    rfm["Rs"] = safe_qcut(rfm["R"], 5, ascending=True)
    rfm["Fs"] = safe_qcut(rfm["F"], 5, ascending=False)
    rfm["Ms"] = safe_qcut(rfm["M"], 5, ascending=False)
    rfm = rfm.dropna(subset=["Rs","Fs","Ms"])
    rfm["score"] = rfm["Rs"].astype(int)+rfm["Fs"].astype(int)+rfm["Ms"].astype(int)
    rfm["segment"] = rfm["score"].apply(
        lambda s: "Champions" if s>=13 else ("Loyal" if s>=10 else ("At Risk" if s>=7 else "Dormant")))

    seg_c = {"Champions":P["orange"],"Loyal":P["success"],"At Risk":P["info"],"Dormant":P["danger"]}
    sample = rfm.sample(min(2000,len(rfm)), random_state=42)

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), facecolor=P["dark_bg"])
    fig.suptitle("🎯  Customer RFM Segmentation Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    for seg, grp in sample.groupby("segment"):
        axes[0].scatter(grp["F"], grp["M"]/1000, alpha=0.4, s=18,
                        label=f"{seg} ({len(rfm[rfm.segment==seg]):,})",
                        color=seg_c.get(seg, P["muted"]))
    axes[0].set_facecolor(P["card_bg"])
    axes[0].set_xlabel("Frequency (Orders)", color=P["muted"])
    axes[0].set_ylabel("Monetary (₹ Thousands)", color=P["muted"])
    axes[0].set_title("Frequency vs Monetary by Segment", color=P["orange"])
    axes[0].legend(fontsize=8, markerscale=2)
    axes[0].grid(alpha=0.2); axes[0].spines[["top","right"]].set_visible(False)

    seg_cnt = rfm["segment"].value_counts()
    colors_s = [seg_c.get(s, P["muted"]) for s in seg_cnt.index]
    wedges, texts, autos = axes[1].pie(seg_cnt, labels=seg_cnt.index, autopct="%1.1f%%",
                                        colors=colors_s, pctdistance=0.78,
                                        wedgeprops={"edgecolor":P["dark_bg"],"linewidth":2})
    for a in autos: a.set_color("white"); a.set_fontsize(9)
    axes[1].add_patch(plt.Circle((0,0),0.52,color=P["card_bg"]))
    axes[1].set_title("Segment Distribution", color=P["orange"])
    axes[1].set_facecolor(P["dark_bg"])

    fig.tight_layout()
    return _save(fig, "q03_rfm_segmentation.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q4 — PAYMENT METHOD EVOLUTION
# ══════════════════════════════════════════════════════════════════════════════
def q4_payment_evolution(df):
    py = df.groupby(["order_year","payment_method"]).size().reset_index(name="cnt")
    py["pct"] = py.groupby("order_year")["cnt"].transform(lambda x: x/x.sum()*100)
    pivot = py.pivot(index="order_year", columns="payment_method", values="pct").fillna(0)
    top = pivot.sum().nlargest(6).index
    pivot = pivot[top]

    colors = [P["orange"],P["info"],P["success"],P["danger"],P["purple"],P["teal"]]
    fig, ax = plt.subplots(figsize=(14, 7), facecolor=P["dark_bg"])
    fig.suptitle("💳  Payment Method Evolution — Rise of UPI (2015-2025)",
                 fontsize=14, color=P["orange"], fontweight="bold")

    pivot.plot.area(ax=ax, color=colors[:len(top)], alpha=0.82, linewidth=1.8)
    ax.set_facecolor(P["card_bg"]); ax.set_xlabel("Year", color=P["muted"])
    ax.set_ylabel("Market Share %", color=P["muted"])
    ax.set_title("Stacked Area — Share of Each Payment Method per Year", color=P["orange"])
    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
    ax.legend(loc="upper left", fontsize=9, framealpha=0.4)
    ax.grid(axis="y", alpha=0.2); ax.spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "q04_payment_evolution.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q5 — CATEGORY PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
def q5_category_perf(df):
    cat = df.groupby("category")["final_amount_inr"].agg(
        revenue="sum", orders="count", aov="mean").reset_index()
    cat["share"] = cat["revenue"]/cat["revenue"].sum()*100
    cat = cat.sort_values("revenue", ascending=False)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor=P["dark_bg"])
    fig.suptitle("🛍️  Category Performance Dashboard", fontsize=14,
                 color=P["orange"], fontweight="bold")

    c = plt.cm.Oranges(np.linspace(0.35,0.95,len(cat)))
    axes[0].barh(cat["category"][::-1], cat["revenue"][::-1]/1e5, color=c[::-1], edgecolor=P["dark_bg"])
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_xlabel("Revenue (₹ Lakhs)", color=P["muted"])
    axes[0].set_title("Revenue by Category", color=P["orange"])
    axes[0].spines[["top","right"]].set_visible(False)

    wedges,texts,autos = axes[1].pie(cat["share"], labels=cat["category"], autopct="%1.1f%%",
                                      colors=c, pctdistance=0.80,
                                      wedgeprops={"edgecolor":P["dark_bg"],"linewidth":1.5})
    for a in autos: a.set_color("white"); a.set_fontsize(8)
    axes[1].add_patch(plt.Circle((0,0),0.55,color=P["card_bg"]))
    axes[1].set_title("Revenue Share %", color=P["orange"])
    axes[1].set_facecolor(P["dark_bg"])

    axes[2].bar(cat["category"], cat["aov"], color=c, edgecolor=P["dark_bg"])
    axes[2].set_facecolor(P["card_bg"]); axes[2].set_xlabel("Category", color=P["muted"])
    axes[2].set_ylabel("Avg Order Value ₹", color=P["muted"])
    axes[2].set_title("Average Order Value", color=P["orange"])
    axes[2].tick_params(axis="x", rotation=30)
    axes[2].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "q05_category_performance.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q6 — PRIME MEMBERSHIP IMPACT
# ══════════════════════════════════════════════════════════════════════════════
def q6_prime_impact(df):
    df2 = df.copy()
    df2["Prime"] = df2["is_prime_member"].apply(
        lambda x: "Prime ⭐" if str(x).lower() in ["true","1","yes"] else "Non-Prime")

    agg = df2.groupby("Prime").agg(
        aov=("final_amount_inr","mean"),
        orders=("transaction_id","count"),
        revenue=("final_amount_inr","sum"),
        avg_rating=("customer_rating","mean"),
    ).reset_index()

    fig, axes = plt.subplots(1, 3, figsize=(16, 6), facecolor=P["dark_bg"])
    fig.suptitle("⭐  Prime Membership Impact Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")
    metrics = [("aov","Avg Order Value (₹)"),("orders","Order Count"),("revenue","Revenue (₹)")]
    pal = {"Prime ⭐":P["orange"],"Non-Prime":P["teal"]}
    for ax, (col, title) in zip(axes, metrics):
        colors = [pal[p] for p in agg["Prime"]]
        bars = ax.bar(agg["Prime"], agg[col], color=colors, edgecolor=P["dark_bg"], alpha=0.9, width=0.5)
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x()+bar.get_width()/2, h*1.02,
                    f"₹{h:,.0f}" if col!="orders" else f"{h:,}",
                    ha="center", va="bottom", fontsize=9, color="white", fontweight="bold")
        ax.set_facecolor(P["card_bg"]); ax.set_title(title, color=P["orange"])
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q06_prime_impact.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q7 — GEOGRAPHIC ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def q7_geographic(df):
    city = df.groupby("customer_city").agg(
        revenue=("final_amount_inr","sum"),
        orders=("transaction_id","count"),
    ).reset_index().nlargest(15,"revenue")

    fig, axes = plt.subplots(1, 2, figsize=(16, 8), facecolor=P["dark_bg"])
    fig.suptitle("🗺️  Geographic Revenue Analysis — Top Indian Cities",
                 fontsize=14, color=P["orange"], fontweight="bold")

    c = plt.cm.plasma(np.linspace(0.2,0.9,len(city)))
    axes[0].barh(city["customer_city"][::-1], city["revenue"][::-1]/1e5, color=c, edgecolor=P["dark_bg"])
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_xlabel("Revenue (₹ Lakhs)", color=P["muted"])
    axes[0].set_title("Top 15 Cities — Total Revenue", color=P["orange"])
    axes[0].spines[["top","right"]].set_visible(False)

    axes[1].barh(city["customer_city"][::-1], city["orders"][::-1], color=c, edgecolor=P["dark_bg"])
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_xlabel("Number of Orders", color=P["muted"])
    axes[1].set_title("Top 15 Cities — Order Volume", color=P["orange"])
    axes[1].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "q07_geographic.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q8 — FESTIVAL IMPACT
# ══════════════════════════════════════════════════════════════════════════════
def q8_festival_impact(df):
    df2 = df.copy()
    df2["is_fest"] = df2.get("is_festival_sale", pd.Series(False)).apply(
        lambda x: str(x).lower() in ["true","1","yes"])

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=P["dark_bg"])
    fig.suptitle("🎉  Festival Sales Impact Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    fest_agg = df2.groupby("is_fest")["final_amount_inr"].agg(
        ["sum","mean","count"]).reset_index()
    fest_agg["label"] = fest_agg["is_fest"].map({True:"Festival 🎊",False:"Regular"})
    bars = axes[0].bar(fest_agg["label"], fest_agg["sum"]/1e5,
                       color=[P["orange"],P["teal"]], edgecolor=P["dark_bg"], width=0.4)
    for bar in bars:
        h = bar.get_height()
        axes[0].text(bar.get_x()+bar.get_width()/2, h*1.02,
                     f"₹{h:.1f}L", ha="center", va="bottom", fontsize=10,
                     color="white", fontweight="bold")
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_ylabel("Revenue (₹ Lakhs)", color=P["muted"])
    axes[0].set_title("Festival vs Non-Festival Revenue", color=P["orange"])
    axes[0].spines[["top","right"]].set_visible(False); axes[0].grid(axis="y", alpha=0.2)

    mo_rev = df.groupby("order_month")["final_amount_inr"].mean().reset_index()
    c_mo = [P["orange"] if m in FESTIVAL_MONTHS else P["teal"] for m in mo_rev["order_month"]]
    axes[1].bar([MONTHS[m-1] for m in mo_rev["order_month"]], mo_rev["final_amount_inr"]/1000,
                color=c_mo, edgecolor=P["dark_bg"], alpha=0.9)
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_xlabel("Month", color=P["muted"])
    axes[1].set_ylabel("Avg Revenue (₹ Thousands)", color=P["muted"])
    axes[1].set_title("Monthly Revenue  |  🟠 Festival Months", color=P["orange"])
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].spines[["top","right"]].set_visible(False); axes[1].grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q08_festival_impact.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q9 — AGE GROUP ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def q9_age_analysis(df):
    if "age_group" not in df.columns:
        return

    age_cat = df.groupby(["age_group","category"])["final_amount_inr"].sum().reset_index()
    pivot = age_cat.pivot(index="age_group", columns="category", values="final_amount_inr").fillna(0)
    pivot_norm = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor=P["dark_bg"])
    fig.suptitle("👥  Age Group Behavior & Spending Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    colors_s = plt.cm.Set2(np.linspace(0,1,pivot_norm.shape[1]))
    bottom = np.zeros(len(pivot_norm))
    for i, col in enumerate(pivot_norm.columns):
        axes[0].bar(pivot_norm.index, pivot_norm[col], bottom=bottom,
                    label=col, color=colors_s[i], alpha=0.88)
        bottom += pivot_norm[col].values
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_ylabel("Revenue Share %", color=P["muted"])
    axes[0].set_title("Category Preference by Age Group", color=P["orange"])
    axes[0].legend(fontsize=7, loc="upper right", framealpha=0.3)
    axes[0].yaxis.set_major_formatter(mticker.PercentFormatter())
    axes[0].spines[["top","right"]].set_visible(False)

    age_spend = df.groupby("age_group")["final_amount_inr"].mean().sort_values(ascending=False)
    c = plt.cm.Oranges(np.linspace(0.4,1.0,len(age_spend)))
    bars = axes[1].bar(age_spend.index, age_spend.values, color=c, edgecolor=P["dark_bg"])
    for bar in bars:
        h = bar.get_height()
        axes[1].text(bar.get_x()+bar.get_width()/2, h*1.01,
                     f"₹{h:,.0f}", ha="center", va="bottom", fontsize=8, color="white")
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_ylabel("Avg Order Value (₹)", color=P["muted"])
    axes[1].set_title("Average Spending per Order by Age Group", color=P["orange"])
    axes[1].spines[["top","right"]].set_visible(False); axes[1].grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q09_age_analysis.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q10 — PRICE VS DEMAND
# ══════════════════════════════════════════════════════════════════════════════
def q10_price_demand(df):
    bins   = [0,500,1000,2000,5000,10000,50000,1e9]
    labels = ["<₹500","₹500-1K","₹1K-2K","₹2K-5K","₹5K-10K","₹10K-50K","₹50K+"]
    df2 = df.copy()
    df2["bucket"] = pd.cut(pd.to_numeric(df2["original_price_inr"],errors="coerce"),
                           bins=bins, labels=labels)
    agg = df2.groupby("bucket",observed=True).agg(
        orders=("transaction_id","count"),
        revenue=("final_amount_inr","sum"),
        aov=("final_amount_inr","mean"),
    ).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(15, 6), facecolor=P["dark_bg"])
    fig.suptitle("💰  Price vs Demand Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    c = plt.cm.YlOrRd(np.linspace(0.3,1.0,len(agg)))
    axes[0].bar(agg["bucket"], agg["orders"], color=c, edgecolor=P["dark_bg"])
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_xlabel("Price Range", color=P["muted"])
    axes[0].set_ylabel("Orders", color=P["muted"])
    axes[0].set_title("Order Volume by Price Range", color=P["orange"])
    axes[0].tick_params(axis="x", rotation=30)
    axes[0].spines[["top","right"]].set_visible(False); axes[0].grid(axis="y", alpha=0.2)

    axes[1].bar(agg["bucket"], agg["revenue"]/1e5, color=c, edgecolor=P["dark_bg"])
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_xlabel("Price Range", color=P["muted"])
    axes[1].set_ylabel("Revenue (₹ Lakhs)", color=P["muted"])
    axes[1].set_title("Revenue by Price Range", color=P["orange"])
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].spines[["top","right"]].set_visible(False); axes[1].grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q10_price_demand.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q11 — DELIVERY PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
def q11_delivery(df):
    d = pd.to_numeric(df["delivery_days"],errors="coerce").dropna()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=P["dark_bg"])
    fig.suptitle("🚚  Delivery Performance Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    axes[0].hist(d.clip(upper=d.quantile(0.97)), bins=35,
                 color=P["orange"], edgecolor=P["dark_bg"], alpha=0.85)
    axes[0].axvline(d.mean(), color=P["success"], lw=2, ls="--",
                    label=f"Mean: {d.mean():.1f}d")
    axes[0].axvline(d.median(), color=P["danger"], lw=2, ls="--",
                    label=f"Median: {d.median():.1f}d")
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_xlabel("Delivery Days", color=P["muted"])
    axes[0].set_ylabel("Frequency", color=P["muted"])
    axes[0].set_title("Delivery Days Distribution", color=P["orange"])
    axes[0].legend(); axes[0].spines[["top","right"]].set_visible(False)
    axes[0].grid(axis="y", alpha=0.2)

    city_del = (df.groupby("customer_city")
                  .agg(avg=("delivery_days","mean"), n=("transaction_id","count"))
                  .reset_index())
    city_del = city_del[city_del["n"]>30].nsmallest(10,"avg")
    c = plt.cm.Greens(np.linspace(0.4,0.9,len(city_del)))
    axes[1].barh(city_del["customer_city"][::-1], city_del["avg"][::-1], color=c, edgecolor=P["dark_bg"])
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_xlabel("Avg Delivery Days", color=P["muted"])
    axes[1].set_title("Fastest Delivery Cities", color=P["orange"])
    axes[1].spines[["top","right"]].set_visible(False)
    fig.tight_layout()
    return _save(fig, "q11_delivery.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q12 — RETURN RATE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def q12_returns(df):
    if "return_status" not in df.columns: return
    df2 = df.copy()
    df2["returned"] = df2["return_status"].str.lower().str.contains("return",na=False)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=P["dark_bg"])
    fig.suptitle("↩️  Return Rate Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    cat_ret = df2.groupby("category")["returned"].mean().sort_values(ascending=False)*100
    c = plt.cm.Reds(np.linspace(0.3,0.9,len(cat_ret)))
    axes[0].barh(cat_ret.index[::-1], cat_ret.values[::-1], color=c, edgecolor=P["dark_bg"])
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_xlabel("Return Rate %", color=P["muted"])
    axes[0].set_title("Return Rate by Category", color=P["orange"])
    axes[0].xaxis.set_major_formatter(mticker.PercentFormatter())
    axes[0].spines[["top","right"]].set_visible(False)

    bins_p = [0,500,2000,8000,1e9]; lbl_p = ["Budget","Mid","Premium","Luxury"]
    df2["seg"] = pd.cut(df2["original_price_inr"],bins=bins_p,labels=lbl_p)
    pr = df2.groupby("seg",observed=True)["returned"].mean()*100
    axes[1].bar(pr.index, pr.values, color=[P["success"],P["orange"],P["info"],P["danger"]],
                edgecolor=P["dark_bg"], alpha=0.9, width=0.5)
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_ylabel("Return Rate %", color=P["muted"])
    axes[1].set_title("Return Rate by Price Segment", color=P["orange"])
    axes[1].yaxis.set_major_formatter(mticker.PercentFormatter())
    axes[1].spines[["top","right"]].set_visible(False); axes[1].grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q12_returns.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q13 — BRAND PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
def q13_brands(df):
    brand = df.groupby("brand")["final_amount_inr"].sum().nlargest(12).reset_index()
    fig, ax = plt.subplots(figsize=(14, 6), facecolor=P["dark_bg"])
    fig.suptitle("🏷️  Top 12 Brands by Revenue", fontsize=14,
                 color=P["orange"], fontweight="bold")
    c = plt.cm.plasma(np.linspace(0.2,0.9,len(brand)))
    bars = ax.bar(brand["brand"], brand["final_amount_inr"]/1e5, color=c, edgecolor=P["dark_bg"])
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h*1.01, f"₹{h:.1f}L",
                ha="center", va="bottom", fontsize=8, color="white")
    ax.set_facecolor(P["card_bg"]); ax.set_ylabel("Revenue (₹ Lakhs)", color=P["muted"])
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("Revenue Ranking by Brand", color=P["orange"])
    ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q13_brands.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q14 — CUSTOMER LIFETIME VALUE
# ══════════════════════════════════════════════════════════════════════════════
def q14_clv(df):
    first_yr = df.groupby("customer_id")["order_year"].min().reset_index()
    first_yr.columns = ["customer_id","cohort"]
    clv = (df.merge(first_yr, on="customer_id")
             .groupby(["customer_id","cohort"])["final_amount_inr"]
             .sum().reset_index())
    cohort_agg = clv.groupby("cohort")["final_amount_inr"].agg(["median","mean"]).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=P["dark_bg"])
    fig.suptitle("💎  Customer Lifetime Value Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")

    axes[0].plot(cohort_agg["cohort"], cohort_agg["median"], "o-",
                 color=P["orange"], lw=2, ms=8, label="Median CLV")
    axes[0].plot(cohort_agg["cohort"], cohort_agg["mean"], "s--",
                 color=P["success"], lw=2, ms=7, label="Mean CLV")
    axes[0].fill_between(cohort_agg["cohort"], cohort_agg["median"], alpha=0.15, color=P["orange"])
    axes[0].set_facecolor(P["card_bg"]); axes[0].set_xlabel("Cohort Year", color=P["muted"])
    axes[0].set_ylabel("CLV (₹)", color=P["muted"])
    axes[0].set_title("CLV by Acquisition Cohort", color=P["orange"])
    axes[0].legend(); axes[0].spines[["top","right"]].set_visible(False)
    axes[0].grid(axis="y", alpha=0.2)

    cap = clv["final_amount_inr"].quantile(0.95)
    axes[1].hist(clv["final_amount_inr"].clip(upper=cap), bins=40,
                 color=P["teal"], edgecolor=P["dark_bg"], alpha=0.85)
    axes[1].axvline(clv["final_amount_inr"].median(), color=P["orange"], lw=2, ls="--",
                    label=f"Median: ₹{clv['final_amount_inr'].median():,.0f}")
    axes[1].set_facecolor(P["card_bg"]); axes[1].set_xlabel("Total Spend (₹)", color=P["muted"])
    axes[1].set_ylabel("Customers", color=P["muted"])
    axes[1].set_title("CLV Distribution (95th Pct cap)", color=P["orange"])
    axes[1].legend(); axes[1].spines[["top","right"]].set_visible(False)
    axes[1].grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q14_clv.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q15 — DISCOUNT EFFECTIVENESS
# ══════════════════════════════════════════════════════════════════════════════
def q15_discounts(df):
    df2 = df.copy()
    df2["disc_bucket"] = pd.cut(
        pd.to_numeric(df2["discount_percent"],errors="coerce").fillna(0),
        bins=[-1,0,10,20,30,50,100],
        labels=["0%","1-10%","11-20%","21-30%","31-50%","51%+"])
    agg = df2.groupby("disc_bucket",observed=True).agg(
        orders=("transaction_id","count"),
        revenue=("final_amount_inr","sum"),
        aov=("final_amount_inr","mean")).reset_index()

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), facecolor=P["dark_bg"])
    fig.suptitle("🏷️  Discount Effectiveness Analysis", fontsize=14,
                 color=P["orange"], fontweight="bold")
    c = plt.cm.RdYlGn(np.linspace(0.1,0.9,len(agg)))
    for ax, (col,title) in zip(axes,[("orders","Order Volume"),("revenue","Revenue (₹)"),("aov","AOV (₹)")]):
        vals = agg[col] if col=="orders" else agg[col]/(1e5 if col=="revenue" else 1)
        ax.bar(agg["disc_bucket"], vals, color=c, edgecolor=P["dark_bg"])
        ax.set_facecolor(P["card_bg"]); ax.set_xlabel("Discount Range", color=P["muted"])
        ax.set_ylabel(title, color=P["muted"]); ax.set_title(title, color=P["orange"])
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q15_discounts.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q16 — RATINGS IMPACT
# ══════════════════════════════════════════════════════════════════════════════
def q16_ratings(df):
    df2 = df.copy()
    df2["rat_bucket"] = pd.cut(
        pd.to_numeric(df2["product_rating"],errors="coerce"),
        bins=[0,2,3,4,4.5,5.01],labels=["1-2⭐","2-3⭐","3-4⭐","4-4.5⭐","4.5-5⭐"])
    agg = df2.groupby("rat_bucket",observed=True).agg(
        orders=("transaction_id","count"),
        revenue=("final_amount_inr","sum")).reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=P["dark_bg"])
    fig.suptitle("⭐  Product Rating Impact on Sales", fontsize=14,
                 color=P["orange"], fontweight="bold")
    c_r = [P["danger"],P["info"],P["teal"],P["success"],P["orange"]]
    for ax, (col,title) in zip(axes,[("orders","Order Volume"),("revenue","Revenue (₹L)")]):
        vals = agg[col] if col=="orders" else agg[col]/1e5
        ax.bar(agg["rat_bucket"], vals, color=c_r, edgecolor=P["dark_bg"], alpha=0.9)
        ax.set_facecolor(P["card_bg"]); ax.set_xlabel("Rating Range", color=P["muted"])
        ax.set_ylabel(title, color=P["muted"]); ax.set_title(title+" by Rating", color=P["orange"])
        ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q16_ratings.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q17 — PURCHASE FREQUENCY
# ══════════════════════════════════════════════════════════════════════════════
def q17_purchase_freq(df):
    freq = df.groupby("customer_id")["transaction_id"].count()
    cap  = freq.quantile(0.95)
    fig, ax = plt.subplots(figsize=(12, 6), facecolor=P["dark_bg"])
    fig.suptitle("🔄  Customer Purchase Frequency Distribution", fontsize=14,
                 color=P["orange"], fontweight="bold")
    ax.hist(freq.clip(upper=cap), bins=40, color=P["orange"], edgecolor=P["dark_bg"], alpha=0.85)
    ax.axvline(freq.mean(), color=P["success"], lw=2, ls="--",
               label=f"Mean: {freq.mean():.1f} orders")
    ax.axvline(freq.median(), color=P["danger"], lw=2, ls="--",
               label=f"Median: {freq.median():.0f} orders")
    ax.set_facecolor(P["card_bg"]); ax.set_xlabel("Orders per Customer", color=P["muted"])
    ax.set_ylabel("Number of Customers", color=P["muted"])
    ax.set_title("How Many Times Do Customers Buy?", color=P["orange"])
    ax.legend(); ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q17_purchase_freq.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q18 — CATEGORY LIFECYCLE
# ══════════════════════════════════════════════════════════════════════════════
def q18_category_lifecycle(df):
    yr_cat = df.groupby(["order_year","category"])["final_amount_inr"].sum().reset_index()
    pivot  = yr_cat.pivot(index="order_year",columns="category",values="final_amount_inr").fillna(0)
    top6   = pivot.sum().nlargest(6).index; pivot = pivot[top6]

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=P["dark_bg"])
    fig.suptitle("📦  Category Revenue Lifecycle — Evolution 2015-2025", fontsize=14,
                 color=P["orange"], fontweight="bold")
    c = plt.cm.tab10(np.linspace(0,1,len(top6)))
    for i, col in enumerate(pivot.columns):
        ax.plot(pivot.index, pivot[col]/1e5, "o-", label=col, color=c[i], lw=2, ms=6)
    ax.set_facecolor(P["card_bg"]); ax.set_xlabel("Year", color=P["muted"])
    ax.set_ylabel("Revenue (₹ Lakhs)", color=P["muted"])
    ax.set_title("Category Revenue Trends Over the Decade", color=P["orange"])
    ax.legend(fontsize=9, framealpha=0.3)
    ax.spines[["top","right"]].set_visible(False); ax.grid(alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q18_category_lifecycle.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q19 — COMPETITIVE PRICING BOX PLOT
# ══════════════════════════════════════════════════════════════════════════════
def q19_pricing(df):
    top_cats = df.groupby("category")["transaction_id"].count().nlargest(6).index
    df2 = df[df["category"].isin(top_cats)].copy()
    cap  = df2["original_price_inr"].quantile(0.92)
    data = [df2[df2["category"]==cat]["original_price_inr"].clip(upper=cap).dropna()
            for cat in top_cats]

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=P["dark_bg"])
    fig.suptitle("💲  Competitive Pricing — Price Distribution by Category", fontsize=14,
                 color=P["orange"], fontweight="bold")
    bp = ax.boxplot(data, labels=top_cats, patch_artist=True, notch=True,
                    medianprops={"color":P["orange"],"linewidth":2.5},
                    whiskerprops={"color":P["muted"]},
                    capprops={"color":P["muted"]},
                    flierprops={"marker":".","alpha":0.25,"markerfacecolor":P["teal"]})
    colors_bx = plt.cm.cool(np.linspace(0.1,0.9,len(top_cats)))
    for patch, color in zip(bp["boxes"], colors_bx):
        patch.set_facecolor(color); patch.set_alpha(0.7)
    ax.set_facecolor(P["card_bg"]); ax.set_ylabel("Price (₹)", color=P["muted"])
    ax.set_xlabel("Category", color=P["muted"]); ax.tick_params(axis="x", rotation=20)
    ax.spines[["top","right"]].set_visible(False); ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    return _save(fig, "q19_pricing.png")


# ══════════════════════════════════════════════════════════════════════════════
# Q20 — EXECUTIVE MULTI-PANEL DASHBOARD (CAPSTONE EDA)
# ══════════════════════════════════════════════════════════════════════════════
def q20_executive_dashboard(df):
    fig = plt.figure(figsize=(22, 14), facecolor=P["dark_bg"])
    gs  = gridspec.GridSpec(3, 4, figure=fig, hspace=0.52, wspace=0.38)
    fig.suptitle("📊  Executive Business Health Dashboard — Amazon India 2015-2025",
                 fontsize=17, color=P["orange"], fontweight="bold", y=1.01)

    def kpi_ax(ax, val, label, color=P["orange"]):
        ax.set_facecolor(P["card_bg"]); ax.axis("off")
        ax.text(0.5,0.62,val,ha="center",va="center",fontsize=20,color=color,
                fontweight="bold",transform=ax.transAxes)
        ax.text(0.5,0.22,label,ha="center",va="center",fontsize=9,color=P["muted"],
                transform=ax.transAxes)
        ax.set_title("", pad=2)

    # KPI row
    total_rev = df["final_amount_inr"].sum()
    kpi_ax(fig.add_subplot(gs[0,0]), f"₹{total_rev/1e7:.1f}Cr", "Total Revenue", P["orange"])
    kpi_ax(fig.add_subplot(gs[0,1]), f"{len(df):,}", "Total Orders", P["info"])
    kpi_ax(fig.add_subplot(gs[0,2]), f"{df['customer_id'].nunique():,}", "Customers", P["success"])
    kpi_ax(fig.add_subplot(gs[0,3]), f"₹{df['final_amount_inr'].mean():,.0f}", "Avg Order ₹", P["purple"])

    # Revenue trend
    ax1 = fig.add_subplot(gs[1,:2]); ax1.set_facecolor(P["card_bg"])
    yr = df.groupby("order_year")["final_amount_inr"].sum()
    ax1.fill_between(yr.index, yr.values/1e5, alpha=0.25, color=P["orange"])
    ax1.plot(yr.index, yr.values/1e5, "o-", color=P["orange"], lw=2, ms=7)
    ax1.set_title("Yearly Revenue (₹ Lakhs)", color=P["orange"]); ax1.grid(alpha=0.2)
    ax1.spines[["top","right"]].set_visible(False); ax1.set_xlabel("Year", color=P["muted"])

    # Category donut
    ax2 = fig.add_subplot(gs[1,2:]); ax2.set_facecolor(P["dark_bg"])
    cat = df.groupby("category")["final_amount_inr"].sum().nlargest(6)
    c = plt.cm.Oranges(np.linspace(0.35,0.95,len(cat)))
    w, _, a = ax2.pie(cat, labels=cat.index, autopct="%1.1f%%", colors=c,
                      pctdistance=0.80, wedgeprops={"edgecolor":P["dark_bg"],"lw":1.5})
    for a_ in a: a_.set_color("white"); a_.set_fontsize(8)
    ax2.add_patch(plt.Circle((0,0),0.52,color=P["card_bg"]))
    ax2.set_title("Category Revenue Mix", color=P["orange"])

    # Monthly orders
    ax3 = fig.add_subplot(gs[2,:2]); ax3.set_facecolor(P["card_bg"])
    mo = df.groupby("order_month")["transaction_id"].count()
    c_mo = [P["orange"] if m in FESTIVAL_MONTHS else P["teal"] for m in mo.index]
    ax3.bar([MONTHS[m-1] for m in mo.index], mo.values, color=c_mo, edgecolor=P["dark_bg"])
    ax3.set_title("Monthly Orders  |  🟠 Festival Months", color=P["orange"])
    ax3.tick_params(axis="x", rotation=30); ax3.grid(axis="y", alpha=0.2)
    ax3.spines[["top","right"]].set_visible(False)

    # Payment bar
    ax4 = fig.add_subplot(gs[2,2:]); ax4.set_facecolor(P["card_bg"])
    pay = df.groupby("payment_method")["final_amount_inr"].sum().nlargest(6)
    c_p = plt.cm.Blues(np.linspace(0.4,0.95,len(pay)))
    ax4.barh(pay.index[::-1], pay.values[::-1]/1e5, color=c_p, edgecolor=P["dark_bg"])
    ax4.set_title("Revenue by Payment Method (₹ Lakhs)", color=P["orange"])
    ax4.spines[["top","right"]].set_visible(False)

    return _save(fig, "q20_executive_dashboard.png")


# ══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_all(df: pd.DataFrame) -> list[Path]:
    print("\n" + "═"*55)
    print("   📊  EDA VISUALIZATIONS")
    print("═"*55)
    fns = [q1_revenue_trend, q2_seasonal_heatmap, q3_rfm_segmentation,
           q4_payment_evolution, q5_category_perf, q6_prime_impact,
           q7_geographic, q8_festival_impact, q9_age_analysis,
           q10_price_demand, q11_delivery, q12_returns,
           q13_brands, q14_clv, q15_discounts,
           q16_ratings, q17_purchase_freq, q18_category_lifecycle,
           q19_pricing, q20_executive_dashboard]
    paths = []
    for i, fn in enumerate(fns, 1):
        try:
            p = fn(df)
            if p: paths.append(p)
        except Exception as e:
            print(f"   ⚠️  Q{i:02d} {fn.__name__}: {e}")
    print(f"\n   ✅  {len(paths)}/20 charts saved → {EDA_DIR}\n")
    return paths


if __name__ == "__main__":
    from utils.data_generator import make_transactions
    from data_cleaning.cleaning_pipeline import run_pipeline
    raw   = make_transactions()
    clean, _ = run_pipeline(raw)
    run_all(clean)
