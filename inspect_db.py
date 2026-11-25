
from database import get_connection


def inspect_database():
    conn = get_connection()

    try:
        print("\n========== DATABASE INSPECTION ==========\n")

        tables = conn.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """).fetchall()

        for table in tables:
            table_name = table["name"]

            print("\n" + "=" * 50)
            print("TABLE:", table_name)
            print("=" * 50)

            columns = conn.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            print("\nCOLUMNS:")
            for column in columns:
                print(
                    column["name"],
                    "| Type:", column["type"],
                    "| Primary Key:", column["pk"]
                )

            print("\nSAMPLE RECORDS:")

            rows = conn.execute(
                f'SELECT * FROM "{table_name}" LIMIT 3'
            ).fetchall()

            for row in rows:
                print(dict(row))

            if not rows:
                print("No records found.")

        print("\n========== INSPECTION COMPLETE ==========\n")

    finally:
        conn.close()


if __name__ == "__main__":
    inspect_database()
