"""
setup_db.py
===========
Creates a SQLite database with realistic e-commerce tables and seeds them
with synthetic but plausible retail/campaign data.

Tables:
    products       — product catalogue with category and base price
    campaigns      — promotional campaigns with type, discount, date range
    sessions       — web sessions linked to a category (simulates traffic)
    orders         — individual orders, linked to product and campaign
    order_items    — line items within each order
"""

import sqlite3
import random
from datetime import datetime, timedelta


PRODUCTS = [
    ("Arla Organic Milk 1L",        "Dairy",      18.90),
    ("Arla Butter 500g",            "Dairy",      34.50),
    ("Arla Skyr Natural 500g",      "Dairy",      29.90),
    ("Arla Cream Cheese 200g",      "Dairy",      22.00),
    ("Arla Cheddar Slices 200g",    "Dairy",      39.90),
    ("Arla Lactose-Free Milk 1L",   "Dairy",      24.90),
    ("Organic Yoghurt Strawberry",  "Dairy",      16.50),
    ("Oat Drink Original 1L",       "Plant-Based", 29.90),
    ("Oat Drink Barista 1L",        "Plant-Based", 34.90),
    ("Soy Drink Vanilla 1L",        "Plant-Based", 27.50),
    ("Almond Drink Unsweetened 1L", "Plant-Based", 31.90),
    ("Protein Shake Chocolate",     "Nutrition",  54.90),
    ("Protein Shake Vanilla",       "Nutrition",  54.90),
    ("Whey Powder 1kg",             "Nutrition",  299.00),
    ("Cottage Cheese 500g",         "Dairy",      32.90),
    ("Mozzarella 125g",             "Dairy",      28.50),
    ("Feta Block 200g",             "Dairy",      44.90),
    ("Greek Yoghurt 1kg",           "Dairy",      59.90),
    ("Cooking Cream 200ml",         "Dairy",      19.90),
    ("Sour Cream 200ml",            "Dairy",      17.50),
]

CAMPAIGNS = [
    ("Spring Dairy Sale",       "Percentage",  15, "2026-03-01", "2026-03-31"),
    ("Plant-Based Push Q1",     "Percentage",  20, "2026-01-15", "2026-02-15"),
    ("Nutrition Bundle Deal",   "Bundle",      10, "2026-02-01", "2026-02-28"),
    ("Easter Promo",            "Percentage",  12, "2026-04-10", "2026-04-20"),
    ("Flash Friday Week 14",    "Flash",       25, "2026-04-03", "2026-04-03"),
    ("Loyalty Member Week",     "Loyalty",      8, "2026-03-10", "2026-03-16"),
    ("Summer Kickoff",          "Percentage",  18, "2026-05-01", "2026-05-31"),
    ("No Campaign",             "None",         0, "2026-01-01", "2026-06-01"),
]

CATEGORIES = ["Dairy", "Plant-Based", "Nutrition"]


def random_date(start_str, end_str):
    start = datetime.strptime(start_str, "%Y-%m-%d")
    end   = datetime.strptime(end_str,   "%Y-%m-%d")
    delta = (end - start).days
    if delta <= 0:
        return start.strftime("%Y-%m-%d")
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")


def create_and_seed_db(db_path=":memory:"):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category     TEXT NOT NULL,
            base_price   REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS campaigns (
            campaign_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_name TEXT NOT NULL,
            campaign_type TEXT NOT NULL,
            discount_pct  REAL NOT NULL,
            start_date    TEXT NOT NULL,
            end_date      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessions (
            session_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TEXT NOT NULL,
            category    TEXT NOT NULL,
            converted   INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS orders (
            order_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            order_date    TEXT NOT NULL,
            campaign_id   INTEGER REFERENCES campaigns(campaign_id),
            total_amount  REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS order_items (
            item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id    INTEGER REFERENCES orders(order_id),
            product_id  INTEGER REFERENCES products(product_id),
            quantity    INTEGER NOT NULL,
            unit_price  REAL NOT NULL,
            discount_pct REAL NOT NULL DEFAULT 0
        );
    """)

    # Seed products
    cur.executemany(
        "INSERT INTO products (product_name, category, base_price) VALUES (?,?,?)",
        PRODUCTS
    )

    # Seed campaigns
    cur.executemany(
        "INSERT INTO campaigns (campaign_name, campaign_type, discount_pct, start_date, end_date) VALUES (?,?,?,?,?)",
        CAMPAIGNS
    )

    conn.commit()

    # Fetch inserted ids
    products  = cur.execute("SELECT * FROM products").fetchall()
    campaigns = cur.execute("SELECT * FROM campaigns").fetchall()

    random.seed(42)

    # Seed sessions — 4,000 sessions across 6 months
    session_rows = []
    for _ in range(4000):
        day  = random_date("2026-01-01", "2026-06-01")
        cat  = random.choice(CATEGORIES)
        conv = 1 if random.random() < 0.072 else 0   # ~7.2% conversion rate
        session_rows.append((day, cat, conv))

    cur.executemany(
        "INSERT INTO sessions (session_date, category, converted) VALUES (?,?,?)",
        session_rows
    )

    # Seed orders — one per converted session (~288 orders)
    converted_sessions = [(r[0], r[1]) for r in session_rows if r[2] == 1]

    for sess_date, sess_cat in converted_sessions:
        # Pick a campaign active on this date
        active = [c for c in campaigns
                  if c["start_date"] <= sess_date <= c["end_date"]]
        camp = random.choice(active) if active else campaigns[-1]  # fallback = No Campaign

        # 1–4 items per order
        n_items  = random.randint(1, 4)
        # Prefer products in the session's category
        cat_prods = [p for p in products if p["category"] == sess_cat]
        other_prods = [p for p in products if p["category"] != sess_cat]
        chosen = random.choices(cat_prods, k=min(n_items, len(cat_prods)))
        if len(chosen) < n_items:
            chosen += random.choices(other_prods, k=n_items - len(chosen))

        total = 0.0
        items = []
        for prod in chosen:
            qty   = random.randint(1, 6)
            disc  = camp["discount_pct"]
            price = prod["base_price"] * (1 - disc / 100)
            total += price * qty
            items.append((prod["product_id"], qty, price, disc))

        cur.execute(
            "INSERT INTO orders (order_date, campaign_id, total_amount) VALUES (?,?,?)",
            (sess_date, camp["campaign_id"], round(total, 2))
        )
        order_id = cur.lastrowid

        cur.executemany(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES (?,?,?,?,?)",
            [(order_id, *item) for item in items]
        )

    conn.commit()
    return conn
