from datetime import datetime
import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Order, Product, User, users, db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

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
    product = db.session.query(Product).filter(Product.id == id).first()
    
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        quantity = int(request.form['quantity'])
        new_order = Order(
            product_id=id,
            first_name=first_name,
            last_name=last_name,
            address=address,
            quantity=quantity
        )
        db.session.add(new_order)
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('home'))
    
    return render_template('product_view.html',product=product)

# Product Search Page
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
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
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        image = request.files['images']

        if not Config.allowed_file(image.filename):
            flash('Invalid file type', 'error')
            return redirect(url_for('product'))

        # Generate a unique filename using the current timestamp
        image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        
        # Create a new product with the filename
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
        return redirect(url_for('home_shop'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        image = request.files.get('images')

        # Check if a new image was uploaded
        if image and image.filename:
            # Delete the old image from the server
            if product.image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Check if the new image file is allowed
            if not Config.allowed_file(image.filename):
                flash('Invalid file type', 'error')
                return redirect(url_for('edit_product', id=id))

            # Save the new image to the server
            image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        else:
            # If no new image is uploaded, keep the old image filename
            image_filename = product.image

        # Update the product details
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
        return redirect(url_for('home_shop'))

    # Delete the product's image from the directory
    if product.image:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image))
        except Exception as e:
            flash(f"Error deleting image: {e}", 'error')

    # Delete the product from the database
    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product'))

# Orders Page (Protected)
@app.route('/admin/orders')
@login_required
def order():
    orders = db.session.query(Order, Product.title.label('product_title')) \
        .join(Product, Order.product_id == Product.id) \
        .all()
    
    # Create a list of dictionaries for easier access in templates
    order_list = [{'id': order.id,
                   'first_name': order.first_name,
                   'last_name': order.last_name,
                   'address': order.address,
                   'quantity': order.quantity,
                   'date_time': order.date_time,
                   'product': order.product_title,
                   'note': order.note} for order, order.product_title in orders]

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
        db.session.delete(order)  # Delete the order from the database
        db.session.commit()  # Commit the transaction
        flash('Order successfully deleted.', 'success')
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
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
    app.run()
