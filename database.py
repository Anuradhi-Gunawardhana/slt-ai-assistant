from dotenv import load_dotenv
load_dotenv()

import os
import sqlite3
from pathlib import Path


# Database configuration

BASE_DIR = Path(__file__).resolve().parent

DB_NAME = Path(
    os.environ.get(
        "DATABASE_PATH",
        str(BASE_DIR / "slt_demo.db")
    )
)


def get_connection():

    connection = sqlite3.connect(str(DB_NAME))

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.executescript("""

        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            city TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS packages (
            package_id INTEGER PRIMARY KEY,
            package_name TEXT NOT NULL,
            service_type TEXT,
            monthly_price REAL,
            speed_mbps INTEGER,
            data_limit_gb INTEGER,
            description TEXT
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            package_id INTEGER,
            status TEXT,
            start_date TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(package_id) REFERENCES packages(package_id)
        );

        CREATE TABLE IF NOT EXISTS bills (
            bill_id INTEGER PRIMARY KEY,
            subscription_id INTEGER,
            billing_month TEXT,
            amount REAL,
            payment_status TEXT,
            due_date TEXT,
            FOREIGN KEY(subscription_id)
                REFERENCES subscriptions(subscription_id)
        );

        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            department TEXT,
            job_title TEXT,
            city TEXT
        );

        CREATE TABLE IF NOT EXISTS support_tickets (
            ticket_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            assigned_staff_id INTEGER,
            issue_category TEXT,
            description TEXT,
            status TEXT,
            priority TEXT,
            created_at TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(assigned_staff_id) REFERENCES staff(staff_id)
        );

        CREATE TABLE IF NOT EXISTS staff_policies (
            policy_id INTEGER PRIMARY KEY,
            title TEXT,
            category TEXT,
            content TEXT,
            access_role TEXT DEFAULT 'staff'
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            customer_id INTEGER,
            staff_id INTEGER,
            FOREIGN KEY(customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY(staff_id) REFERENCES staff(staff_id)
        );

        """)

        connection.commit()

        print("Database tables created successfully.")

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()

