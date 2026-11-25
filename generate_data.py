
import random
from datetime import date, timedelta

from database import initialize_database, get_connection

random.seed(42)

# Sample data -

first_names = [
    "Kamal", "Nimal", "Sunil", "Kasun", "Tharindu",
    "Amara", "Nadeesha", "Chamari", "Dilani", "Ishara",
    "Saman", "Ruwan", "Sanduni", "Harsha", "Malith",
    "Anjali", "Rashmi", "Supun", "Dinesh", "Piumi"
]

last_names = [
    "Perera", "Silva", "Fernando", "Jayasinghe",
    "Wickramasinghe", "Gunawardena", "Bandara",
    "De Silva", "Karunaratne", "Senanayake"
]

cities = [
    "Colombo", "Kandy", "Galle", "Kalutara",
    "Gampaha", "Negombo", "Matara", "Kurunegala",
    "Jaffna", "Anuradhapura", "Ratnapura",
    "Badulla", "Trincomalee", "Batticaloa"
]

departments = [
    "Customer Service", "Technical Support",
    "Network Operations", "Human Resources",
    "Finance", "Sales", "IT"
]

issue_categories = [
    "Slow Internet", "Connection Failure",
    "Billing Issue", "Package Change",
    "Router Problem", "Service Interruption"
]

statuses = ["Open", "In Progress", "Resolved", "Closed"]
priorities = ["Low", "Medium", "High", "Critical"]


# Helper functions - 

def random_name():
    return (
        random.choice(first_names)
        + " "
        + random.choice(last_names)
    )


def random_date(days_back=900):
    start = date.today() - timedelta(days=days_back)
    result = start + timedelta(
        days=random.randint(0, days_back)
    )
    return result.isoformat()


# Create DB - 

from database import DB_NAME
if DB_NAME.exists():
    raise SystemExit("Refusing to overwrite an existing database. Choose a new DATABASE_PATH.")
DB_NAME.parent.mkdir(parents=True, exist_ok=True)
initialize_database()

conn = get_connection()
cursor = conn.cursor()

# Reset old generated records.
# This makes the script safe to run again.
cursor.execute("DELETE FROM bills")
cursor.execute("DELETE FROM support_tickets")
cursor.execute("DELETE FROM subscriptions")
cursor.execute("DELETE FROM users")
cursor.execute("DELETE FROM customers")
cursor.execute("DELETE FROM packages")
cursor.execute("DELETE FROM staff_policies")
cursor.execute("DELETE FROM staff")


# 1. PACKAGES: 20

packages = []

for i in range(1, 21):

    service_type = random.choice([
        "Fibre Broadband",
        "ADSL Broadband",
        "Mobile Data",
        "Business Internet"
    ])

    speed = random.choice([20, 40, 60, 100, 200, 300])
    price = random.choice([1490, 1990, 2490, 2990, 3990, 4990])

    package = (
        i,
        f"SLT Demo {service_type} {i}",
        service_type,
        price,
        speed,
        random.choice([100, 200, 500, 1000, 2000]),
        f"Fictional {service_type} package with {speed} Mbps speed."
    )

    packages.append(package)

cursor.executemany("""
    INSERT INTO packages
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", packages)

# 2. CUSTOMERS: 1,000

customers = []

for i in range(1, 1001):

    name = random_name()

    customers.append((
        i,
        name,
        f"customer{i}@example.com",
        f"07{random.randint(10000000, 99999999)}",
        random.choice(cities),
        random_date()
    ))

cursor.executemany("""
    INSERT INTO customers
    VALUES (?, ?, ?, ?, ?, ?)
""", customers)

# 3. STAFF: 150

staff_members = []

for i in range(1, 151):

    staff_members.append((
        i,
        random_name(),
        f"staff{i}@example.com",
        random.choice(departments),
        random.choice([
            "Support Officer",
            "Technical Officer",
            "Executive",
            "Manager",
            "Analyst"
        ]),
        random.choice(cities)
    ))

cursor.executemany("""
    INSERT INTO staff
    VALUES (?, ?, ?, ?, ?, ?)
""", staff_members)


# 4. SUBSCRIPTIONS: 1,500

subscriptions = []

for i in range(1, 1501):

    subscriptions.append((
        i,
        random.randint(1, 1000),
        random.randint(1, 20),
        random.choice(["Active", "Active", "Active", "Suspended", "Cancelled"]),
        random_date()
    ))

cursor.executemany("""
    INSERT INTO subscriptions
    VALUES (?, ?, ?, ?, ?)
""", subscriptions)


# 5. BILLS: 6,000

bills = []

for i in range(1, 6001):

    subscription_id = random.randint(1, 1500)
    month = random.randint(1, 12)
    year = random.choice([2025, 2026])

    amount = random.choice([
        1490, 1990, 2490, 2990, 3990, 4990
    ])

    payment_status = random.choices(
        ["Paid", "Unpaid", "Overdue"],
        weights=[65, 25, 10]
    )[0]

    bills.append((
        i,
        subscription_id,
        f"{year}-{month:02d}",
        amount,
        payment_status,
        f"{year}-{month:02d}-28"
    ))

cursor.executemany("""
    INSERT INTO bills
    VALUES (?, ?, ?, ?, ?, ?)
""", bills)


# 6. SUPPORT TICKETS: 2,500

tickets = []

for i in range(1, 2501):

    tickets.append((
        i,
        random.randint(1, 1000),
        random.randint(1, 150),
        random.choice(issue_categories),
        "Fictional customer support request regarding a service issue.",
        random.choice(statuses),
        random.choice(priorities),
        random_date(365)
    ))

cursor.executemany("""
    INSERT INTO support_tickets
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", tickets)


# 7. STAFF POLICIES: 30

policy_topics = [
    ("Annual Leave", "Employees must submit annual leave requests through the approved internal process."),
    ("Sick Leave", "Employees should notify their supervisor when unable to attend work due to illness."),
    ("Attendance", "Employees are expected to follow their assigned working hours."),
    ("Data Protection", "Employees must protect customer information and only access authorised records."),
    ("Password Security", "Employees must use strong passwords and never share their credentials."),
    ("Customer Complaints", "Customer complaints should be recorded and assigned to the relevant support team."),
    ("Remote Work", "Remote work arrangements require approval from the relevant manager."),
    ("IT Support", "Technical issues should be reported through the approved IT support process."),
    ("Workplace Conduct", "Employees should maintain professional conduct in the workplace."),
    ("Equipment Usage", "Company equipment should be used responsibly and for authorised purposes.")
]

policies = []

for i in range(1, 31):

    title, content = policy_topics[(i - 1) % len(policy_topics)]

    policies.append((
        i,
        f"{title} Policy - Version {((i - 1) // 10) + 1}",
        random.choice([
            "Human Resources",
            "IT",
            "Operations",
            "Customer Service"
        ]),
        content,
        "staff"
    ))

cursor.executemany("""
    INSERT INTO staff_policies
    VALUES (?, ?, ?, ?, ?)
""", policies)

conn.commit()
conn.close()

print("\nSLT Demo dataset generated successfully!")
print("Customers: 1,000")
print("Packages: 20")
print("Subscriptions: 1,500")
print("Bills: 6,000")
print("Support tickets: 2,500")
print("Staff: 150")
print("Staff policies: 30")
