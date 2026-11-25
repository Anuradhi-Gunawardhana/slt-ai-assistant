
from app import app

app.config["TESTING"] = True


def run_test(name, role=None, customer_id=None, staff_id=None,
             question=None, expected_status=200, expected_text=None):

    client = app.test_client()

    # Create a valid test session and CSRF token.
    with client.session_transaction() as session:
        session["csrf_token"] = "test-csrf-token"

        if role is not None:
            session["user_id"] = 999
            session["username"] = "security_test"
            session["role"] = role
            session["customer_id"] = customer_id
            session["staff_id"] = staff_id

    response = client.post(
        "/api/chat",
        json={"message": question},
        headers={"X-CSRF-Token": "test-csrf-token"}
    )

    print(f"\nTEST: {name}")
    print("HTTP status:", response.status_code)

    result = response.get_json() or {}
    print("Response:", result)

    passed = response.status_code == expected_status

    if expected_text:
        answer = result.get("answer", "").lower()
        passed = passed and expected_text.lower() in answer

    print("RESULT:", "PASSED" if passed else "FAILED")

    return passed


if __name__ == "__main__":

    results = []

    print("\n========== SECURITY TESTING ==========")

    # 1. Unauthenticated API request
    results.append(
        run_test(
            name="Unauthenticated API access",
            question="Show my bills",
            expected_status=302
        )
    )

    # 2. Customer requests admin report
    results.append(
        run_test(
            name="Customer blocked from admin report",
            role="customer",
            customer_id=1,
            question="Give me the admin business report",
            expected_text="not authorised"
        )
    )

    # 3. Customer requests staff tickets
    results.append(
        run_test(
            name="Customer blocked from staff tickets",
            role="customer",
            customer_id=1,
            question="Show tickets assigned to me",
            expected_text="not authorised"
        )
    )

    # 4. Staff requests customer bills
    results.append(
        run_test(
            name="Staff blocked from customer bills",
            role="staff",
            staff_id=1,
            question="Show my bills",
            expected_text="not authorised"
        )
    )

    # 5. Customer account 1 requests their own package
    results.append(
        run_test(
            name="Customer account 1 package access",
            role="customer",
            customer_id=1,
            question="Show my current package"
        )
    )

    # 6. Customer account 2 requests their own package
    results.append(
        run_test(
            name="Customer account 2 package access",
            role="customer",
            customer_id=2,
            question="Show my current package"
        )
    )

    print("\n========== SECURITY TEST SUMMARY ==========")
    print("Passed:", sum(results))
    print("Failed:", len(results) - sum(results))
    print("Total:", len(results))

    if all(results):
        print("\nALL SECURITY CHECKS PASSED.")
    else:
        print("\nSOME SECURITY CHECKS FAILED.")

