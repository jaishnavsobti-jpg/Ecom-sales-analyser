"""
queries.py
==========
All analysis queries in one place.
Each function takes a sqlite3 connection and returns a list of Row objects.

SQL concepts demonstrated:
    - SELECT, WHERE, GROUP BY, ORDER BY, LIMIT
    - JOINs (INNER, LEFT)
    - Aggregations: SUM, COUNT, AVG, ROUND
    - Subqueries
    - CASE WHEN
    - Window-function-style subquery for comparison
    - Date functions: strftime
"""


def top_products_by_revenue(conn):
    """
    Which products generated the most revenue?
    Joins order_items → products, aggregates revenue and units sold.
    """
    return conn.execute("""
        SELECT
            p.product_name,
            p.category,
            SUM(oi.quantity)                              AS units_sold,
            ROUND(SUM(oi.quantity * oi.unit_price), 2)   AS revenue
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        GROUP BY p.product_id
        ORDER BY revenue DESC
        LIMIT 10
    """).fetchall()


def campaign_performance(conn):
    """
    How did each campaign perform in terms of orders, revenue,
    average order value, and average discount given?
    """
    return conn.execute("""
        SELECT
            c.campaign_name,
            c.campaign_type,
            COUNT(o.order_id)                           AS total_orders,
            ROUND(SUM(o.total_amount), 0)               AS total_revenue,
            ROUND(AVG(o.total_amount), 0)               AS avg_order_value,
            ROUND(AVG(c.discount_pct), 1)               AS avg_discount_pct
        FROM orders o
        JOIN campaigns c ON c.campaign_id = o.campaign_id
        GROUP BY c.campaign_id
        ORDER BY total_revenue DESC
    """).fetchall()


def weekly_revenue_trend(conn):
    """
    What does revenue look like week by week over the last 12 weeks?
    Uses strftime to group by ISO week start (Monday).
    """
    return conn.execute("""
        SELECT
            strftime('%Y-%m-%d',
                order_date, 'weekday 0', '-6 days') AS week_start,
            ROUND(SUM(total_amount), 0)              AS weekly_revenue,
            COUNT(order_id)                          AS orders
        FROM orders
        GROUP BY week_start
        ORDER BY week_start DESC
        LIMIT 12
    """).fetchall()[::-1]   # reverse so oldest → newest


def category_conversion_rate(conn):
    """
    For each product category, how many sessions converted to orders,
    and what is the revenue per session?

    Uses a subquery to calculate orders per category,
    joined against session counts.
    """
    return conn.execute("""
        SELECT
            s.category,
            COUNT(s.session_id)                              AS sessions,
            SUM(s.converted)                                 AS orders,
            ROUND(100.0 * SUM(s.converted) / COUNT(*), 2)   AS conversion_rate,
            ROUND(
                COALESCE((
                    SELECT SUM(o2.total_amount)
                    FROM orders o2
                    JOIN order_items oi2 ON oi2.order_id = o2.order_id
                    JOIN products p2     ON p2.product_id = oi2.product_id
                    WHERE p2.category = s.category
                ), 0) / CAST(COUNT(s.session_id) AS REAL), 2
            ) AS rev_per_session
        FROM sessions s
        GROUP BY s.category
        ORDER BY conversion_rate DESC
    """).fetchall()


def underperforming_campaigns(conn):
    """
    Which campaigns generated less revenue than the average campaign?
    Demonstrates a subquery used as a scalar comparison value.
    """
    return conn.execute("""
        SELECT
            c.campaign_name,
            ROUND(SUM(o.total_amount), 0)  AS total_revenue,
            ROUND((
                SELECT AVG(sub.campaign_total)
                FROM (
                    SELECT SUM(o2.total_amount) AS campaign_total
                    FROM orders o2
                    GROUP BY o2.campaign_id
                ) sub
            ), 0) AS avg_revenue
        FROM orders o
        JOIN campaigns c ON c.campaign_id = o.campaign_id
        GROUP BY c.campaign_id
        HAVING total_revenue < avg_revenue
        ORDER BY total_revenue ASC
    """).fetchall()
