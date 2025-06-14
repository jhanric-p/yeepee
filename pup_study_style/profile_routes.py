# py-cute/pup_study_style/profile_routes.py
from flask import Blueprint, flash, g, redirect, session, url_for, request
from .db import get_db
from .ui_utils import create_base_document, add_question_mark_icon
from .main_routes import login_required # Import login_required from main_routes
import dominate
from dominate.tags import *
import dominate.util as du

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/') # Becomes /profile/
@login_required
def profile_page():
    doc = create_base_document(f"Profile - {g.user['name']}")
    # user data is already in g.user from @login_required and before_app_request in auth

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper', style="text-align:left;")):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo', style="display:block; margin-left:auto; margin-right:auto;")
            div(img(src=url_for('static', filename='assets/profile_icon_large.png'), alt="Profile", style="width:100px; height:100px; border-radius:50%; margin:0 auto 20px auto; display:block; border: 2px solid #7b0015;"), _class="profile-header")
            h2(f"Hi, {g.user['name']}!", style="text-align:center; margin-bottom:20px;")
            
            div(h3("Address 1", style="font-size:1.1em; border-bottom:1px solid #ccc; padding-bottom:5px; margin-bottom:10px;"),
                p(strong("Address: "), du.text(g.user['address1_line1'] if g.user['address1_line1'] is not None else '123 Main St')),
                p(strong("Name: "), du.text(g.user['name'])),
                p(strong("Contact No.: "), du.text(g.user['contact_no1'] if g.user['contact_no1'] is not None else '09171234567')),
                style="margin-bottom:20px; background-color:white; padding:15px; border-radius:5px; box-shadow: 0 0 5px rgba(0,0,0,0.05);"
            )
            div(h3("Address 2", style="font-size:1.1em; border-bottom:1px solid #ccc; padding-bottom:5px; margin-bottom:10px;"),
                p(strong("Address: "), du.text(g.user['address2_line1'] if g.user['address2_line1'] is not None else 'N/A')),
                p(strong("Name: "), du.text(g.user['name'])),
                p(strong("Contact No.: "), du.text(g.user['contact_no2'] if g.user['contact_no2'] is not None else 'N/A')),
                style="margin-bottom:20px; background-color:white; padding:15px; border-radius:5px; box-shadow: 0 0 5px rgba(0,0,0,0.05);"
            )
            a("Home", href=url_for('main.home'), style="display:block; text-align:center; background-color:#7b0015; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:10px;")
            a("Edit Profile", href=url_for('profile.edit_profile'), style="display:block; text-align:center; background-color:#555; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:20px;")
            a("Log Out", href=url_for('auth.logout'), style="display:block; text-align:center; background-color:#7b0015; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:10px;")
        add_question_mark_icon(mobile_view_div)
    return doc.render()

