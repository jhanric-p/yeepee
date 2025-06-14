# py-cute/pup_study_style/main_routes.py
from flask import (
    Blueprint, flash, g, redirect, request, session, url_for
)
from .db import get_db
from .ui_utils import create_base_document, add_question_mark_icon
from werkzeug.exceptions import abort # For 404
import dominate
from dominate.tags import *
import dominate.util as du

bp = Blueprint('main', __name__) # No url_prefix if these are top-level like /home, /cart

# Decorator to require login for certain routes
import functools
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login')) # Redirect to auth blueprint's login
        return view(**kwargs)
    return wrapped_view

@bp.route('/') # This will be the effective '/' if linked in __init__.py
@bp.route('/home')
@login_required # Example of protecting a route
def home():
    # if 'user_id' not in session: # Replaced by @login_required and g.user
    #     return redirect(url_for('auth.login'))
        
    doc = create_base_document(f"Home - {g.user['username']}")
    db = get_db()
    product = db.execute('SELECT * FROM products ORDER BY stock_quantity DESC LIMIT 1').fetchone()

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            with div(_class="top-right-icons"):
                a(img(src=url_for('static', filename='assets/cart_icon.png'), alt='Cart'), href=url_for('main.shopping_cart_page'))
                a(img(src=url_for('static', filename='assets/profile_icon.png'), alt='Profile'), href=url_for('profile.profile_page')) # Assuming profile blueprint

            h2("Best Seller", _class='page-title')
            
            if product:
                with div(_class="product-card", style="text-align:center;"):
                    # Update image_url for PUP Baybayin Lace - Minimalist product to use jpg images
                    image_file = 'assets/Classic.jpg'  # default image
                    if product['name'] == 'PUP Baybayin Lace - Minimalist':
                        image_file = 'assets/Mono_Chrome.jpg'  # or 'assets/Coquette.jpg' based on variant if needed
                    div(img(src=url_for('static', filename=image_file), alt=product['name'], style="max-width:80%; height:auto; margin-bottom:10px; border: 1px solid #ccc;"), _class="product-image-container")
                    h3(product['name'], style="font-size: 1.2em; margin-bottom: 5px;")
                    div(
                        img(src=url_for('static', filename='assets/Jeepney_Signage.jpg'), alt="PUP Jeepney Signage", style="max-width: 100%; height: auto;"),
                        style="margin-top:10px;"
                    )
                    p(a("View Details", href=url_for('main.product_detail_page', product_id=product['id'])), style="margin-top:10px;")
            else:
                p("No best selling products available at the moment.")
            
            h2("All Products", style="margin-top:30px;")
            # Ensure product_id is defined even if product is None for the query
            best_seller_id = product['id'] if product else -1
            all_products = db.execute('SELECT * FROM products WHERE id != ? LIMIT 5', (best_seller_id,)).fetchall()
            if all_products:
                for p_item in all_products:
                    with div(_class="product-card"):
                        # Update image_url for PUP Baybayin Lace - Minimalist product to use jpg images
                        image_file = p_item['image_url']
                        if p_item['name'] == 'PUP Baybayin Lace - Minimalist':
                            image_file = 'assets/Classic.jpg'  # or 'assets/Mono_Chrome.jpg' or 'assets/Coquette.jpg' based on variant if needed
                        img(src=url_for('static', filename=image_file), alt=p_item['name'], _class="product-image")
                        with div(_class="product-info"):
                            h4(a(p_item['name'], href=url_for('main.product_detail_page', product_id=p_item['id'])))
                            p(f"₱{p_item['price']:.2f}")
                            p(du.text(p_item['description'][:50] + '...' if p_item['description'] else ''))
                            a(img(src=url_for('static', filename='assets/add_to_cart_button.png'), alt='Add to Cart'),
                              href=url_for('main.add_to_cart', product_id=p_item['id']), _class="button-link")
                            a("BUY NOW", href=url_for('main.buy_now', product_id=p_item['id']),
                              style="display:inline-block; background-color:#7b0015; color:white; padding:5px 10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-left:10px; font-size:0.9em;")
            else:
                p("No other products found.")
        add_question_mark_icon(mobile_view_div)
    return doc.render()

