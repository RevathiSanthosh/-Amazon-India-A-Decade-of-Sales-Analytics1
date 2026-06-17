
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


CREATE INDEX IF NOT EXISTS idx_tx_cust   ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_tx_prod   ON transactions(product_id);
CREATE INDEX IF NOT EXISTS idx_tx_date   ON transactions(order_date);
CREATE INDEX IF NOT EXISTS idx_tx_year   ON transactions(order_year);
CREATE INDEX IF NOT EXISTS idx_tx_cat    ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_tx_city   ON transactions(customer_city);
CREATE INDEX IF NOT EXISTS idx_tx_state  ON transactions(customer_state);
CREATE INDEX IF NOT EXISTS idx_tx_pay    ON transactions(payment_method);
CREATE INDEX IF NOT EXISTS idx_tx_prime  ON transactions(is_prime_member);
CREATE INDEX IF NOT EXISTS idx_tx_fest   ON transactions(is_festival_sale);
CREATE INDEX IF NOT EXISTS idx_tx_tier   ON transactions(customer_spending_tier);
CREATE INDEX IF NOT EXISTS idx_prod_cat  ON products(category);
CREATE INDEX IF NOT EXISTS idx_prod_brand ON products(brand);