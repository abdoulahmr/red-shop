from datetime import datetime
import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Order, Product, User, users, db
from config import Config
from api import api_bp

app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(api_bp)

# Ensure upload directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Home Page
@app.route('/')
def home():
    products = db.session.query(Product).all()
    return render_template('home.html', products=products)

# Product View Page
@app.route('/product:<int:id>', methods=['GET', 'POST'])
def product_view(id):
    # Fix: Check if product exists first
    product = db.session.query(Product).filter(Product.id == id).first()
    
    if not product:
        abort(404)
    
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            flash('Invalid quantity.', 'danger')
            return redirect(url_for('product_view', id=id))

        # Improvement: Check stock
        if quantity > product.quantity:
            flash(f'Sorry, only {product.quantity} items available in stock.', 'danger')
            return redirect(url_for('product_view', id=id))

        phone_number = request.form['phone']
        
        new_order = Order(
            product_id=id,
            first_name=first_name,
            last_name=last_name,
            address=address,
            quantity=quantity,
            phone_number=phone_number
        )
        
        # Optional: Decrease product stock here
        # product.quantity -= quantity 
        
        db.session.add(new_order)
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('product_view.html', product=product)

# Product Search Page
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('home'))
        
    products = db.session.query(Product).filter(Product.title.ilike(f'%{query}%')).all()
    return render_template('home.html', products=products, query=query)

# Admin Login Page
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

# Admin Dashboard Page (Protected)
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Add Product Page (Protected)
@app.route('/admin/product', methods=['GET', 'POST'])
@login_required
def product():
    products = db.session.query(Product).all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        try:
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
        except ValueError:
            flash('Invalid price or quantity format.', 'error')
            return redirect(url_for('product'))

        image = request.files.get('images')

        if image and image.filename:
            if not Config.allowed_file(image.filename):
                flash('Invalid file type', 'error')
                return redirect(url_for('product'))

            image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            flash('Product image is required.', 'error')
            return redirect(url_for('product'))
        
        new_product = Product(
            title=title,
            description=description,
            quantity=quantity,
            price=price,
            image=image_filename 
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('product'))

    return render_template('product.html', products=products)

# Edit Product Page (Protected)
@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    product = db.session.query(Product).filter(Product.id == id).first()

    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('home')) # Fix: Changed from home_shop to home

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        try:
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
        except ValueError:
             flash('Invalid input data.', 'error')
             return redirect(url_for('edit_product', id=id))

        image = request.files.get('images')

        if image and image.filename:
            if product.image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            if not Config.allowed_file(image.filename):
                flash('Invalid file type', 'error')
                return redirect(url_for('edit_product', id=id))

            image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            image_filename = product.image

        product.title = title
        product.description = description
        product.quantity = quantity
        product.price = price
        product.image = image_filename

        db.session.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product'))

    return render_template('edit_product.html', product=product)

# Delete Product (Protected)
@app.route('/admin/delete_product/<int:id>')
@login_required
def delete_product(id):
    product = Product.query.get(id)
    
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('home')) # Fix: Changed from home_shop to home

    if product.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
        except Exception as e:
            print(f"Error deleting image: {e}") # Log to console instead of flashing to avoid UI clutter

    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product'))

# Orders Page (Protected)
@app.route('/admin/orders')
@login_required
def order():
    # Fix: Correctly unpack the tuple (Order, product_title)
    orders = db.session.query(Order, Product.title.label('product_title')) \
        .join(Product, Order.product_id == Product.id) \
        .all()
    
    order_list = [
        {'id': order.id,
         'first_name': order.first_name,
         'last_name': order.last_name,
         'address': order.address,
         'quantity': order.quantity,
         'date_time': order.date_time,
         'product': product_title, # Fix: Use the unpacked variable
         'phone_number': order.phone_number,
         'status': order.status,
         'note': order.note
        } for order, product_title in orders
    ]

    return render_template('order.html', orders=order_list)

# Order Status Update (Protected)
@app.route('/admin/update_order/<int:id>', methods=['POST'])
@login_required
def update_order(id):
    order = db.session.query(Order).filter(Order.id == id).first()
    if not order:
        flash('Order not found', 'error')
        return redirect(url_for('order'))

    status = request.form['status']
    order.status = status
    db.session.commit()
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('order'))

# Order Delete (Protected)
@app.route('/admin/delete_order/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    order = Order.query.get_or_404(id)

    try:
        db.session.delete(order)
        db.session.commit()
        flash('Order successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting order: {e}', 'danger')

    return redirect(url_for('order'))

# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    db_path = db_uri.replace('sqlite:///', '')

    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Database not found at '{db_path}'. Creating tables...")
        with app.app_context():
            db.create_all()
            print("Database tables created successfully!")
    else:
        print("Database file exists. Skipping table creation.")
    app.run(debug=True)