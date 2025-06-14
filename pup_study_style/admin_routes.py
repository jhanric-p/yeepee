from flask import Blueprint, session, url_for, redirect, request
from .db import get_db
from .ui_utils import create_base_document # No question mark icon for admin
from .main_routes import login_required # Import login_required
import dominate
from dominate.tags import *
import functools # For custom admin_required decorator

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('username') != 'admin': # Simple admin check
            # flash("You are not authorized to access this page.", "danger")
            return redirect(url_for('main.home')) # Or auth.login
        return view(**kwargs)
    return wrapped_view

@bp.route('/inventory', methods=['GET', 'POST'])
@login_required # Ensure user is logged in first
@admin_required # Then check if admin
def inventory_management_page():
    doc = create_base_document("Inventory Management")
    db = get_db()
    error = None

    if request.method == 'POST':
        action = request.form.get('action')
        item_id = request.form.get('item_id', '').strip()
        item_name = request.form.get('item_name', '').strip()
        quantity = request.form.get('quantity', '').strip()
        price = request.form.get('price', '').strip()

        if action == 'add':
            if not item_name or not quantity or not price:
                error = "Item name, quantity, and price are required to add an item."
            else:
                try:
                    db.execute(
                        "INSERT INTO products (name, stock_quantity, price) VALUES (?, ?, ?)",
                        (item_name, int(quantity), float(price))
                    )
                    db.commit()
                except Exception as e:
                    error = f"Error adding item: {str(e)}"
        elif action == 'update':
            if not item_id or not item_name or not quantity or not price:
                error = "Item ID, name, quantity, and price are required to update an item."
            else:
                try:
                    db.execute(
                        "UPDATE products SET name = ?, stock_quantity = ?, price = ? WHERE id = ?",
                        (item_name, int(quantity), float(price), int(item_id))
                    )
                    db.commit()
                except Exception as e:
                    error = f"Error updating item: {str(e)}"
        elif action == 'delete':
            if not item_id:
                error = "Item ID is required to delete an item."
            else:
                try:
                    db.execute(
                        "DELETE FROM products WHERE id = ?",
                        (int(item_id),)
                    )
                    db.commit()
                except Exception as e:
                    error = f"Error deleting item: {str(e)}"

    products = db.execute('SELECT id, name, stock_quantity, price FROM products').fetchall()

    with doc.add(div(_class='mobile-view', style="max-width:600px;")):
        with div(_class='content-wrapper'):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            h1("INVENTORY MANAGEMENT", _class='page-title', style="background-color:#7b0015; color:white; padding:10px; border-radius:5px;")
            if error:
                p(error, style="color:red; font-weight:bold;")
            with form(method="post", action=url_for('admin.inventory_management_page'), style="margin-bottom:20px; padding:15px; border:1px solid #ccc; background-color:white; border-radius:5px;"):
                div(label("ITEM ID:", fr="item_id"), input_(type="text", name="item_id", id="item_id", value=request.form.get('item_id', ''), _class="form-group"))
                div(label("ITEM NAME:", fr="item_name"), input_(type="text", name="item_name", id="item_name", value=request.form.get('item_name', ''), _class="form-group"))
                div(label("QUANTITY:", fr="item_quantity"), input_(type="number", name="quantity", id="item_quantity", min="0", value=request.form.get('quantity', ''), _class="form-group"))
                div(label("PRICE:", fr="item_price"), input_(type="number", name="price", id="item_price", min="0", step="0.01", value=request.form.get('price', ''), _class="form-group"))
                div(
                    button("Add Item", type="submit", name="action", value="add", style="padding:8px 12px; background-color:green; color:white; border:none; border-radius:3px; cursor:pointer; margin-right:5px;"),
                    button("View", type="button", style="padding:8px 12px; background-color:blue; color:white; border:none; border-radius:3px; cursor:pointer; margin-right:5px;"),
                    button("Update", type="submit", name="action", value="update", style="padding:8px 12px; background-color:orange; color:white; border:none; border-radius:3px; cursor:pointer; margin-right:5px;"),
                    button("Delete", type="submit", name="action", value="delete", style="padding:8px 12px; background-color:red; color:white; border:none; border-radius:3px; cursor:pointer;"),
                    style="text-align:center; margin-top:10px;"
                )
            # Table for Inventory
            if not products:
                p("No products in inventory.")
            else:
                with table(style="width:100%; border-collapse:collapse; margin-top:20px; font-size:0.9em;"):
                    with tr(style="background-color:#333; color:white;"):
                        th("ID", style="padding:8px; border:1px solid #666; text-align:left;")
                        th("NAME", style="padding:8px; border:1px solid #666; text-align:left;")
                        th("QUANTITY", style="padding:8px; border:1px solid #666; text-align:center;")
                        th("PRICE", style="padding:8px; border:1px solid #666; text-align:right;")
                    for prod in products:
                        with tr():
                            td(prod['id'], style="padding:6px; border:1px solid #ccc;")
                            td(prod['name'], style="padding:6px; border:1px solid #ccc;")
                            td(prod['stock_quantity'], style="padding:6px; border:1px solid #ccc; text-align:center;")
                            td(f"₱{prod['price']:.2f}", style="padding:6px; border:1px solid #ccc; text-align:right;")
    return doc.render()
