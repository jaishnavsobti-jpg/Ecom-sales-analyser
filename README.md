# E-commerce Sales Analyser

A SQL-driven analytics tool that simulates a retail campaign dataset, stores it in a SQLite database, and surfaces business insights through structured queries — built to mirror real e-commerce operations work.

## What it does

| Analysis | SQL concepts used |
|---|---|
| Top 10 products by revenue | JOIN, GROUP BY, SUM, ORDER BY, LIMIT |
| Campaign performance breakdown | JOIN, AVG, COUNT, GROUP BY |
| Weekly revenue trend (12 weeks) | strftime, GROUP BY, aggregation |
| Category conversion rate | Subquery, COALESCE, CAST, ROUND |
| Underperforming campaigns | Scalar subquery, HAVING |

## Project structure

```
ecom-sales-analyser/
├── main.py       # Entry point — runs all analyses and prints results
├── setup_db.py   # Creates SQLite schema and seeds realistic data
├── queries.py    # All SQL queries as documented Python functions
└── README.md
```

## How to run

No external libraries needed — uses Python's built-in `sqlite3` module only.

```bash
git clone https://github.com/YOUR_USERNAME/ecom-sales-analyser
cd ecom-sales-analyser
python main.py
```

## Sample output

```
==================================================
  TOP 10 PRODUCTS BY REVENUE
==================================================
Product                        Category        Units Sold  Revenue (SEK)
------------------------------------------------------------------------
Arla Organic Milk 1L           Dairy                  312       5,234.10
Oat Drink Barista 1L           Plant-Based            198       6,102.40
...

==================================================
  CAMPAIGN PERFORMANCE
==================================================
Campaign                     Type            Orders      Revenue  Avg Order  Discount%
...
```

## Skills demonstrated

- Relational database design (5 normalised tables)
- SQL querying: JOINs, aggregations, subqueries, HAVING, date functions
- Python + SQLite integration (`sqlite3`, `Row` factory)
- E-commerce domain concepts: conversion rate, campaign ROI, revenue per session

## Context

Built as part of a self-directed technical curriculum alongside AI, cybersecurity, and Python coursework. Applying SQL skills to a business analytics use case relevant to e-commerce and digital marketing operations.
