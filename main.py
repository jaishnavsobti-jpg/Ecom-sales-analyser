"""
E-commerce Sales Analyser
=========================
Simulates a retail/campaign dataset, stores it in SQLite,
and runs SQL-driven analysis — campaign performance, product trends,
and customer behaviour insights.
"""

import sqlite3
import random
from datetime import datetime, timedelta
from setup_db import create_and_seed_db
from queries import (
    top_products_by_revenue,
    campaign_performance,
    weekly_revenue_trend,
    category_conversion_rate,
    underperforming_campaigns,
)


def divider(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def main():
    conn = create_and_seed_db()

    divider("TOP 10 PRODUCTS BY REVENUE")
    rows = top_products_by_revenue(conn)
    print(f"{'Product':<30} {'Category':<15} {'Units Sold':>10} {'Revenue (SEK)':>14}")
    print("-" * 72)
    for r in rows:
        print(f"{r['product_name']:<30} {r['category']:<15} {r['units_sold']:>10,} {r['revenue']:>14,.2f}")

    divider("CAMPAIGN PERFORMANCE")
    rows = campaign_performance(conn)
    print(f"{'Campaign':<28} {'Type':<14} {'Orders':>7} {'Revenue':>12} {'Avg Order':>10} {'Discount%':>10}")
    print("-" * 85)
    for r in rows:
        print(f"{r['campaign_name']:<28} {r['campaign_type']:<14} {r['total_orders']:>7,} {r['total_revenue']:>12,.0f} {r['avg_order_value']:>10,.0f} {r['avg_discount_pct']:>9.1f}%")

    divider("WEEKLY REVENUE TREND (last 12 weeks)")
    rows = weekly_revenue_trend(conn)
    max_rev = max(r['weekly_revenue'] for r in rows) if rows else 1
    for r in rows:
        bar_len = int((r['weekly_revenue'] / max_rev) * 30)
        bar = "█" * bar_len
        print(f"  Week {r['week_start']}  {bar:<30}  SEK {r['weekly_revenue']:>10,.0f}")

    divider("CATEGORY CONVERSION RATE")
    rows = category_conversion_rate(conn)
    print(f"{'Category':<20} {'Sessions':>10} {'Orders':>8} {'Conv. Rate':>12} {'Rev/Session':>13}")
    print("-" * 66)
    for r in rows:
        print(f"{r['category']:<20} {r['sessions']:>10,} {r['orders']:>8,} {r['conversion_rate']:>11.2f}%  SEK {r['rev_per_session']:>7.2f}")

    divider("UNDERPERFORMING CAMPAIGNS (below avg revenue)")
    rows = underperforming_campaigns(conn)
    if rows:
        print(f"{'Campaign':<28} {'Revenue':>12} {'vs Avg':>10}")
        print("-" * 52)
        for r in rows:
            diff = r['total_revenue'] - r['avg_revenue']
            print(f"{r['campaign_name']:<28} SEK {r['total_revenue']:>8,.0f}  {diff:>+10,.0f}")
    else:
        print("  All campaigns performing at or above average.")

    conn.close()
    print(f"\n{'='*50}")
    print("  Analysis complete.")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
