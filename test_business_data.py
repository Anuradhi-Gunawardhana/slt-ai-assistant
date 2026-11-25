
from pprint import pprint

from business_data import (
    get_customer_profile,
    get_customer_subscription,
    get_customer_bills,
    get_customer_tickets,
    get_staff_tickets,
    get_admin_report
)


print("\n========== CUSTOMER TEST ==========")

# Demo customer has customer_id = 1
print("\nCustomer Profile:")
pprint(get_customer_profile(1))

print("\nCustomer Subscriptions:")
pprint(get_customer_subscription(1))

print("\nCustomer Bills:")
pprint(get_customer_bills(1))

print("\nCustomer Support Tickets:")
pprint(get_customer_tickets(1))


print("\n========== STAFF TEST ==========")

# Demo staff has staff_id = 1
print("\nAssigned Staff Tickets:")
pprint(get_staff_tickets(1))


print("\n========== ADMIN TEST ==========")

print("\nAdmin Business Report:")
pprint(get_admin_report())


print("\n========== TEST COMPLETE ==========")
