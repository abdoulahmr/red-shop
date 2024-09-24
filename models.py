from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# Users dictionary
users = {'admin': {'password': 'admin'}}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

    # Class method to get a user by ID
    @classmethod
    def get(cls, user_id):
        if user_id in users:
            return cls(user_id)
        return None

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'quantity': self.quantity,
            'price': self.price,
            'image': self.image
        }

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(255), default='pending', nullable=False)
    note = db.Column(db.Text)
    phone_number = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', backref='orders')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'address': self.address,
            'quantity': self.quantity,
            'date_time': self.date_time,
            'status': self.status,
            'note': self.note,
            'phone_number': self.phone_number
        }