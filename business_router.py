
import json
from database import get_connection
from contextlib import closing
from role_safety import reject_question

from business_data import (
    get_customer_profile,
    get_customer_subscription,
    get_customer_bills,
    get_customer_tickets,
    get_staff_tickets,
    get_admin_report
)


# Helper functions -

def get_ticket_value(ticket, *keys, default="N/A"):
    """Safely retrieve a ticket field."""

    for key in keys:
        value = ticket.get(key)

        if value is not None and str(value).strip():
            return str(value).strip()

    return default


def format_staff_tickets(tickets):
    """Format staff ticket records."""

    if not tickets:
        return "You currently have no tickets assigned to you."

    lines = [
        f"You have {len(tickets)} assigned ticket(s):",
        ""
    ]

    for ticket in tickets:

        ticket_id = get_ticket_value(
            ticket, "ticket_id", "id"
        )

        category = get_ticket_value(
            ticket, "category", "ticket_category",
            "issue_category"
        )

        status = get_ticket_value(
            ticket, "status", "ticket_status"
        )

        priority = get_ticket_value(
            ticket, "priority", "ticket_priority"
        )

        description = get_ticket_value(
            ticket, "description", "ticket_description",
            default=""
        )

        lines.append(f"Ticket ID: {ticket_id}")
        lines.append(f"Category: {category}")
        lines.append(f"Status: {status}")
        lines.append(f"Priority: {priority}")

        if description:
            lines.append(f"Description: {description}")

        lines.append("")

    return "\n".join(lines).strip()


def format_customer_bills(bills):
    """Format customer billing records."""

    if not bills:
        return "You currently have no billing records."

    lines = [
        f"Here are your {len(bills)} billing record(s):",
        ""
    ]

    for bill in bills:

        amount = bill.get("amount", 0)

        try:
            amount = float(amount)
            formatted_amount = f"LKR {amount:,.2f}"
        except (ValueError, TypeError):
            formatted_amount = str(amount)

        lines.append(f"Bill ID: {bill.get('bill_id', 'N/A')}")
        lines.append(
            f"Billing Month: {bill.get('billing_month', 'N/A')}"
        )
        lines.append(f"Amount: {formatted_amount}")
        lines.append(
            f"Payment Status: {bill.get('payment_status', 'N/A')}"
        )
        lines.append(f"Due Date: {bill.get('due_date', 'N/A')}")
        lines.append("")

    return "\n".join(lines).strip()


def format_customer_tickets(tickets):
    """Format customer support ticket records."""

    if not tickets:
        return "You currently have no support tickets."

    lines = [
        f"You have {len(tickets)} support ticket(s):",
        ""
    ]

    for ticket in tickets:

        lines.append(
            f"Ticket ID: {ticket.get('ticket_id', 'N/A')}"
        )
        lines.append(
            f"Category: {ticket.get('issue_category', 'N/A')}"
        )
        lines.append(
            f"Status: {ticket.get('status', 'N/A')}"
        )
        lines.append(
            f"Priority: {ticket.get('priority', 'N/A')}"
        )
        lines.append(
            f"Description: {ticket.get('description', 'N/A')}"
        )
        lines.append(
            f"Created At: {ticket.get('created_at', 'N/A')}"
        )
        lines.append("")

    return "\n".join(lines).strip()


def is_staff_ticket_question(question):
    """Identify staff ticket questions."""

    phrases = [
        "assigned tickets",
        "tickets assigned",
        "tickets are assigned to me",
        "tickets assigned to me",
        "my assigned tickets",
        "my staff tickets",
        "show my tickets",
        "my work tickets",
        "my high priority tickets",
        "my low priority tickets",
        "my medium priority tickets",
        "my open tickets",
        "my closed tickets",
        "my resolved tickets",
        "my in progress tickets"
    ]

    return any(phrase in question for phrase in phrases)


