from flask import Blueprint, request, url_for
from .ui_utils import create_base_document, add_question_mark_icon
from .db import get_db  # Add this import, adjust '.db' if get_db is in a different module
import dominate
from dominate.tags import *

bp = Blueprint('contact', __name__, url_prefix='/contact')

@bp.route('/', methods=['GET', 'POST']) # Becomes /contact/
def contact_us_page():
    doc = create_base_document("Contact Us")
    message_sent = False
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message_text = request.form.get('message', '').strip()

        if not name or not email or not message_text:
            error = "All fields are required."
        else:
            db = get_db()
            try:
                db.execute(
                    "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
                    (name, email, message_text)
                )
                db.commit()
                message_sent = True
            except Exception as e:
                error = f"An error occurred while sending your message: {str(e)}"

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            img(src=url_for('static', filename='assets/Jeepney_Signage.jpg'), alt='Jeepney Signage', _class='logo')
            with div(_class="top-right-icons"):
                a(img(src=url_for('static', filename='assets/cart_icon.png'), alt='Cart'), href=url_for('main.shopping_cart_page'))
                a(img(src=url_for('static', filename='assets/profile_icon.png'), alt='Profile'), href=url_for('profile.profile_page'))
            h1("Contact Us", _class='page-title')
            if message_sent:
                p("Thank you for your message! We'll get back to you soon.", style="color:green; font-weight:bold;")
            if error:
                p(error, style="color:red; font-weight:bold;")
            with form(method='post', style="border:1px solid #ccc; padding:20px; border-radius:8px; background-color:white;"):
                div(label("Name:", fr="contact_name"), input_(type="text", name="name", id="contact_name", required=True, value=name), _class="form-group")
                div(label("Email Address:", fr="contact_email"), input_(type="email", name="email", id="email", required=True, value=email), _class="form-group")
                div(label("Message:", fr="contact_message"), textarea(name="message", id="contact_message", rows="5", required=True), _class="form-group", value=message_text)
                button(img(src=url_for('static', filename='assets/submit_button.png'), alt='Submit'), type='submit', style="border:none; background:transparent; padding:0; cursor:pointer; display:block; margin:10px auto 0 auto;")
            a("Home", href=url_for('main.home'), style="display:block; text-align:center; background-color:#7b0015; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:15px;")
        add_question_mark_icon(mobile_view_div)
    return doc.render()
