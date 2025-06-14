# py-cute/pup_study_style/auth_routes.py
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from .ui_utils import create_base_document, add_question_mark_icon # Import UI utils
import dominate
from dominate.tags import * # Import dominate tags
import dominate.util as du # For raw text

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    doc = create_base_document("Register - PUP Study with Style") # Use the helper
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form.get('username', email)
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        db = get_db()

        if not name or not email or not password or not confirm_password:
            error = 'All fields are required.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone() is not None:
            error = f"Username {username} is already registered."
        elif db.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone() is not None:
            error = f"Email {email} is already registered."
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO users (name, email, username, password_hash) VALUES (?, ?, ?, ?)",
                    (name, email, username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError: # Should be caught by checks above, but good practice
                error = f"User {username} or email {email} is already registered (Integrity)."
            else:
                # Log in the new user automatically
                user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
                if user:
                    session.clear()
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    return redirect(url_for('main.home')) # Redirect to main blueprint's home
                else:
                    error = "Registration succeeded but failed to log in automatically."
        
        if error: # Flash error if it occurred
            flash(error) # Using flash for errors is better than passing 'error' variable directly

    # Dominate HTML generation
    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            h1("Mula sayo para", br(), "sa bayan", _class='page-title')
            if error: # Display flashed messages or direct error
                p(error, _class="error-message")

            with form(method='post'):
                div(label("Name:", fr="name"), input_(type="text", name="name", id="name", value=request.form.get('name', ''), required=True), _class="form-group")
                div(label("Email Address:", fr="email"), input_(type="email", name="email", id="email", value=request.form.get('email', ''), required=True), _class="form-group")
                div(label("Username:", fr="username"), input_(type="text", name="username", id="username", placeholder="Optional, uses email if blank", value=request.form.get('username','')), _class="form-group")
                div(label("Password:", fr="password"), input_(type="password", name="password", id="password", required=True), _class="form-group")
                div(label("Confirm Password:", fr="confirm_password"), input_(type="password", name="confirm_password", id="confirm_password", required=True), _class="form-group")
                
                button(img(src=url_for('static', filename='assets/register_button.png'), alt='Register', style="width:120px; height:auto;"), type='submit', _class="action-button", style="border:none; background:transparent; padding:0; cursor:pointer;")
                br()
                a(img(src=url_for('static', filename='assets/back_login_button.png'), alt='Back to Login'), href=url_for('auth.login'), _class="button-link")
        add_question_mark_icon(mobile_view_div)
    return doc.render()


@bp.route('/login', methods=('GET', 'POST'))
def login():
    # If user is already logged in, redirect to home
    if g.user: # Assuming you set g.user in a @bp.before_app_request
        return redirect(url_for('main.home'))

    doc = create_base_document("Login - PUP Study with Style")
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password_hash'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('main.home')) # Redirect to main blueprint's home
        
        flash(error)

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            h1("Welcome To PUP Study", br(), "with Style", _class='page-title')
            if error:
                p(error, _class="error-message")
            with form(method='post'):
                div(label("Username:", fr="username"), input_(type="text", name="username", id="username", required=True), _class="form-group")
                div(label("Password:", fr="password"), input_(type="password", name="password", id="password", required=True), _class="form-group")
                button(img(src=url_for('static', filename='assets/login_button.png'), alt='Log In', style="width:120px; height:auto;"), type='submit', _class="action-button", style="border:none; background:transparent; padding:0; cursor:pointer;")
                br()
                a(img(src=url_for('static', filename='assets/signup_button.png'), alt='Sign Up'), href=url_for('auth.register'), _class="button-link")
        add_question_mark_icon(mobile_view_div)
    return doc.render()

@bp.before_app_request # Loads logged in user data before each request if logged in
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM users WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index')) # Or 'auth.login' or 'main.home'