def answer_staff_ticket_question(question, staff_id):
    """Retrieve and answer staff ticket questions."""

    if not staff_id:
        return (
            "Your staff account is not linked to a staff record."
        )

    tickets = get_staff_tickets(staff_id)

    if not tickets:
        return "You currently have no tickets assigned to you."

    q = question.lower()

    # Priority filter

    priority_filter = None

    if "high priority" in q:
        priority_filter = "high"

    elif "medium priority" in q:
        priority_filter = "medium"

    elif "low priority" in q:
        priority_filter = "low"

    if priority_filter:

        tickets = [
            ticket for ticket in tickets
            if get_ticket_value(
                ticket,
                "priority",
                "ticket_priority",
                default=""
            ).lower() == priority_filter
        ]

    # Status filter

    status_filter = None

    for status in [
        "in progress",
        "open",
        "closed",
        "resolved"
    ]:

        if status in q:
            status_filter = status
            break

    if status_filter:

        tickets = [
            ticket for ticket in tickets
            if get_ticket_value(
                ticket,
                "status",
                "ticket_status",
                default=""
            ).lower() == status_filter
        ]

    # Count question

    count_phrases = [
        "how many",
        "count",
        "number of",
        "total number"
    ]

    if any(phrase in q for phrase in count_phrases):

        description = "assigned"

        if priority_filter:
            description += f" {priority_filter} priority"

        if status_filter:
            description += f" {status_filter}"

        return (
            f"You have {len(tickets)} {description} ticket(s)."
        )

    # List question

    if not tickets:
        return "No matching tickets were found."

    return format_staff_tickets(tickets)


# Main business router -

def route_business_question(
    question,
    role,
    customer_id=None,
    staff_id=None
):
    """
    Route business questions using authorised database records.

    Returns:
        Dictionary: Business question handled.
        None: Question should be handled by RAG.
    """

    q = question.lower().strip()

    refusal = reject_question(q, role)
    direct = refusal or direct_answer(q, role, customer_id)
    if direct is not None:
        return {"handled": True, "context": "", "message": direct}

    # 1. ADMIN reporting - 

    admin_keywords = [
        "admin report",
        "business report",
        "business statistics",
        "business overview",
        "overall statistics",
        "total customers",
        "total subscriptions",
        "unpaid amount",
        "popular packages",
        "ticket statistics",
        "show all business data"
    ]

    if any(keyword in q for keyword in admin_keywords):

        if role != "admin":
            return {
                "handled": True,
                "context": "",
                "message": (
                    "You are not authorised to access admin reports."
                )
            }

        report = get_admin_report()

        return {
            "handled": True,
            "context": json.dumps(report, indent=2),
            "message": ""
        }

    # 2. STAFF tickets - 

    if is_staff_ticket_question(q):

        if role != "staff":
            return {
                "handled": True,
                "context": "",
                "message": (
                    "You are not authorised to access staff ticket records."
                )
            }

        answer = answer_staff_ticket_question(
            q,
            staff_id
        )

        return {
            "handled": True,
            "context": "",
            "message": answer
        }

    # 3. CUSTOMER intent detection -


    customer_intent = None

    # Customer profile

    if any(phrase in q for phrase in [
        "my profile",
        "my account details",
        "my personal details",
        "show my details"
    ]):

        customer_intent = "profile"

    # Customer subscription / package

    elif any(phrase in q for phrase in [
        "my subscription",
        "my package",
        "my internet package",
        "my current package",
        "current internet package",
        "current package",
        "what package am i using",
        "which package am i using",
        "what is my package",
        "what is my current package",
        "what is my current internet package",
        "show my package",
        "show my current package",
        "show my internet package",
        "my broadband package",
        "which internet package do i have",
        "what broadband package do i have"
    ]):

        customer_intent = "subscription"

    # Customer bills

    elif any(phrase in q for phrase in [
        "my bill",
        "my bills",
        "my payment",
        "my payments",
        "payment status",
        "unpaid bill",
        "billing history",
        "my billing history",
        "show my bill",
        "show my bills",
        "how much do i owe"
    ]):

        customer_intent = "bills"

    # Customer support tickets

    elif any(phrase in q for phrase in [
        "my support ticket",
        "my support tickets",
        "my complaints",
        "my service requests",
        "my ticket status",
        "show my support tickets",
        "show my complaints"
    ]):

        customer_intent = "tickets"

    # 4. CUSTOMER data retrieval - 

    if customer_intent:

        if role != "customer":
            return {
                "handled": True,
                "context": "",
                "message": (
                    "You are not authorised to access customer account records."
                )
            }

        if not customer_id:
            return {
                "handled": True,
                "context": "",
                "message": (
                    "Your customer account is not linked to a customer record."
                )
            }

        if customer_intent == "profile":
            data = get_customer_profile(customer_id)

        elif customer_intent == "subscription":
            data = get_customer_subscription(customer_id)

        elif customer_intent == "bills":
            data = get_customer_bills(customer_id)

        elif customer_intent == "tickets":
            data = get_customer_tickets(customer_id)

        else:
            data = None

        # Direct formatting for bills and support tickets

        if customer_intent == "bills":

            answer = format_customer_bills(data)

            return {
                "handled": True,
                "context": "",
                "message": answer
            }

        if customer_intent == "tickets":

            answer = format_customer_tickets(data)

            return {
                "handled": True,
                "context": "",
                "message": answer
            }

        # Profile and subscription continue using the existing AI flow

        if not data:
            context = (
                "No matching records were found for this account."
            )

        else:
            context = json.dumps(
                data,
                indent=2,
                ensure_ascii=False
            )

        return {
            "handled": True,
            "context": context,
            "message": ""
        }

    
    # 5. Not a business question -  

    return None