@bp.route('/product/<int:product_id>')
@login_required
def product_detail_page(product_id):
    doc = create_base_document("Product Details")
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()

    if product is None: # Use werkzeug.exceptions.abort for standard 404
        abort(404, f"Product id {product_id} doesn't exist.")

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            with div(_class="top-right-icons"):
                a(img(src=url_for('static', filename='assets/cart_icon.png'), alt='Cart'), href=url_for('main.shopping_cart_page'))
                a(img(src=url_for('static', filename='assets/profile_icon.png'), alt='Profile'), href=url_for('profile.profile_page'))

            img(src=url_for('static', filename=product['image_url']), alt=product['name'], style="max-width: 90%; height: auto; margin-bottom: 15px; border: 1px solid #ddd;")
            div("Variations: " + product['variations'] if product['variations'] else "No specific variations.", style="font-size:0.9em; color:#555; margin-bottom:10px;")

            h1(product['name'], style="font-size:1.5em; margin-bottom:10px;")
            p(f"₱{product['price']:.2f}", style="font-size:1.3em; color: #7b0015; font-weight:bold; margin-bottom:5px;")
            # Corrected to show actual stock:
            p(f"Stock: {product['stock_quantity']}", style="font-size:0.9em; color:#555; margin-bottom:15px;")

            p("Guaranteed to get by: 17-19 May (Example)", style="font-size:0.9em;")
            p("Free & Easy Return", style="font-size:0.9em;")
            p("Merchandise Protection", style="font-size:0.9em; margin-bottom:15px;")

            if product['variations']:
                with div(style="margin-bottom:15px;"):
                    label("Select variation:", style="display:block; margin-bottom:5px; font-weight:bold;")
                    for var in product['variations'].split(','):
                        button(var.strip(), style="padding: 5px 10px; margin-right: 5px; border:1px solid #ccc; background-color:white; cursor:pointer;")
            
            p("4.9 Product rating (100 reviews)", style="font-size:0.9em; color:#555; margin-bottom:20px;")

            div(
                a(img(src=url_for('static', filename='assets/add_to_cart_button.png'), alt='Add to Cart'), href=url_for('main.add_to_cart', product_id=product['id']), _class="button-link"),
                a("BUY NOW", href=url_for('main.buy_now', product_id=product['id']),
                  style="display:inline-block; background-color:#7b0015; color:white; padding:10px 20px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-left:10px;"),
                style="margin-top:10px;"
            )
            a("Go Back", href=request.referrer or url_for('main.home'), _class="back-button", style="display:block; text-align:center; background-color:#555; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:15px;")
        add_question_mark_icon(mobile_view_div)

    return doc.render()


