from datetime import timedelta
import os
from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    session,
    Blueprint,
    abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)
from functools import wraps
from extensions import db, login_manager, oauth
from form import RegisterForm, LoginForm
from models import UserDatabase

auth_bp = Blueprint("auth", __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(UserDatabase, int(user_id))

def admin_only(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or  current_user.email.strip().lower() !=  "rohanmalve810@gmail.com":
            flash("You do not have permission to view that page.", "danger")
            return redirect(url_for('main.home_page'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    user_register = RegisterForm()
    if user_register.validate_on_submit():
        user_email = user_register.Email.data
        result = db.session.execute(
            db.select(UserDatabase).where(UserDatabase.email == user_email)
        )
        user = result.scalar()

        if user:
            flash("You've already signed up with that email, log in instead!", "warning")
            return redirect(url_for("auth.login"))

        hashed_password = generate_password_hash(
            user_register.Password.data, method="scrypt", salt_length=16
        )
        new_user = UserDatabase(
            email=user_email,
            password=hashed_password,
            name=user_register.Name.data,
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=user_register)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    user_login = LoginForm()
    if user_login.validate_on_submit():
        user_email = user_login.Email.data
        user_password = user_login.Password.data
        result = db.session.execute(db.select(UserDatabase).filter_by(email=user_email))
        user = result.scalar()

        if not user:
            flash("That email does not exist, please try again.", "danger")
            return redirect(url_for("auth.login"))
        if not user.is_password_auth():
            flash("Please use Google login for this account.", "info")
            return redirect(url_for("auth.login_google"))
        elif not check_password_hash(user.password, user_password):
            flash("Password incorrect, please try again.", "danger")
            return redirect(url_for("auth.login"))
        else:
            session_duration = timedelta(minutes=10)
            login_user(user, remember=True, duration=session_duration)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.get_all_items"))

    return render_template("login.html", form=user_login)

@auth_bp.route("/login/google")
def login_google():
    try:
        redirect_uri = url_for("auth.authorize_google", _external=True)
        return oauth.google.authorize_redirect(redirect_uri)
    except Exception as e:
        flash("An error occurred during Google login.", "error")
        return "Error occurred during login"

@auth_bp.route("/authorize/google")
def authorize_google():
    try:
        token = oauth.google.authorize_access_token()
        userinfo_endpoint = oauth.google.server_metadata["userinfo_endpoint"]
        resp = oauth.google.get(userinfo_endpoint)
        user_info = resp.json()
        email = user_info.get("email")
        session["user_pic"] = user_info.get("picture")

        if not email:
            flash("Could not get email from Google.", "error")
            return redirect(url_for("auth.login"))

        user = UserDatabase.query.filter_by(email=email).first()
        if not user:
            user = UserDatabase(
                email=email,
                name=user_info.get("name", email),
                password=None,
                is_oauth_user=True,
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        session["oauth_token"] = token

        flash("Logged in successfully with Google.", "success")
        return redirect(url_for("auth.dashboard"))
    except Exception as e:
        flash("An error occurred during Google authorization.", "error")
        return redirect(url_for("auth.login"))

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    user_pic = session.get("user_pic")
    return render_template("dashboard.html", current_user=current_user, user_pic=user_pic)

@auth_bp.route("/logout")
def logout():
    logout_user()
    session.pop("oauth_token", None)
    session.pop("user_pic", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.get_all_items"))
