
import re
from database import get_connection


ROLE_ACCESS = {
    "customer": ["all", "customer"],
    "staff": ["all", "staff"],
    "admin": ["all", "customer", "staff", "admin"]
}


STOP_WORDS = {
    "the", "is", "are", "a", "an", "to", "for",
    "of", "my", "me", "how", "what", "can", "i",
    "do", "does", "and", "in", "on", "with",
    "please", "explain", "tell", "about", "procedure",
    "should", "could", "would", "you", "your"
}


def extract_keywords(question):

    words = re.findall(
        r"[a-zA-Z0-9]+",
        question.lower()
    )

    keywords = [
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    ]

    return list(dict.fromkeys(keywords))


def retrieve_documents(question, role, limit=4):

    if role not in ROLE_ACCESS:
        return []

    keywords = extract_keywords(question)

    if not keywords:
        return []

    allowed_roles = ROLE_ACCESS[role]

    conn = get_connection()

    try:

        role_placeholders = ",".join(
            ["?"] * len(allowed_roles)
        )

        sql = f"""
            SELECT
                doc_id,
                title,
                category,
                content,
                access_role
            FROM knowledge_documents
            WHERE access_role IN ({role_placeholders})
        """

        rows = conn.execute(
            sql,
            allowed_roles
        ).fetchall()

    finally:
        conn.close()

    ranked_documents = []

    for row in rows:

        title_words = extract_keywords(row["title"])

        content_words = extract_keywords(row["content"])

        title_matches = [
            word for word in keywords
            if word in title_words
        ]

        content_matches = [
            word for word in keywords
            if word in content_words
        ]

        score = (
            len(title_matches) * 3
            + len(content_matches)
        )

        if score >= 2:

            ranked_documents.append({
                "doc_id": row["doc_id"],
                "title": row["title"],
                "category": row["category"],
                "content": row["content"],
                "access_role": row["access_role"],
                "score": score
            })

    ranked_documents.sort(
        key=lambda document: document["score"],
        reverse=True
    )

    return ranked_documents[:limit]


def build_context(documents):

    if not documents:
        return "No relevant authorised documents were found."

    context_parts = []

    for document in documents:

        context_parts.append(
            f"""
Title: {document['title']}
Category: {document['category']}
Content: {document['content']}
"""
        )

    return "\n".join(context_parts)
