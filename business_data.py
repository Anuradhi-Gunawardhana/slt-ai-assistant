
from database import get_connection


# ---------- CUSTOMER DATA ----------

def get_customer_profile(customer_id):
    if not customer_id:
        return None

    conn = get_connection()

    try:
        row = conn.execute("""
            SELECT
                customer_id,
                name,
                email,
                phone,
                city
            FROM customers
            WHERE customer_id = ?
        """, (customer_id,)).fetchone()

        return dict(row) if row else None

    finally:
        conn.close()


def get_customer_subscription(customer_id):
    if not customer_id:
        return []

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                s.subscription_id,
                s.status,
                s.start_date,
                p.package_name,
                p.service_type,
                p.monthly_price,
                p.speed_mbps,
                p.data_limit_gb
            FROM subscriptions s
            JOIN packages p
                ON s.package_id = p.package_id
            WHERE s.customer_id = ?
            ORDER BY s.start_date DESC
        """, (customer_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_customer_bills(customer_id):
    if not customer_id:
        return []

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                b.bill_id,
                b.billing_month,
                b.amount,
                b.payment_status,
                b.due_date
            FROM bills b
            JOIN subscriptions s
                ON b.subscription_id = s.subscription_id
            WHERE s.customer_id = ?
            ORDER BY b.billing_month DESC
        """, (customer_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


def get_customer_tickets(customer_id):
    if not customer_id:
        return []

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                ticket_id,
                issue_category,
                description,
                status,
                priority,
                created_at
            FROM support_tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """, (customer_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ---------- STAFF DATA ----------

def get_staff_tickets(staff_id):
    if not staff_id:
        return []

    conn = get_connection()

    try:
        rows = conn.execute("""
            SELECT
                t.ticket_id,
                t.issue_category,
                t.description,
                t.status,
                t.priority,
                t.created_at,
                c.name AS customer_name,
                c.phone AS customer_phone,
                c.city AS customer_city
            FROM support_tickets t
            JOIN customers c
                ON t.customer_id = c.customer_id
            WHERE t.assigned_staff_id = ?
            ORDER BY
                CASE t.priority
                    WHEN 'High' THEN 1
                    WHEN 'Medium' THEN 2
                    ELSE 3
                END,
                t.created_at DESC
        """, (staff_id,)).fetchall()

        return [dict(row) for row in rows]

    finally:
        conn.close()


# ---------- ADMIN REPORTING ----------

def get_admin_report():
    conn = get_connection()

    try:
        summary = conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM customers)
                    AS total_customers,

                (SELECT COUNT(*) FROM subscriptions
                 WHERE status = 'Active')
                    AS active_subscriptions,

                (SELECT COUNT(*) FROM bills
                 WHERE payment_status = 'Unpaid')
                    AS unpaid_bills,

                (SELECT COALESCE(SUM(amount), 0)
                 FROM bills
                 WHERE payment_status = 'Unpaid')
                    AS unpaid_amount,

                (SELECT COUNT(*) FROM support_tickets)
                    AS total_tickets
        """).fetchone()

        ticket_status = conn.execute("""
            SELECT
                status,
                COUNT(*) AS ticket_count
            FROM support_tickets
            GROUP BY status
            ORDER BY ticket_count DESC
        """).fetchall()

        popular_packages = conn.execute("""
            SELECT
                p.package_name,
                COUNT(s.subscription_id) AS subscription_count
            FROM packages p
            LEFT JOIN subscriptions s
                ON p.package_id = s.package_id
            GROUP BY p.package_id, p.package_name
            ORDER BY subscription_count DESC
            LIMIT 5
        """).fetchall()

        return {
            "summary": dict(summary),
            "ticket_status": [
                dict(row) for row in ticket_status
            ],
            "popular_packages": [
                dict(row) for row in popular_packages
            ]
        }

    finally:
        conn.close()