@bp.route('/cart/add/<int:product_id>')
@login_required
def add_to_cart(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        flash(f"Product ID {product_id} not found.", "error")
        return redirect(request.referrer or url_for('main.home'))

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {'name': product['name'], 'price': product['price'], 'quantity': 1, 'image_url': product['image_url']}
    
    session['cart'] = cart
    flash(f"{product['name']} added to cart.", "success")
    return redirect(request.referrer or url_for('main.home'))

@bp.route('/buy-now/<int:product_id>')
@login_required
def buy_now(product_id):
    cart = session.get('cart', {})
    product_id_str = str(product_id)
    db = get_db()
    product = db.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    if not product:
        flash(f"Product ID {product_id} not found.", "error")
        return redirect(request.referrer or url_for('main.home'))

    # Clear cart and add only this product for immediate checkout
    cart = {}
    cart[product_id_str] = {'name': product['name'], 'price': product['price'], 'quantity': 1, 'image_url': product['image_url']}
    session['cart'] = cart
    flash(f"{product['name']} added to cart for immediate checkout.", "success")
    return redirect(url_for('main.checkout_page'))


@bp.route('/cart')
@login_required
def shopping_cart_page():
    doc = create_base_document("Shopping Cart")
    cart_items = session.get('cart', {})
    total_price = 0

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            h1("Shopping cart", _class='page-title')
            div(_class="header-image-container", style=f"background-image: url({url_for('static', filename='assets/pup_building_banner.png')});")
            p("StudywithStyle", style="font-weight:bold; text-align:left; margin-bottom:15px; border-bottom: 1px solid #eee; padding-bottom:5px;")

            if not cart_items:
                p("Your cart is empty.")
            else:
                for item_id, item_data in cart_items.items():
                    with div(_class="item-row"):
                        input_(type="checkbox", checked=True, style="margin-right:10px;") # Non-functional checkbox
                        img(src=url_for('static', filename=item_data['image_url']), alt=item_data['name'], _class="item-thumbnail")
                        with div(_class="item-details"):
                            p(item_data['name'], style="font-weight:bold;")
                            p(f"₱{item_data['price']:.2f} each", style="font-size:0.9em; color:#555;")
                        with div(_class="item-quantity"): # Placeholder quantity buttons
                            button("-", onclick=f"alert('Decrease qty for {item_id}')")
                            span(item_data['quantity'])
                            button("+", onclick=f"alert('Increase qty for {item_id}')")
                    item_total = item_data['price'] * item_data['quantity']
                    total_price += item_total
                
                hr(style="margin: 20px 0;")
                div(f"Total: ₱{total_price:.2f}", style="font-size:1.2em; font-weight:bold; text-align:right; margin-bottom:20px;")
                a(img(src=url_for('static', filename='assets/checkout_button.png'), alt='Check Out'), 
                  href=url_for('main.checkout_page'), _class="button-link", style="display:block; text-align:center;")
            a("Home", href=url_for('main.home'), style="display:block; text-align:center; background-color:#7b0015; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:15px;")
        add_question_mark_icon(mobile_view_div)
    return doc.render()

@bp.route('/checkout')
@login_required
def checkout_page():
    if not session.get('cart'):
        flash("Your cart is empty. Add items before checking out.", "warning")
        return redirect(url_for('main.shopping_cart_page'))

    doc = create_base_document("Checkout")
    cart_items = session.get('cart', {})
    subtotal = 0
    
    first_item_key = next(iter(cart_items)) if cart_items else None
    display_item = cart_items[first_item_key] if first_item_key else None

    for item_data in cart_items.values():
        subtotal += item_data['price'] * item_data['quantity']
    
    shipping_cost = 36.00 
    total_due = subtotal + shipping_cost

    with doc.add(div(_class='mobile-view')) as mobile_view_div:
        with mobile_view_div.add(div(_class='content-wrapper')):
            img(src=url_for('static', filename='assets/pup_logo.png'), alt='PUP Logo', _class='logo')
            h1("STUDY WITH", br(), "PASSION", _class='page-title')
            p("PUPStudyWithStyle", style="font-weight:bold; text-align:left; margin-bottom:10px;")

            if display_item:
                with div(_class="item-row", style="border-bottom:none; padding-bottom: 0;"):
                    img(src=url_for('static', filename=display_item['image_url']), alt=display_item['name'], _class="item-thumbnail", style="width:80px;")
                    with div(_class="item-details"):
                        p(display_item['name'], style="font-weight:bold;")
                        p("Coquette", style="font-size:0.9em; color:#777;") # Example variant
                        p(f"₱{display_item['price']:.2f}", style="font-weight:bold; color:#7b0015;")
            
            hr(style="margin: 15px 0;")
            div(p("Estimated delivery: May 8-9"), p(f"₱{shipping_cost:.2f}"), _class="checkout-summary-item")
            div(p("Standard shipping"), _class="checkout-summary-item", style="padding-top:0;")
            hr(style="margin: 15px 0;")
            p(f"{len(cart_items)} item{'s' if len(cart_items) > 1 else ''}, total P{total_due:.2f}", style="text-align:right; font-size:0.9em; color:#555; margin-bottom:15px;")
            h3("Order summary", style="text-align:left; font-size:1.1em; margin-bottom:10px;")
            div(p("Subtotal"), p(f"₱{subtotal:.2f}"), _class="checkout-summary-item")
            div(p("Shipping"), p(f"₱{shipping_cost:.2f}"), _class="checkout-summary-item")
            hr(style="border-top: 1px solid black; margin: 5px 0;")
            div(p("Total", style="font-weight:bold;"), p(f"₱{total_due:.2f}", style="font-weight:bold; color:#7b0015;"), _class="checkout-summary-item")
            hr(style="margin: 15px 0;")
            h3("Payment method", style="text-align:left; font-size:1.1em; margin-bottom:5px;")
            div(p("Cash on delivery"), span("✔", style="color:green; font-size:1.5em;"), _class="checkout-summary-item")
            a("CHECK OUT NOW!", href=url_for('main.process_order'),
              style="display:block; text-align:center; background-color:#7b0015; color:white; padding:12px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:20px; font-size:1.1em;")
            a("Go Back", href=url_for('main.home'), style="display:block; text-align:center; background-color:#555; color:white; padding:10px; text-decoration:none; border-radius:5px; font-family:'RocaOne'; margin-top:15px;")
        add_question_mark_icon(mobile_view_div)
    return doc.render()

@bp.route('/process-order')
@login_required
def process_order():
    # Basic order processing: clear cart, flash message
    # In a real app: save order to DB, update stock, send confirmation email, etc.
    session.pop('cart', None)
    flash("Order Placed Successfully! (This is a placeholder)", "success")
    return redirect(url_for('main.home'))