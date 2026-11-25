import os
import secrets

from database import get_connection
from werkzeug.security import generate_password_hash

conn = get_connection()
cursor = conn.cursor()

demo_users = [
    (
        "customer_demo",
        os.getenv("DEMO_CUSTOMER_PASSWORD") or secrets.token_urlsafe(18),
        "customer",
        1,
        None
    ),
    (
        "staff_demo",
        os.getenv("DEMO_STAFF_PASSWORD") or secrets.token_urlsafe(18),
        "staff",
        None,
        1
    ),
    (
        "admin_demo",
        os.getenv("DEMO_ADMIN_PASSWORD") or secrets.token_urlsafe(18),
        "admin",
        None,
        None
    )
]

for username, password, role, customer_id, staff_id in demo_users:

    if cursor.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
        continue
    password_hash = generate_password_hash(password)

    cursor.execute("""
        INSERT OR IGNORE INTO users
        (username, password_hash, role, customer_id, staff_id)
        VALUES (?, ?, ?, ?, ?)
    """, (
        username,
        password_hash,
        role,
        customer_id,
        staff_id
    ))

    print(f"New demo login: {username} / {password}")

conn.commit()
conn.close()

print("Demo accounts created successfully.")
print("Customer: customer_demo")
print("Staff: staff_demo")
print("Admin: admin_demo")
