"""
utils/data_generator.py
-----------------------
Generates a rich, realistic synthetic Amazon India dataset with
intentional data quality issues matching the project spec (25% dirt).
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config.settings import RANDOM_SEED, SYNTHETIC_ROWS, YEARS, CATEGORIES


def make_transactions(n: int = SYNTHETIC_ROWS) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # ── year distribution (growth curve) ─────────────────────────────────────
    yr_weights = np.array([0.03,0.04,0.06,0.07,0.08,0.10,0.11,0.12,0.14,0.13,0.12])
    yr_weights /= yr_weights.sum()
    years  = rng.choice(YEARS, n, p=yr_weights)
    months = rng.integers(1, 13, n)
    days   = rng.integers(1, 29, n)

    # ── messy dates (Q1) ──────────────────────────────────────────────────────
    dates = []
    for yr, mo, dy in zip(years, months, days):
        fmt = rng.choice(["iso","dmy_slash","dmy_dash","bad"], p=[0.35,0.30,0.25,0.10])
        if fmt == "iso":       dates.append(f"{yr}-{mo:02d}-{dy:02d}")
        elif fmt == "dmy_slash": dates.append(f"{dy:02d}/{mo:02d}/{yr}")
        elif fmt == "dmy_dash":  dates.append(f"{dy:02d}-{mo:02d}-{str(yr)[2:]}")
        else:                    dates.append("32/13/2020")

    # ── categories & subcategories ────────────────────────────────────────────
    cat_w = np.array([0.26,0.20,0.15,0.09,0.09,0.08,0.07,0.06]); cat_w /= cat_w.sum()
    sub_map = {
        "Electronics":    ["Smartphones","Laptops","Tablets","Headphones","Cameras"],
        "Fashion":        ["Men's Clothing","Women's Clothing","Footwear","Accessories","Sarees"],
        "Home & Kitchen": ["Cookware","Furniture","Appliances","Decor","Bedding"],
        "Books":          ["Fiction","Non-Fiction","Academic","Comics","Self-Help"],
        "Sports":         ["Fitness","Outdoor","Cricket","Football","Yoga"],
        "Beauty":         ["Skincare","Haircare","Makeup","Perfumes","Grooming"],
        "Grocery":        ["Staples","Snacks","Beverages","Health Food","Dairy"],
        "Toys":           ["Action Figures","Board Games","Puzzles","Educational","STEM"],
    }
    brands_map = {
        "Electronics":    ["Samsung","Apple","Realme","OnePlus","Xiaomi","Sony","LG","Boat"],
        "Fashion":        ["Nike","Adidas","Puma","Levi's","Zara","H&M","Bata","Woodland"],
        "Home & Kitchen": ["Prestige","Pigeon","Havells","Philips","Godrej","Bosch","IFB","IKEA"],
        "Books":          ["Penguin","HarperCollins","Scholastic","Westland","Rupa","Aleph"],
        "Sports":         ["Adidas","Nike","Cosco","SG Cricket","Yonex","Decathlon","Nivia"],
        "Beauty":         ["Lakme","Maybelline","L'Oreal","Nykaa","Forest Essentials","Wow","Mamaearth"],
        "Grocery":        ["Amul","Nestle","ITC","Britannia","Haldiram's","MTR","Patanjali"],
        "Toys":           ["Lego","Hasbro","Mattel","Funskool","Fisher-Price","Hot Wheels"],
    }

    # Dirty category names (Q6)
    dirty_map = {"Electronics":["Electronics","ELECTRONICS","electronic","Electronics & Accessories"],
                 "Fashion":["Fashion","fashion","FASHION","Clothing"],
                 "Home & Kitchen":["Home & Kitchen","Home and Kitchen","HOME","Home"],
                 "Books":["Books","BOOKS","book","Literature"],
                 "Sports":["Sports","SPORTS","sports","Fitness"],
                 "Beauty":["Beauty","beauty","BEAUTY","Beauty & Personal Care"],
                 "Grocery":["Grocery","GROCERY","grocery","Food"],
                 "Toys":["Toys","TOYS","toys","Toys & Games"]}

    cat_clean  = rng.choice(CATEGORIES, n, p=cat_w)
    cats, subs, brands = [], [], []
    for c in cat_clean:
        dirty = rng.choice(dirty_map[c])
        cats.append(dirty)
        subs.append(rng.choice(sub_map[c]))
        brands.append(rng.choice(brands_map[c]))

    # ── prices (Q2) ──────────────────────────────────────────────────────────
    base_prices = {"Electronics":[5000,8000,15000,25000,50000],
                   "Fashion":[500,1000,2000,3500,8000],
                   "Home & Kitchen":[800,1500,3000,6000,12000],
                   "Books":[200,350,500,800,1200],
                   "Sports":[400,800,1500,3000,6000],
                   "Beauty":[200,400,800,1500,3000],
                   "Grocery":[100,200,400,600,1000],
                   "Toys":[300,600,1200,2000,4000]}
    raw_prices = []
    for c in cat_clean:
        bp = rng.choice(base_prices[c])
        bp = int(bp * rng.uniform(0.7, 1.4))
        fmt = rng.choice(["num","sym","comma","text"], p=[0.55,0.20,0.20,0.05])
        if fmt == "num":    raw_prices.append(str(bp))
        elif fmt == "sym":  raw_prices.append(f"₹{bp}")
        elif fmt == "comma":raw_prices.append(f"₹{bp:,}")
        else:               raw_prices.append("Price on Request")

    # ── ratings (Q3) ─────────────────────────────────────────────────────────
    raw_ratings = []
    for _ in range(n):
        val = round(rng.uniform(2.0, 5.0), 1)
        fmt = rng.choice(["float","stars","frac","nan"], p=[0.45,0.15,0.30,0.10])
        if fmt == "float":  raw_ratings.append(str(val))
        elif fmt == "stars":raw_ratings.append(f"{int(val)} stars")
        elif fmt == "frac": raw_ratings.append(f"{val}/5.0")
        else:               raw_ratings.append(np.nan)

    # ── cities (Q4) ──────────────────────────────────────────────────────────
    city_clean = ["Mumbai","Delhi","Bangalore","Chennai","Hyderabad","Kolkata",
                  "Pune","Ahmedabad","Jaipur","Lucknow","Surat","Kochi",
                  "Chandigarh","Indore","Nagpur"]
    city_dirty_map = {
        "Mumbai":    ["Mumbai","Bombay","MUMBAI","mumbai"],
        "Delhi":     ["Delhi","New Delhi","DELHI","delhi ncr"],
        "Bangalore": ["Bangalore","Bengaluru","BANGALORE","B'lore"],
        "Chennai":   ["Chennai","Madras","CHENNAI","chennai"],
        "Hyderabad": ["Hyderabad","Secunderabad","HYD","hyderabad"],
        "Kolkata":   ["Kolkata","Calcutta","KOLKATA","kolkata"],
        "Pune":      ["Pune","Poona","PUNE","pune"],
        "Ahmedabad": ["Ahmedabad","Amdavad","AHMEDABAD","ahmedabad"],
        "Jaipur":    ["Jaipur","Pink City","JAIPUR","jaipur"],
        "Lucknow":   ["Lucknow","LKO","LUCKNOW","lucknow"],
        "Surat":     ["Surat","SURAT","surat"],
        "Kochi":     ["Kochi","Cochin","KOCHI","kochi"],
        "Chandigarh":["Chandigarh","CHD","chandigarh"],
        "Indore":    ["Indore","INDORE","indore"],
        "Nagpur":    ["Nagpur","NAGPUR","nagpur"],
    }
    state_map = {
        "Mumbai":"Maharashtra","Delhi":"Delhi","Bangalore":"Karnataka","Chennai":"Tamil Nadu",
        "Hyderabad":"Telangana","Kolkata":"West Bengal","Pune":"Maharashtra",
        "Ahmedabad":"Gujarat","Jaipur":"Rajasthan","Lucknow":"Uttar Pradesh",
        "Surat":"Gujarat","Kochi":"Kerala","Chandigarh":"Punjab","Indore":"Madhya Pradesh","Nagpur":"Maharashtra"
    }
    city_tier = {
        "Mumbai":"Metro","Delhi":"Metro","Bangalore":"Metro","Chennai":"Metro","Hyderabad":"Metro",
        "Kolkata":"Metro","Pune":"Tier1","Ahmedabad":"Tier1","Jaipur":"Tier1","Lucknow":"Tier1",
        "Surat":"Tier1","Kochi":"Tier1","Chandigarh":"Tier2","Indore":"Tier2","Nagpur":"Tier2"
    }
    city_w = np.array([0.14,0.13,0.12,0.09,0.09,0.08,0.07,0.06,0.05,0.05,0.05,0.03,0.02,0.02,0.01])
    city_w /= city_w.sum()
    raw_cities = []
    chosen_cities = rng.choice(city_clean, n, p=city_w)
    for c in chosen_cities:
        raw_cities.append(rng.choice(city_dirty_map[c]))
    states = [state_map[c] for c in chosen_cities]
    tiers  = [city_tier[c] for c in chosen_cities]

    # ── booleans (Q5) ────────────────────────────────────────────────────────
    bool_opts = ["True","False","Yes","No","1","0","Y","N"]
    prime_prob = np.clip(0.15 + (years - 2015) * 0.05, 0.15, 0.65)
    is_prime = [rng.choice(["True","False","Yes","No","1","0"],
                           p=np.array([p*0.5,(1-p)*0.5,p*0.2,(1-p)*0.2,p*0.15,(1-p)*0.15])/sum([p*0.5,(1-p)*0.5,p*0.2,(1-p)*0.2,p*0.15,(1-p)*0.15]))
                for p in prime_prob]
    is_prime_elig = rng.choice(bool_opts[:4], n)
    festival_months_set = {1,7,8,10,11}
    is_festival = []
    festival_names = []
    for mo in months:
        if mo in festival_months_set:
            is_festival.append(rng.choice(["True","Yes","1"], p=[0.5,0.3,0.2]))
            f_map = {1:"Republic Day Sale",7:"Prime Day",8:"Independence Day Sale",
                     10:"Diwali Sale",11:"Big Billion Days"}
            festival_names.append(f_map[mo])
        else:
            is_festival.append(rng.choice(["False","No","0"], p=[0.5,0.3,0.2]))
            festival_names.append("None")

    # ── delivery days (Q7) ────────────────────────────────────────────────────
    raw_delivery = []
    for city in chosen_cities:
        t = city_tier[city]
        if t == "Metro":   base = rng.choice([1,2,3,4], p=[0.3,0.35,0.25,0.10])
        elif t == "Tier1": base = rng.choice([2,3,4,5], p=[0.2,0.35,0.30,0.15])
        else:              base = rng.choice([3,4,5,6,7], p=[0.15,0.25,0.30,0.20,0.10])
        noise = rng.choice(["ok","neg","text","extreme"], p=[0.82,0.05,0.05,0.08])
        if noise == "ok":      raw_delivery.append(str(base))
        elif noise == "neg":   raw_delivery.append(str(-base))
        elif noise == "text":  raw_delivery.append(rng.choice(["Same Day","1-2 days","Next Day"]))
        else:                  raw_delivery.append(str(rng.integers(40,60)))

    # ── payments (Q10) ────────────────────────────────────────────────────────
    upi_growth = np.clip((years - 2015) / 10, 0, 1)
    raw_payments = []
    upi_dirty    = ["UPI","PhonePe","GooglePay","Google Pay","UPI/PhonePe","BHIM","Paytm"]
    cc_dirty     = ["Credit Card","CREDIT_CARD","CC","Visa Credit","Mastercard Credit","credit card"]
    dc_dirty     = ["Debit Card","debit card","DC","Debit_Card","Visa Debit"]
    cod_dirty    = ["Cash on Delivery","COD","C.O.D","Cash","cod"]
    nb_dirty     = ["Net Banking","NetBanking","Internet Banking","NEFT"]
    emi_dirty    = ["EMI","No Cost EMI","emi/credit","Equated Monthly"]
    wal_dirty    = ["Amazon Pay","Wallet","MobiKwik","Freecharge"]
    for u in upi_growth:
        p_upi = u * 0.45
        p_cod = max(0.05, 0.35 - u * 0.30)
        p_cc  = 0.15; p_dc = 0.15; p_rest = 1 - p_upi - p_cod - p_cc - p_dc
        p_nb  = p_rest * 0.4; p_emi = p_rest * 0.35; p_wal = p_rest * 0.25
        chosen = rng.choice(["upi","cc","dc","cod","nb","emi","wal"],
                             p=np.array([p_upi,p_cc,p_dc,p_cod,p_nb,p_emi,p_wal]))
        dm = {"upi":upi_dirty,"cc":cc_dirty,"dc":dc_dirty,"cod":cod_dirty,
              "nb":nb_dirty,"emi":emi_dirty,"wal":wal_dirty}
        raw_payments.append(rng.choice(dm[chosen]))

    # ── prices & discounts ────────────────────────────────────────────────────
    clean_prices = []
    for rp in raw_prices:
        import re
        v = re.sub(r"[₹,\s]","",str(rp))
        try: clean_prices.append(float(v))
        except: clean_prices.append(2000.0)

    discount = []
    for yr, cat in zip(years, cat_clean):
        fest_boost = 1.2 if yr % 5 == 0 else 1.0
        base_disc = {"Electronics":20,"Fashion":25,"Books":10,"Beauty":30,
                     "Grocery":15,"Home & Kitchen":18,"Sports":20,"Toys":15}[cat]
        d = int(np.clip(rng.normal(base_disc * fest_boost, 8), 0, 70))
        discount.append(d)

    final_amt = [round(max(99, p * (1 - d/100) + rng.uniform(-50,50)), 2)
                 for p, d in zip(clean_prices, discount)]
    del_charges = [0 if amt > 499 else rng.choice([40,49,59,79,99])
                   for amt in final_amt]

    # ── customer segmentation ─────────────────────────────────────────────────
    age_groups = rng.choice(["18-25","26-35","36-45","46-55","55+"], n,
                             p=[0.22,0.32,0.24,0.14,0.08])
    def spending_tier(amt):
        if amt < 500:  return "Budget"
        if amt < 2000: return "Mid-range"
        if amt < 8000: return "Premium"
        return "Luxury"
    spending_tiers = [spending_tier(a) for a in final_amt]

    # ── return & ratings ─────────────────────────────────────────────────────
    return_status = []
    for cat, amt in zip(cat_clean, final_amt):
        ret_prob = {"Electronics":0.08,"Fashion":0.15,"Books":0.04,"Beauty":0.10,
                    "Grocery":0.03,"Home & Kitchen":0.09,"Sports":0.07,"Toys":0.06}[cat]
        if amt > 10000: ret_prob *= 1.3
        s = rng.choice(["Returned","Not Returned","Pending"],
                        p=[min(ret_prob,0.3), 1-min(ret_prob,0.3)-0.02, 0.02])
        return_status.append(s)

    cust_ratings = []
    for rs, dr in zip(return_status, raw_delivery):
        base = 4.0 if rs == "Not Returned" else 2.5
        cust_ratings.append(round(np.clip(rng.normal(base, 0.7), 1.0, 5.0), 1)
                            if rng.random() > 0.05 else np.nan)

    df = pd.DataFrame({
        "transaction_id"        : [f"TXN{i:08d}" for i in range(n)],
        "customer_id"           : [f"CUST{rng.integers(1,80001):06d}" for _ in range(n)],
        "product_id"            : [f"PROD{rng.integers(1,2001):04d}" for _ in range(n)],
        "order_date"            : dates,
        "order_year"            : years,
        "order_month"           : months,
        "order_quarter"         : ((months - 1) // 3 + 1),
        "product_name"          : [f"Product {rng.integers(1,2001)}" for _ in range(n)],
        "category"              : cats,
        "category_clean"        : cat_clean,     # reference
        "subcategory"           : subs,
        "brand"                 : brands,
        "product_rating"        : raw_ratings,
        "original_price_inr"    : raw_prices,
        "discount_percent"      : discount,
        "final_amount_inr"      : final_amt,
        "delivery_charges"      : del_charges,
        "customer_city"         : raw_cities,
        "customer_state"        : states,
        "city_tier"             : tiers,
        "age_group"             : age_groups,
        "is_prime_member"       : is_prime,
        "is_prime_eligible"     : is_prime_elig,
        "is_festival_sale"      : is_festival,
        "festival_name"         : festival_names,
        "payment_method"        : raw_payments,
        "delivery_days"         : raw_delivery,
        "return_status"         : return_status,
        "customer_rating"       : cust_ratings,
        "customer_spending_tier": spending_tiers,
    })
    return df


def make_catalog(n: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED + 1)
    cat_w = np.array([0.26,0.20,0.15,0.09,0.09,0.08,0.07,0.06]); cat_w /= cat_w.sum()
    cats = rng.choice(CATEGORIES, n, p=cat_w)
    base_p = {"Electronics":15000,"Fashion":1500,"Home & Kitchen":2500,"Books":400,
              "Sports":1200,"Beauty":600,"Grocery":300,"Toys":800}
    return pd.DataFrame({
        "product_id"      : [f"PROD{i:04d}" for i in range(1, n+1)],
        "product_name"    : [f"Product {i}" for i in range(1, n+1)],
        "category"        : cats,
        "subcategory"     : [f"Sub_{rng.integers(1,6)}" for _ in range(n)],
        "brand"           : [f"Brand_{rng.integers(1,101)}" for _ in range(n)],
        "base_price_2015" : [round(base_p[c] * rng.uniform(0.5, 3.0), 2) for c in cats],
        "weight_kg"       : [round(rng.uniform(0.1, 15.0), 2) for _ in range(n)],
        "rating"          : [round(rng.uniform(3.0, 5.0), 1) for _ in range(n)],
        "is_prime_eligible": rng.choice([True,False], n, p=[0.75, 0.25]),
        "launch_year"     : rng.integers(2012, 2024, n),
    })
