import re
from datetime import datetime, timezone

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from app import db
from app.models.user import User


auth_bp = Blueprint("auth", __name__)


def normalize_phone(phone):
    phone = phone.strip().replace(" ", "").replace("-", "")

    if phone.startswith("09"):
        phone = "+98" + phone[1:]

    elif phone.startswith("9"):
        phone = "+98" + phone

    elif phone.startswith("+98"):
        pass

    else:
        return None

    if not re.fullmatch(r"\+989\d{9}", phone):
        return None

    return phone


@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    phone_input = request.form.get("phone_number", "")
    display_name = request.form.get("display_name", "").strip()

    if not username or not password or not phone_input or not display_name:
        flash("All fields are required.", "error")
        return redirect(url_for("auth.register"))

    if len(username) < 3 or len(username) > 32:
        flash("Username must be between 3 and 32 characters.", "error")
        return redirect(url_for("auth.register"))

    if not re.fullmatch(r"[A-Za-z0-9_]+", username):
        flash(
            "Username can only contain letters, numbers and underscore.",
            "error"
        )
        return redirect(url_for("auth.register"))

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return redirect(url_for("auth.register"))

    if len(display_name) < 2 or len(display_name) > 50:
        flash(
            "Display name must be between 2 and 50 characters.",
            "error"
        )
        return redirect(url_for("auth.register"))

    phone_number = normalize_phone(phone_input)

    if not phone_number:
        flash("Invalid Iranian phone number.", "error")
        return redirect(url_for("auth.register"))

    existing_username = User.query.filter_by(
        username=username
    ).first()

    if existing_username:
        flash("Username is already taken.", "error")
        return redirect(url_for("auth.register"))

    existing_phone = User.query.filter_by(
        phone_number=phone_number
    ).first()

    if existing_phone:
        flash("This phone number is already registered.", "error")
        return redirect(url_for("auth.register"))

    user = User(
        username=username,
        phone_number=phone_number,
        display_name=display_name
    )

    user.set_password(password)

    db.session.add(user)

    try:
        db.session.commit()

    except Exception:
        db.session.rollback()

        flash(
            "Something went wrong while creating the account.",
            "error"
        )

        return redirect(url_for("auth.register"))

    flash("Account created successfully!", "success")

    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        flash(
            "Username and password are required.",
            "error"
        )
        return redirect(url_for("auth.login"))

    user = User.query.filter_by(
        username=username
    ).first()

    if not user:
        flash(
            "Invalid username or password.",
            "error"
        )
        return redirect(url_for("auth.login"))

    if user.is_banned:
        flash(
            "This account has been banned.",
            "error"
        )
        return redirect(url_for("auth.login"))

    if not user.check_password(password):
        flash(
            "Invalid username or password.",
            "error"
        )
        return redirect(url_for("auth.login"))

    session.clear()

    session["user_id"] = user.id
    session["username"] = user.username

    user.last_seen = datetime.now(timezone.utc)

    db.session.commit()

    return redirect(url_for("auth.dashboard"))


@auth_bp.route("/dashboard")
def dashboard():

    user_id = session.get("user_id")

    if not user_id:
        return redirect(url_for("auth.login"))

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        user=user
    )


@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("auth.login"))
