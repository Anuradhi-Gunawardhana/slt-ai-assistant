
from rag import retrieve_documents


def test_rag(question, role):

    print("\n" + "=" * 55)
    print("ROLE:", role)
    print("QUESTION:", question)
    print("-" * 55)

    documents = retrieve_documents(question, role)

    if not documents:
        print("No authorised documents retrieved.")
        return

    for document in documents:
        print("Title:", document["title"])
        print("Access:", document["access_role"])
        print("Score:", document["score"])
        print("-" * 30)

    # Security verification
    allowed_roles = {
        "customer": ["all", "customer"],
        "staff": ["all", "staff"],
        "admin": ["all", "customer", "staff", "admin"]
    }

    for document in documents:
        if document["access_role"] not in allowed_roles[role]:
            print("SECURITY TEST FAILED")
            return

    print("SECURITY TEST PASSED")


# Customer tests
test_rag(
    "How can I fix slow internet?",
    "customer"
)

test_rag(
    "Explain the staff customer verification procedure",
    "customer"
)

test_rag(
    "Explain administrative reporting",
    "customer"
)


# Staff tests
test_rag(
    "How should I handle a customer support ticket?",
    "staff"
)

test_rag(
    "Explain administrative reporting",
    "staff"
)


# Admin tests
test_rag(
    "How can I prepare an administrative report?",
    "admin"
)
