
import os
import secrets
from hmac import compare_digest
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from werkzeug.security import check_password_hash

from database import get_connection
from rag import retrieve_documents, build_context
from ai_engine import generate_response
from business_router import route_business_question
from role_safety import reject_question


# Application config -

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is missing. Set it before starting the app."
    )

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("FLASK_HTTPS", "false").lower() == "true"
)


# CSRF protection -

def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

    return session["csrf_token"]


def validate_csrf_token(token):
    saved_token = session.get("csrf_token")

    if not saved_token or not token:
        return False

    return compare_digest(saved_token, token)


# Login required decorater - 

def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return decorated_function


# Home - 

@app.route("/")
def index():

    if "user_id" in session:
        return redirect(url_for("chat_page"))

    return redirect(url_for("login"))


# Login - 

@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("chat_page"))

    if request.method == "POST":

        if not validate_csrf_token(
            request.form.get("csrf_token")
        ):
            return render_template(
                "login.html",
                error="Invalid security token. Please try again.",
                csrf_token=get_csrf_token()
            ), 400

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            return render_template(
                "login.html",
                error="Please enter your username and password.",
                csrf_token=get_csrf_token()
            )

        connection = get_connection()

        try:
            user = connection.execute(
                """
                SELECT
                    user_id,
                    username,
                    password_hash,
                    role,
                    customer_id,
                    staff_id
                FROM users
                WHERE username = ?
                """,
                (username,)
            ).fetchone()

        finally:
            connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session.clear()

            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["customer_id"] = user["customer_id"]
            session["staff_id"] = user["staff_id"]

            # Generate a new CSRF token after login
            session["csrf_token"] = secrets.token_urlsafe(32)

            return redirect(url_for("chat_page"))

        return render_template(
            "login.html",
            error="Invalid username or password.",
            csrf_token=get_csrf_token()
        )

    return render_template(
        "login.html",
        csrf_token=get_csrf_token()
    )


# Logout -

@app.route("/logout", methods=["POST"])
@login_required
def logout():

    if not validate_csrf_token(
        request.form.get("csrf_token")
    ):
        return "Invalid security token.", 400

    session.clear()

    return redirect(url_for("login"))


# Chat page -

@app.route("/chat")
@login_required
def chat_page():

    return render_template(
        "chat.html",
        username=session.get("username"),
        role=session.get("role"),
        csrf_token=get_csrf_token()
    )


# Customer restricted question check -

def is_customer_restricted_question(question):

    restricted_phrases = [
        "staff customer verification procedure",
        "staff verification procedure",
        "customer verification procedure",
        "internal staff procedure",
        "internal verification process",
        "staff login procedure",
        "admin procedure",
        "administrative procedure",
        "staff policy",
        "internal policy"
    ]

    question = question.lower()

    return any(
        phrase in question
        for phrase in restricted_phrases
    )

# Chat API -

@app.route("/api/chat", methods=["POST"])
@login_required
def chat_api():

   
    # CSRF validation -

    csrf_token = request.headers.get("X-CSRF-Token")

    if not validate_csrf_token(csrf_token):
        return jsonify({
            "error": "Invalid security token. Refresh the page and try again."
        }), 400


    # GET & validate user message -

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid request."
        }), 400

    question = data.get("message", "")

    if not isinstance(question, str):
        return jsonify({
            "error": "Message must be text."
        }), 400

    question = question.strip()

    if not question:
        return jsonify({
            "error": "Please enter a question."
        }), 400

    if len(question) > 1000:
        return jsonify({
            "error": "Message is too long. Maximum 1000 characters."
        }), 400

    # GET authenticated user info -

    user_id = session.get("user_id")
    username = session.get("username")
    role = session.get("role")
    customer_id = session.get("customer_id")
    staff_id = session.get("staff_id")


    # Check valid user role - 


    if role not in ["customer", "staff", "admin"]:
        return jsonify({
            "error": "Invalid user role."
        }), 403


    # Role based doc acccess - 

    allowed_roles = {
        "customer": ["all", "customer"],
        "staff": ["all", "staff"],
        "admin": ["all", "customer", "staff", "admin"]
    }


    refusal = reject_question(question, role)
    if refusal:
        return jsonify({"answer": refusal, "sources": []})

    # Customer restricted topics - 


    if role == "customer" and is_customer_restricted_question(question):

        return jsonify({
            "answer": (
                "I'm sorry, but I cannot provide internal "
                "staff or administrative information."
            ),
            "sources": []
        })


    # Business data router -


    try:

        business_result = route_business_question(
            question,
            role,
            customer_id,
            staff_id
        )

        if business_result is not None:

            # Direct access-denial response -
            if business_result.get("message"):

                return jsonify({
                    "answer": business_result["message"],
                    "sources": []
                })

            # Generate answer using authorised business data -
            business_context = business_result.get("context", "")

            if not business_context:

                return jsonify({
                    "answer": (
                        "I couldn't find sufficient authorised "
                        "information to answer your question."
                    ),
                    "sources": []
                })

            answer = generate_response(
                question,
                business_context
            )

            return jsonify({
                "answer": answer,
                "sources": ["Business Database"]
            })

    except Exception as error:

        app.logger.exception(
            "Business data processing failed"
        )

        return jsonify({
            "error": "Unable to process business data right now."
        }), 500

    # RAG knowledge retrivel -

    try:

        documents = retrieve_documents(
            question,
            role
        )

        # Keep only documents authorised for this role - 
        authorised_documents = [
            document
            for document in documents
            if document.get("access_role") in allowed_roles[role]
        ]

        # No authorised knowledge found - 
        if not authorised_documents:

            return jsonify({
                "answer": (
                    "I couldn't find sufficient authorised "
                    "information to answer your question."
                ),
                "sources": []
            })

        # Build context from retrieved documents -
        context = build_context(authorised_documents)

        if not context.strip():

            return jsonify({
                "answer": (
                    "I couldn't find sufficient authorised "
                    "information to answer your question."
                ),
                "sources": []
            })

        # Local AI response -

        answer = generate_response(
            question,
            context
        )

        source_titles = list(dict.fromkeys(
            document.get("title", "Knowledge Document")
            for document in authorised_documents
        ))

        return jsonify({
            "answer": answer,
            "sources": source_titles
        })

    except Exception:

        app.logger.exception(
            "Knowledge retrieval or AI generation failed"
        )

        return jsonify({
            "error": "Unable to generate a response right now."
        }), 500


# Application start -

if __name__ == "__main__":

    app.run(
    host="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    debug=False
)

