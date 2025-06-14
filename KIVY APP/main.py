import sqlite3
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except ImportError:
    import hashlib

    def generate_password_hash(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def check_password_hash(stored_hash, password):
        return stored_hash == hashlib.sha256(password.encode()).hexdigest()
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.lang import Builder
import os

from create_profiles_table import create_profiles_table

# Set window size for desktop testing
Window.size = (360, 640)

create_profiles_table()

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database.db')

class DatabaseManager:
    """Encapsulates database connection and queries."""
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_user(self, username):
        conn = self.get_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        return user

    def user_exists(self, username, email):
        conn = self.get_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        conn.close()
        return existing_user is not None

    def insert_user(self, name, email, username, password_hash):
        conn = self.get_connection()
        try:
            conn.execute(
                "INSERT INTO users (name, email, username, password_hash) VALUES (?, ?, ?, ?)",
                (name, email, username, password_hash)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return False
        conn.close()
        return True

    def fetch_best_seller(self):
        conn = self.get_connection()
        best_seller = conn.execute('SELECT * FROM products ORDER BY stock_quantity DESC LIMIT 1').fetchone()
        conn.close()
        return best_seller

    def fetch_other_products(self, exclude_id, limit=5):
        conn = self.get_connection()
        other_products = conn.execute('SELECT * FROM products WHERE id != ? LIMIT ?', (exclude_id, limit)).fetchall()
        conn.close()
        return other_products

    def fetch_product_by_id(self, product_id):
        conn = self.get_connection()
        product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
        conn.close()
        return product

    def fetch_profile(self, username):
        conn = self.get_connection()
        profile = conn.execute('SELECT name, address1, contact1, address2, contact2 FROM profiles WHERE username = ?', (username,)).fetchone()
        conn.close()
        return profile

    def update_profile(self, username, name, address1, contact1, address2, contact2):
        conn = self.get_connection()
        try:
            conn.execute('''
                INSERT INTO profiles (username, name, address1, contact1, address2, contact2)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(username) DO UPDATE SET
                    name=excluded.name,
                    address1=excluded.address1,
                    contact1=excluded.contact1,
                    address2=excluded.address2,
                    contact2=excluded.contact2
            ''', (username, name, address1, contact1, address2, contact2))
            conn.commit()
        except sqlite3.Error:
            conn.close()
            return False
        conn.close()
        return True

# -------------------------
# Authentication Screens
# -------------------------

class LoginScreen(Screen):
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    db_manager = DatabaseManager()

    def do_login(self):
        username = self.username.text.strip()
        password = self.password.text.strip()
        user = self.db_manager.fetch_user(username)
        if user and check_password_hash(user['password_hash'], password):
            app = App.get_running_app()
            app.current_user = username
            self.manager.current = "home"
        else:
            popup = Popup(title="Login Failed",
                          content=Label(text="Incorrect username or password."), 
                          size_hint=(0.8, 0.3))
            popup.open()

class RegisterScreen(Screen):
    name_input = ObjectProperty(None)
    email_input = ObjectProperty(None)
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    confirm_password_input = ObjectProperty(None)
    db_manager = DatabaseManager()

    def do_register(self):
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        confirm_password = self.confirm_password_input.text.strip()

        if not name or not email or not password or not confirm_password:
            self.show_popup("Error", "All fields are required.")
            return
        if password != confirm_password:
            self.show_popup("Error", "Passwords do not match.")
            return

        if self.db_manager.user_exists(username, email):
            self.show_popup("Error", "Username or email already registered.")
            return

        password_hash = generate_password_hash(password)
        if not self.db_manager.insert_user(name, email, username, password_hash):
            self.show_popup("Error", "Username or email already registered.")
            return

        self.show_popup("Success", "Registration successful. Please login.")
        self.manager.current = "login"

    def show_popup(self, title, message):
        popup = Popup(title=title,
                      content=Label(text=message),
                      size_hint=(0.8, 0.3))
        popup.open()

# -------------------------
# Main Application Screens
# -------------------------

class HomeScreen(Screen):
    db_manager = DatabaseManager()
    best_seller = None
    other_products = []

    def on_pre_enter(self):
        self.best_seller = self.db_manager.fetch_best_seller()
        best_seller_id = self.best_seller['id'] if self.best_seller else -1
        self.other_products = self.db_manager.fetch_other_products(best_seller_id)
        # Set best seller image and label dynamically
        if self.best_seller:
            best_seller_image = self.ids.get('best_seller_image')
            best_seller_label = self.ids.get('best_seller_label')
            if best_seller_image:
                best_seller_image.source = self.best_seller['image_path'] if 'image_path' in self.best_seller.keys() else '../pup_study_style/static/assets/question_mark.png'
            if best_seller_label:
                best_seller_label.text = self.best_seller['name']
        self.populate_products()

    def populate_products(self):
        product_list = self.ids.product_list
        product_list.clear_widgets()
        products = []
        if self.best_seller:
            products.append(self.best_seller)
        products.extend(self.other_products)
        for product in products:
            item = ProductItem(
                product_id=product['id'],
                product_name=product['name'],
                product_price=f"Price: ${product['price']:.2f}",
                image_source=product['image_path'] if 'image_path' in product.keys() else ''
            )
            product_list.add_widget(item)
        # Update height to minimum_height to ensure visibility
        product_list.height = product_list.minimum_height

class ProductItem(BoxLayout):
    product_id = NumericProperty()
    product_name = StringProperty()
    product_price = StringProperty()
    image_source = StringProperty()
    product_description = StringProperty()

    def on_view_details(self):
        app = App.get_running_app()
        app.show_product_detail(self.product_id)

    def on_add_to_cart(self):
        app = App.get_running_app()
        app.add_to_cart(self.product_id)
        popup = Popup(title="Added to Cart",
                      content=Label(text="Product added to cart."),
                      size_hint=(0.6, 0.3))
        popup.open()
        app.root.current = 'cart'

    def on_buy_now(self):
        app = App.get_running_app()
        app.add_to_cart(self.product_id)
        popup = Popup(title="Buy Now",
                      content=Label(text="Proceeding to checkout."),
                      size_hint=(0.6, 0.3))
        popup.open()
        app.root.current = 'checkout'

class ProductDetailScreen(Screen):
    product_id = NumericProperty()
    db_manager = DatabaseManager()

    def on_pre_enter(self):
        product = self.db_manager.fetch_product_by_id(self.product_id)
        if product:
            self.ids.detail_name.text = product['name']
            self.ids.detail_description.text = product['description'] if 'description' in product.keys() else ''
            self.ids.detail_image.source = product['image_path'] if 'image_path' in product.keys() else ''
            self.product_id = product['id']

    def add_to_cart(self):
        app = App.get_running_app()
        app.add_to_cart(self.product_id)
        popup = Popup(title="Added to Cart",
                      content=Label(text="Product added to cart."),
                      size_hint=(0.6, 0.3))
        popup.open()

class CartScreen(Screen):
    def on_pre_enter(self):
        self.populate_cart()

    def populate_cart(self):
        print("Populating cart screen")
        cart_list = self.ids.cart_list
        cart_list.clear_widgets()
        app = App.get_running_app()
        print(f"Cart items: {app.cart}")
        for item in app.cart:
            product = app.get_product_by_id(item['product_id'])
            if product:
                from kivy.uix.boxlayout import BoxLayout
                from kivy.uix.image import Image
                from kivy.uix.label import Label
                from kivy.uix.button import Button

                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='80dp', padding=5, spacing=10)
                product_image = Image(source=product['image_path'] if 'image_path' in product.keys() and product['image_path'] else '../pup_study_style/static/assets/question_mark.png',
                                      size_hint_x=None, width='80dp', allow_stretch=True, keep_ratio=True)
                product_label = Label(text=f"{product['name']} - Quantity: {item['quantity']}",
                                      valign='middle', halign='left', text_size=(self.width, None))
                item_layout.add_widget(product_image)
                item_layout.add_widget(product_label)

                # Add quantity editor buttons
                def decrease_quantity(instance):
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                    else:
                        app.cart.remove(item)
                    self.populate_cart()

                def increase_quantity(instance):
                    item['quantity'] += 1
                    self.populate_cart()

                btn_decrease = Button(text='-', size_hint_x=None, width='30dp')
                btn_decrease.bind(on_release=decrease_quantity)
                btn_increase = Button(text='+', size_hint_x=None, width='30dp')
                btn_increase.bind(on_release=increase_quantity)

                item_layout.add_widget(btn_decrease)
                item_layout.add_widget(btn_increase)

                cart_list.add_widget(item_layout)

class EditProfileScreen(Screen):
    username = StringProperty('')
    db_manager = DatabaseManager()

    def on_pre_enter(self):
        app = App.get_running_app()
        self.username = getattr(app, 'current_user', '')
        profile = self.db_manager.fetch_profile(self.username)
        if profile:
            self.ids.name_input.text = profile['name'] if profile['name'] else ''
            self.ids.address1_input.text = profile['address1'] if profile['address1'] else ''
            self.ids.contact1_input.text = profile['contact1'] if profile['contact1'] else ''
            self.ids.address2_input.text = profile['address2'] if profile['address2'] else ''
            self.ids.contact2_input.text = profile['contact2'] if profile['contact2'] else ''
        else:
            self.ids.name_input.text = ''
            self.ids.address1_input.text = ''
            self.ids.contact1_input.text = ''
            self.ids.address2_input.text = ''
            self.ids.contact2_input.text = ''

    def save_profile(self):
        name = self.ids.name_input.text.strip()
        address1 = self.ids.address1_input.text.strip()
        contact1 = self.ids.contact1_input.text.strip()
        address2 = self.ids.address2_input.text.strip()
        contact2 = self.ids.contact2_input.text.strip()

        success = self.db_manager.update_profile(self.username, name, address1, contact1, address2, contact2)
        if success:
            content = "Profile updated successfully."
        else:
            content = "Failed to update profile."

        popup = Popup(title="Profile Update",
                      content=Label(text=content),
                      size_hint=(0.8, 0.5))
        popup.open()
        if success:
            self.manager.current = 'profile'

class ProfileScreen(Screen):
    username = StringProperty('')  # Store current username
    db_manager = DatabaseManager()

    def on_pre_enter(self):
        app = App.get_running_app()
        self.username = getattr(app, 'current_user', '')  # Assuming app stores current logged-in username
        profile = self.db_manager.fetch_profile(self.username)
        if profile:
            try:
                # Access ids safely with get method
                self.ids.get('name_label', Label()).text = profile['name'] if profile['name'] else ''
                self.ids.get('address1_label', Label()).text = profile['address1'] if profile['address1'] else ''
                self.ids.get('contact1_label', Label()).text = profile['contact1'] if profile['contact1'] else ''
                self.ids.get('address2_label', Label()).text = profile['address2'] if profile['address2'] else ''
                self.ids.get('contact2_label', Label()).text = profile['contact2'] if profile['contact2'] else ''
            except Exception as e:
                print(f"Error setting profile labels: {e}")
        else:
            # Clear fields if no profile found
            self.ids.get('name_label', Label()).text = ''
            self.ids.get('address1_label', Label()).text = ''
            self.ids.get('contact1_label', Label()).text = ''
            self.ids.get('address2_label', Label()).text = ''
            self.ids.get('contact2_label', Label()).text = ''

    def save_profile(self):
        name = self.ids.name_label.text.strip()
        address1 = self.ids.address1_label.text.strip()
        contact1 = self.ids.contact1_label.text.strip()
        address2 = self.ids.address2_label.text.strip()
        contact2 = self.ids.contact2_label.text.strip()

        success = self.db_manager.update_profile(self.username, name, address1, contact1, address2, contact2)
        if success:
            content = "Profile saved successfully."
        else:
            content = "Failed to save profile."

        popup = Popup(title="Profile Save Status",
                      content=Label(text=content),
                      size_hint=(0.8, 0.5))
        popup.open()

    def logout(self):
        app = App.get_running_app()
        app.current_user = None
        self.manager.current = 'login'

class OrderHistoryScreen(Screen):
    db_manager = DatabaseManager()

    def on_pre_enter(self):
        self.load_order_history()

    def load_order_history(self):
        order_list = self.ids.order_history_list
        order_list.clear_widgets()
        app = App.get_running_app()
        username = getattr(app, 'current_user', None)
        if not username:
            return
        # Fetch order history from DB - placeholder query
        conn = self.db_manager.get_connection()
        orders = conn.execute('SELECT ref_no, status, quantity, payment FROM orders WHERE username = ?', (username,)).fetchall()
        conn.close()
        for order in orders:
            order_list.add_widget(Label(text=str(order['ref_no'])))
            order_list.add_widget(Label(text=order['status']))
            order_list.add_widget(Label(text=str(order['quantity'])))
            order_list.add_widget(Label(text=order['payment']))

class ContactUsScreen(Screen):
    def submit_contact(self):
        name = self.ids.name_input.text.strip()
        email = self.ids.email_input.text.strip()
        message = self.ids.message_input.text.strip()
        if not name or not email or not message:
            popup = Popup(title="Error", content=Label(text="All fields are required."), size_hint=(0.8, 0.3))
            popup.open()
            return
        # Here you would handle sending the message, e.g., save to DB or send email
        popup = Popup(title="Success", content=Label(text="Message sent successfully."), size_hint=(0.8, 0.3))
        popup.open()
        # Clear fields after submission
        self.ids.name_input.text = ''
        self.ids.email_input.text = ''
        self.ids.message_input.text = ''

class InventoryManagementScreen(Screen):
    db_manager = DatabaseManager()

    def add_item(self):
        item_id = self.ids.item_id_input.text.strip()
        name = self.ids.item_name_input.text.strip()
        quantity = self.ids.quantity_input.text.strip()
        price = self.ids.price_input.text.strip()
        if not item_id or not name or not quantity or not price:
            popup = Popup(title="Error", content=Label(text="All fields are required."), size_hint=(0.8, 0.3))
            popup.open()
            return
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            popup = Popup(title="Error", content=Label(text="Quantity must be integer and price must be number."), size_hint=(0.8, 0.3))
            popup.open()
            return
        conn = self.db_manager.get_connection()
        try:
            conn.execute('INSERT INTO inventory (item_id, name, quantity, price) VALUES (?, ?, ?, ?)', (item_id, name, quantity, price))
            conn.commit()
            popup = Popup(title="Success", content=Label(text="Item added successfully."), size_hint=(0.8, 0.3))
            popup.open()
        except sqlite3.IntegrityError:
            popup = Popup(title="Error", content=Label(text="Item ID already exists."), size_hint=(0.8, 0.3))
            popup.open()
        finally:
            conn.close()

    def view_items(self):
        inventory_list = self.ids.inventory_list
        inventory_list.clear_widgets()
        conn = self.db_manager.get_connection()
        items = conn.execute('SELECT item_id, name, quantity, price FROM inventory').fetchall()
        conn.close()
        for item in items:
            inventory_list.add_widget(Label(text=str(item['item_id'])))
            inventory_list.add_widget(Label(text=item['name']))
            inventory_list.add_widget(Label(text=str(item['quantity'])))
            inventory_list.add_widget(Label(text=f"{item['price']:.2f}"))

    def update_item(self):
        item_id = self.ids.item_id_input.text.strip()
        name = self.ids.item_name_input.text.strip()
        quantity = self.ids.quantity_input.text.strip()
        price = self.ids.price_input.text.strip()
        if not item_id or not name or not quantity or not price:
            popup = Popup(title="Error", content=Label(text="All fields are required."), size_hint=(0.8, 0.3))
            popup.open()
            return
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            popup = Popup(title="Error", content=Label(text="Quantity must be integer and price must be number."), size_hint=(0.8, 0.3))
            popup.open()
            return
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE inventory SET name = ?, quantity = ?, price = ? WHERE item_id = ?', (name, quantity, price, item_id))
        if cursor.rowcount == 0:
            popup = Popup(title="Error", content=Label(text="Item ID not found."), size_hint=(0.8, 0.3))
            popup.open()
        else:
            conn.commit()
            popup = Popup(title="Success", content=Label(text="Item updated successfully."), size_hint=(0.8, 0.3))
            popup.open()
        conn.close()

    def delete_item(self):
        item_id = self.ids.item_id_input.text.strip()
        if not item_id:
            popup = Popup(title="Error", content=Label(text="Item ID is required."), size_hint=(0.8, 0.3))
            popup.open()
            return
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventory WHERE item_id = ?', (item_id,))
        if cursor.rowcount == 0:
            popup = Popup(title="Error", content=Label(text="Item ID not found."), size_hint=(0.8, 0.3))
            popup.open()
        else:
            conn.commit()
            popup = Popup(title="Success", content=Label(text="Item deleted successfully."), size_hint=(0.8, 0.3))
            popup.open()
        conn.close()

class CheckoutScreen(Screen):
    def on_pre_enter(self):
        self.update_order_summary()

    def update_order_summary(self):
        app = App.get_running_app()
        cart = app.cart
        if not cart:
            self.ids.order_summary.text = "Your cart is empty."
            return

        total_price = 0
        summary_lines = []
        for item in cart:
            product = app.get_product_by_id(item['product_id'])
            if product:
                line = f"{product['name']} x {item['quantity']} = ₱{product['price'] * item['quantity']:.2f}"
                summary_lines.append(line)
                total_price += product['price'] * item['quantity']

        summary_text = "\n".join(summary_lines)
        summary_text += f"\n\nTotal: ₱{total_price:.2f}"
        self.ids.order_summary.text = summary_text

class CartScreen(Screen):
    def on_pre_enter(self):
        self.populate_cart()

    def populate_cart(self):
        cart_list = self.ids.cart_list
        cart_list.clear_widgets()
        app = App.get_running_app()
        for item in app.cart:
            product = app.get_product_by_id(item['product_id'])
            if product:
                from kivy.uix.boxlayout import BoxLayout
                from kivy.uix.image import Image
                from kivy.uix.label import Label
                from kivy.uix.button import Button

                item_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='80dp', padding=5, spacing=10)
                product_image = Image(source=product['image_path'] if 'image_path' in product.keys() and product['image_path'] else '../pup_study_style/static/assets/question_mark.png',
                                      size_hint_x=None, width='80dp', allow_stretch=True, keep_ratio=True)
                product_label = Label(text=f"{product['name']} - Quantity: {item['quantity']}",
                                      valign='middle', halign='left', text_size=(self.width, None))
                item_layout.add_widget(product_image)
                item_layout.add_widget(product_label)

                # Add quantity editor buttons
                def decrease_quantity(instance):
                    if item['quantity'] > 1:
                        item['quantity'] -= 1
                    else:
                        app.cart.remove(item)
                    self.populate_cart()

                def increase_quantity(instance):
                    item['quantity'] += 1
                    self.populate_cart()

                btn_decrease = Button(text='-', size_hint_x=None, width='30dp')
                btn_decrease.bind(on_release=decrease_quantity)
                btn_increase = Button(text='+', size_hint_x=None, width='30dp')
                btn_increase.bind(on_release=increase_quantity)

                item_layout.add_widget(btn_decrease)
                item_layout.add_widget(btn_increase)

                cart_list.add_widget(item_layout)

