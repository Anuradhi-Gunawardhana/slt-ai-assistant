
from database import get_connection

conn = get_connection()
cursor = conn.cursor()

tables = [
    "customers",
    "packages",
    "subscriptions",
    "bills",
    "support_tickets",
    "staff",
    "staff_policies"
]

print("\n========== SLT DEMO DATABASE ==========\n")

for table in tables:

    cursor.execute(f"SELECT COUNT(*) FROM {table}")

    count = cursor.fetchone()[0]

    print(f"{table:20} : {count:,} records")


print("\n========== SAMPLE CUSTOMERS ==========\n")

cursor.execute("""
    SELECT customer_id, name, email, city
    FROM customers
    LIMIT 10
""")

for row in cursor.fetchall():
    print(dict(row))


print("\n========== SAMPLE PACKAGES ==========\n")

cursor.execute("""
    SELECT package_name, service_type, monthly_price, speed_mbps
    FROM packages
    LIMIT 10
""")

for row in cursor.fetchall():
    print(dict(row))


print("\n========== BILLING STATISTICS ==========\n")

cursor.execute("""
    SELECT
        payment_status,
        COUNT(*) AS bill_count,
        SUM(amount) AS total_amount
    FROM bills
    GROUP BY payment_status
""")

for row in cursor.fetchall():
    print(dict(row))


print("\n========== SUPPORT TICKET STATISTICS ==========\n")

cursor.execute("""
    SELECT status, COUNT(*) AS ticket_count
    FROM support_tickets
    GROUP BY status
""")

for row in cursor.fetchall():
    print(dict(row))


conn.close()
