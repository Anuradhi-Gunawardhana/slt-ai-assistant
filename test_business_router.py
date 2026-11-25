
from business_router import route_business_question


print("\n========== BUSINESS ROUTER TESTS ==========")

tests = [
    {
        "question": "Show my current package",
        "role": "customer",
        "customer_id": 1
    },
    {
        "question": "Show my bills",
        "role": "customer",
        "customer_id": 1
    },
    {
        "question": "Show my support tickets",
        "role": "customer",
        "customer_id": 1
    },
    {
        "question": "Show tickets assigned to me",
        "role": "staff",
        "staff_id": 1
    },
    {
        "question": "Give me the business report",
        "role": "admin"
    },
    {
        "question": "Show the admin report",
        "role": "customer",
        "customer_id": 1
    },
    {
        "question": "How can I restart my router?",
        "role": "customer",
        "customer_id": 1
    }
]

for test in tests:
    print("\nQuestion:", test["question"])
    print("Role:", test["role"])

    result = route_business_question(
        question=test["question"],
        role=test["role"],
        customer_id=test.get("customer_id"),
        staff_id=test.get("staff_id")
    )

    if result is None:
        print("Result: RAG FALLBACK")
    elif result["message"]:
        print("Result: ACCESS DENIED")
        print("Message:", result["message"])
    else:
        print("Result: BUSINESS DATA RETRIEVED")
        print("Context:", result["context"][:300])

print("\n========== TESTS COMPLETED ==========")
