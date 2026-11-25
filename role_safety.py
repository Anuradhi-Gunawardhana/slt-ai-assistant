import re

def reject_question(question, role):
    q = question.lower()
    if re.search(r"password|credential|api.key|secret.key|credit.card|bank.account|another customer|other customer|another employee|confidential database|personal information about|delete |transfer |ignore.*instructions", q):
        return "Access denied. This information or operation is not authorised."
    if re.search(r"weather|football|world cup|cricket score|lottery|capital of|write.*(program|application)|factorial", q):
        return "This question is outside the scope of the SLT assistant."
    if role == "customer" and re.search(r"internal staff|staff polic|admin.report|customer statistics|company.s total revenue", q):
        return "Access denied. This information is restricted."
    if role != "admin" and re.search(r"admin.only|admin.report|business.report|customer statistics|company.s total revenue", q):
        return "Access denied. Administrative information is restricted."
    return None