class StudyWithStyleApp(App):
    cart = []

    def build(self):
        Builder.load_file("main.kv")
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(ProductDetailScreen(name="product_detail"))
        sm.add_widget(CartScreen(name="cart"))
        sm.add_widget(CheckoutScreen(name="checkout"))
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(EditProfileScreen(name="edit_profile"))
        sm.add_widget(OrderHistoryScreen(name="order_history"))
        sm.add_widget(ContactUsScreen(name="contact_us"))
        sm.add_widget(InventoryManagementScreen(name="inventory_management"))
        return sm

    def show_product_detail(self, product_id):
        product_detail_screen = self.root.get_screen('product_detail')
        product_detail_screen.product_id = product_id
        self.root.current = 'product_detail'

    def add_to_cart(self, product_id):
        print(f"Adding product {product_id} to cart")
        for item in self.cart:
            if item['product_id'] == product_id:
                item['quantity'] += 1
                print(f"Incremented quantity for product {product_id} to {item['quantity']}")
                break
        else:
            self.cart.append({'product_id': product_id, 'quantity': 1})
            print(f"Appended product {product_id} to cart with quantity 1")

    def get_product_by_id(self, product_id):
        db_manager = DatabaseManager()
        return db_manager.fetch_product_by_id(product_id)

    def on_start(self):
        # Clear cart on start
        self.cart = []

    def on_stop(self):
        # Save cart or cleanup if needed
        pass

    def on_profile_button(self):
        self.root.current = 'profile'

if __name__ == "__main__":
    StudyWithStyleApp().run()