def direct_answer(q, role, customer_id):
    def has(*phrases): return any(x in q for x in phrases)
    deny = "Access denied. This information is restricted."
    counts = {"customers":"customers", "staff":"staff", "packages":"packages", "subscriptions":"subscriptions", "support tickets":"support_tickets", "bills":"bills"}
    if has("how many", "customer statistics", "customer distribution", "common customer support issues"):
        with closing(get_connection()) as db:
            if has("customer distribution", "common customer support issues"):
                if role != "admin": return deny
                sql = "SELECT p.package_name, COUNT(DISTINCT s.customer_id) FROM packages p LEFT JOIN subscriptions s ON p.package_id=s.package_id GROUP BY p.package_id" if "distribution" in q else "SELECT issue_category, COUNT(*) FROM support_tickets GROUP BY issue_category ORDER BY COUNT(*) DESC"
                return "\n".join(f"{r[0]}: {r[1]}" for r in db.execute(sql)) or "No records found."
            if has("active subscriptions"):
                if role != "admin": return deny
                return f"Active subscriptions: {db.execute('SELECT COUNT(*) FROM subscriptions WHERE status = ?', ('Active',)).fetchone()[0]}"
            for term, table in counts.items():
                if has(term) and ("my" not in q):
                    if role != "admin": return deny
                    return f"{term.capitalize()}: {db.execute('SELECT COUNT(*) FROM '+table).fetchone()[0]}"
    if has("available internet packages", "internet packages are available"):
        with closing(get_connection()) as db:
            return "\n".join(f"{r[0]}: LKR {r[1]}, {r[2]} Mbps" for r in db.execute("SELECT package_name,monthly_price,speed_mbps FROM packages")) or "No packages found."
    if has("my customer id", "my monthly package price", "my subscription status", "internet package am i using", "my billing details", "any unpaid bills", "my account details"):
        if role != "customer": return deny
        if not customer_id: return "No linked customer account."
        if has("my customer id"): return f"Your customer ID is {customer_id}."
        if has("my account details"): return json.dumps(get_customer_profile(customer_id))
        if has("billing details", "unpaid bills"):
            bills = get_customer_bills(customer_id)
            if has("unpaid"): bills = [b for b in bills if b['payment_status'].lower() in ('unpaid','overdue')]
            return format_customer_bills(bills)
        subs = get_customer_subscription(customer_id)
        if not subs: return "No subscriptions found."
        return "\n".join(f"{r['package_name']}: LKR {r['monthly_price']} per month; status {r['status']}" for r in subs)
    topics = [("complaint handling", "demo_complaints"), ("billing complaint", "demo_complaints"), ("unresolved complaint", "demo_complaints"), ("reports slow internet", "demo_interrupt"), ("service interruption", "demo_interrupt"), ("escalate a technical", "staff_escalation"), ("information should i collect", "demo_collect"), ("customer service guidelines", "demo_service"), ("unhappy customer", "demo_service"), ("cancellation requests", "demo_cancel"), ("troubleshoot slow internet", "faq_internet_slow"), ("improve my wi-fi", "demo_wifi"), ("submit a complaint", "demo_submit")]
    for phrase, key in topics:
        if phrase in q:
            with closing(get_connection()) as db:
                row = db.execute("SELECT content,access_role FROM knowledge_documents WHERE source_key=?", (key,)).fetchone()
                if not row: return "No guidance found."
                if row['access_role'] not in ('all',role) and role != 'admin': return deny
                return row['content']
    if has("internal staff policies") and role in ('staff','admin'):
        with closing(get_connection()) as db:
            return "\n".join(r[0]+": "+r[1] for r in db.execute("SELECT title,content FROM staff_policies WHERE access_role='staff'"))
    return None
