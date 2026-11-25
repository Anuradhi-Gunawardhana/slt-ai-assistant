
from database import get_connection

documents = [
    {
        "source_key": "faq_internet_slow",
        "title": "Troubleshooting slow internet",
        "category": "troubleshooting",
        "access_role": "all",
        "content": (
            "If your internet connection is slow, restart your router. "
            "Check whether multiple devices are using the connection. "
            "Move closer to the Wi-Fi router and check the cables. "
            "If the issue continues, contact customer support."
        )
    },
    {
        "source_key": "faq_router_restart",
        "title": "How to restart a router",
        "category": "troubleshooting",
        "access_role": "all",
        "content": (
            "Switch off the router using its power button. "
            "Wait approximately 30 seconds. Switch it on again "
            "and allow the router to reconnect."
        )
    },
    {
        "source_key": "faq_wifi_security",
        "title": "Wi-Fi security",
        "category": "customer_faq",
        "access_role": "all",
        "content": (
            "Use a strong Wi-Fi password containing a combination "
            "of letters, numbers and symbols. Do not share your "
            "Wi-Fi password with unknown people."
        )
    },
    {
        "source_key": "faq_bill_payment",
        "title": "Bill payment information",
        "category": "billing",
        "access_role": "all",
        "content": (
            "Customers should check their billing statement for "
            "the amount due and payment due date. Payment status "
            "can be checked through the account or customer support."
        )
    },
    {
        "source_key": "faq_package_change",
        "title": "Changing a service package",
        "category": "packages",
        "access_role": "all",
        "content": (
            "A customer who wants to change a package should contact "
            "customer support and request information about available "
            "packages, eligibility and any applicable charges."
        )
    },
    {
        "source_key": "faq_no_connection",
        "title": "No internet connection",
        "category": "troubleshooting",
        "access_role": "all",
        "content": (
            "Check that the router is powered on and connected correctly. "
            "Check the indicator lights and restart the router. "
            "If there is still no connection, contact customer support."
        )
    },
    {
        "source_key": "customer_account_privacy",
        "title": "Customer account privacy",
        "category": "customer_policy",
        "access_role": "customer",
        "content": (
            "Customers should protect their account credentials. "
            "Do not share passwords or verification codes. "
            "Only authorised account holders should access account details."
        )
    },
    {
        "source_key": "staff_ticket_handling",
        "title": "Support ticket handling procedure",
        "category": "staff_procedure",
        "access_role": "staff",
        "content": (
            "Staff should review the ticket description, verify the "
            "customer's reported issue, assign an appropriate priority "
            "and update the ticket status after taking action."
        )
    },
    {
        "source_key": "staff_customer_verification",
        "title": "Customer verification procedure",
        "category": "staff_procedure",
        "access_role": "staff",
        "content": (
            "Before discussing account-specific information, staff "
            "must verify the customer's identity using the approved "
            "verification process. Never disclose private information "
            "before verification."
        )
    },
    {
        "source_key": "staff_escalation",
        "title": "Escalating technical issues",
        "category": "staff_procedure",
        "access_role": "staff",
        "content": (
            "Staff should escalate unresolved technical issues to "
            "the relevant technical team. Include the ticket reference, "
            "issue description and troubleshooting steps already taken."
        )
    },
    {
        "source_key": "admin_reporting",
        "title": "Administrative reporting guidance",
        "category": "admin",
        "access_role": "admin",
        "content": (
            "Administrators can review aggregated customer counts, "
            "billing summaries and support ticket statistics. "
            "Reports should use database records and clearly identify "
            "the reporting period."
        )
    },
    {
        "source_key": "admin_data_protection",
        "title": "Administrative data protection",
        "category": "admin",
        "access_role": "admin",
        "content": (
            "Administrators should restrict access to sensitive records, "
            "use authorised accounts and avoid sharing customer data "
            "outside approved business purposes."
        )
    }
]


documents.extend([{'source_key': 'demo_complaints', 'title': 'Complaint handling', 'category': 'demo', 'access_role': 'staff', 'content': 'Demonstration guidance, not official SLT policy: Verify identity, record the issue, review authorised records, explain next steps and escalate unresolved cases.'}, {'source_key': 'demo_interrupt', 'title': 'Service interruption', 'category': 'demo', 'access_role': 'staff', 'content': 'Demonstration guidance, not official SLT policy: Confirm symptoms, check outage notices if available, document the issue and escalate unresolved problems.'}, {'source_key': 'demo_collect', 'title': 'Customer information collection', 'category': 'demo', 'access_role': 'staff', 'content': 'Demonstration guidance, not official SLT policy: Collect only necessary service and contact details through approved channels; never request secrets.'}, {'source_key': 'demo_service', 'title': 'Customer service guidelines', 'category': 'demo', 'access_role': 'staff', 'content': 'Demonstration guidance, not official SLT policy: Listen calmly, acknowledge concerns, document actions and agree follow-up.'}, {'source_key': 'demo_cancel', 'title': 'Cancellation requests', 'category': 'demo', 'access_role': 'staff', 'content': 'Demonstration guidance, not official SLT policy: Verify identity and refer the request to the authorised cancellation process. This assistant cannot cancel services.'}, {'source_key': 'demo_wifi', 'title': 'Improve Wi-Fi signal', 'category': 'demo', 'access_role': 'all', 'content': 'Demonstration guidance, not official SLT policy: Place the router centrally, reduce obstacles and interference, and test near the router.'}, {'source_key': 'demo_submit', 'title': 'Submit a complaint', 'category': 'demo', 'access_role': 'all', 'content': 'Demonstration guidance, not official SLT policy: Contact customer support, describe the issue and request a ticket reference.'}])

def seed_knowledge():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_documents (
            doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_key TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            category TEXT,
            access_role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    for doc in documents:
        cursor.execute("""
            INSERT OR IGNORE INTO knowledge_documents
            (source_key, title, category, access_role, content)
            VALUES (?, ?, ?, ?, ?)
        """, (
            doc["source_key"],
            doc["title"],
            doc["category"],
            doc["access_role"],
            doc["content"]
        ))

    conn.commit()

    count = cursor.execute(
        "SELECT COUNT(*) FROM knowledge_documents"
    ).fetchone()[0]

    conn.close()

    print("Knowledge documents seeded successfully.")
    print("Total documents:", count)


if __name__ == "__main__":
    seed_knowledge()
