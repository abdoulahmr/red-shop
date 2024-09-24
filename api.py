from datetime import datetime
from flask import Blueprint, jsonify, send_from_directory, Flask, request
from models import Order, Product, db
from config import Config
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
api_bp = Blueprint('api', __name__)
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# API route to get all products
@api_bp.route('/api/products', methods=['GET'])
def api_products():
    products = Product.query.all()
    products_list = [product.to_dict() for product in products]

    return jsonify(products_list)

# API route to send images
@api_bp.route('/api/images/<filename>', methods=['GET'])
def api_images(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
# API route to add products
@api_bp.route('/api/add-product', methods=['POST'])
def api_add_product():
    data = request.form
    image = request.files.get('image')
    
    required_fields = ['title', 'description', 'price', 'quantity']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data fields'}), 400
    
    if not image:
        return jsonify({'error': 'Image file is required'}), 400

    if not Config.allowed_file(image.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    new_product = Product(
        title=data['title'],
        description=data['description'],
        price=data['price'],
        image=image_filename,
        quantity=data['quantity']
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully!'})

# API route to delete product
@api_bp.route('/api/delete-product/<int:id>', methods=['DELETE'])
def api_delete_product(id):
    product = Product.query.get(id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404
    
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': 'Product deleted successfully!'})

# API route to edit product
@api_bp.route('/api/edit-product/<int:id>', methods=['PUT'])
def api_edit_product(id):
    product = Product.query.get(id)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.form
    image = request.files.get('image')

    if 'title' in data:
        product.title = data['title']
    if 'description' in data:
        product.description = data['description']
    if 'price' in data:
        product.price = data['price']
    if 'quantity' in data:
        product.quantity = data['quantity']
    if image:
        if not Config.allowed_file(image.filename):
            return jsonify({'error': 'Invalid file type'}), 400

        image_filename = datetime.now().strftime('%Y%m%d%H%M%S') + "_" + secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
        product.image = image_filename

    db.session.commit()

    return jsonify({'message': 'Product updated successfully!'})

# API route to get all orders
@api_bp.route('/api/orders', methods=['GET'])
def api_orders():
    orders = Order.query.all()
    orders_list = [order.to_dict() for order in orders]

    return jsonify(orders_list)

# API route to add orders
@api_bp.route('/api/add-order', methods=['POST'])
def api_order():
    data = request.form

    required_fields = ['product_id', 'first_name', 'last_name', 'address', 'quantity', 'phone_number']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing data fields'}), 400

    new_order = Order(
        product_id=data['product_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        address=data['address'],
        quantity=data['quantity'],
        phone_number=data['phone_number']
    )
    db.session.add(new_order)
    db.session.commit()

    return jsonify({'message': 'Order placed successfully!'})

# API route to delete order
@api_bp.route('/api/delete-order/<int:id>', methods=['DELETE'])
def api_delete_order(id):
    order = Order.query.get(id)

    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    db.session.delete(order)
    db.session.commit()

    return jsonify({'message': 'Order deleted successfully!'})

# API route to edit order status
@api_bp.route('/api/edit-order/<int:id>', methods=['PUT'])
def api_edit_order(id):
    order = Order.query.get(id)

    if not order:
        return jsonify({'error': 'Order not found'}), 404

    data = request.form

    if 'status' in data:
        order.status = data['status']
    if 'note' in data:
        order.note = data['note']

    db.session.commit()

    return jsonify({'message': 'Order updated successfully!'})