@bp.route('/edit', methods=('GET', 'POST'))
@login_required
def edit_profile():
    doc = create_base_document(f"Edit Profile - {g.user['name']}")
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        address1_line1 = request.form.get('address1_line1', '').strip()
        contact_no1 = request.form.get('contact_no1', '').strip()
        address2_line1 = request.form.get('address2_line1', '').strip()
        contact_no2 = request.form.get('contact_no2', '').strip()

        if not name:
            error = "Name is required."

        if error is None:
            db = get_db()
            try:
                db.execute(
                    "UPDATE users SET name = ?, address1_line1 = ?, contact_no1 = ?, address2_line1 = ?, contact_no2 = ? WHERE id = ?",
                    (name, address1_line1, contact_no1, address2_line1, contact_no2, g.user['id'])
                )
                db.commit()
            except Exception as e:
                error = f"An error occurred while updating profile: {str(e)}"
            else:
                # Update g.user to reflect changes
                user = db.execute('SELECT * FROM users WHERE id = ?', (g.user['id'],)).fetchone()
                if user:
                    session['username'] = user['username']
                    # Update g.user for current request
                    g.user = user
                return redirect(url_for('profile.profile_page'))

        if error:
            flash(error)

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper', style="text-align:center; max-width: 400px; margin: 30px auto; padding: 20px; background-color: #fff; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1);")):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo', style="display:block; margin: 0 auto 20px auto; width: 100px; height: auto;")
            h1("Edit Profile", _class='page-title', style="text-align:left; margin-bottom: 20px; color: #7b0015; font-weight: bold;")
            with form(method='post'):
                div(label("Name:", fr="name", style="display:block; text-align:left; font-weight: bold; margin-bottom: 5px;"), input_(type="text", name="name", id="name", value=request.form.get('name', g.user['name']), required=True, style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 15px;"), _class="form-group")
                div(label("Address 1:", fr="address1_line1", style="display:block; text-align:left; font-weight: bold; margin-bottom: 5px;"), input_(type="text", name="address1_line1", id="address1_line1", value=request.form.get('address1_line1', g.user['address1_line1'] or ''), style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 15px;"), _class="form-group")
                div(label("Contact No. 1:", fr="contact_no1", style="display:block; text-align:left; font-weight: bold; margin-bottom: 5px;"), input_(type="text", name="contact_no1", id="contact_no1", value=request.form.get('contact_no1', g.user['contact_no1'] or ''), style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 15px;"), _class="form-group")
                div(label("Address 2:", fr="address2_line1", style="display:block; text-align:left; font-weight: bold; margin-bottom: 5px;"), input_(type="text", name="address2_line1", id="address2_line1", value=request.form.get('address2_line1', g.user['address2_line1'] or ''), style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 15px;"), _class="form-group")
                div(label("Contact No. 2:", fr="contact_no2", style="display:block; text-align:left; font-weight: bold; margin-bottom: 5px;"), input_(type="text", name="contact_no2", id="contact_no2", value=request.form.get('contact_no2', g.user['contact_no2'] or ''), style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 15px;"), _class="form-group")
                button("Save Changes", type="submit", _class="action-button", style="width: 100%; padding: 12px; background-color: #7b0015; color: white; border: none; border-radius: 5px; font-size: 1em; cursor: pointer;")
                a("Cancel", href=url_for('profile.profile_page'), _class="button-link", style="display: inline-block; margin-top: 10px; color: #7b0015; font-weight: bold;")
        add_question_mark_icon(mobile_view_div)
    return doc.render()


@bp.route('/order-history')
@login_required
def order_history_page():
    doc = create_base_document("Order History")
    # Placeholder order data; in a real app, fetch from DB based on g.user['id']
    orders = [
        {'ref_no': 'ORD12345', 'status': 'Delivered', 'quantity': 2, 'payment': '₱280.00'},
        {'ref_no': 'ORD67890', 'status': 'Shipped', 'quantity': 1, 'payment': '₱160.00'},
    ]
    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            h1("Order History", _class='page-title', style="border: 2px solid #7b0015; display:inline-block; padding: 5px 15px; border-radius: 20px;")
            if not orders:
                p("You have no past orders.")
            else:
                with table(style="width:100%; border-collapse:collapse; margin-top:20px;"):
                    with tr(style="background-color:#7b0015; color:white;"):
                        th("Ref No.", style="padding:8px; border:1px solid #ddd; text-align:left;")
                        th("Order status", style="padding:8px; border:1px solid #ddd; text-align:left;")
                        th("Quantity", style="padding:8px; border:1px solid #ddd; text-align:center;")
                        th("Payment", style="padding:8px; border:1px solid #ddd; text-align:right;")
                    for order_item in orders:
                        with tr():
                            td(order_item['ref_no'], style="padding:8px; border:1px solid #ddd;")
                            td(order_item['status'], style="padding:8px; border:1px solid #ddd;")
                            td(order_item['quantity'], style="padding:8px; border:1px solid #ddd; text-align:center;")
                            td(order_item['payment'], style="padding:8px; border:1px solid #ddd; text-align:right;")
        add_question_mark_icon(mobile_view_div)
    return doc.render()