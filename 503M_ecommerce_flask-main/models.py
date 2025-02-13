from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import DB_CONFIG
from sqlalchemy import event
from urllib.parse import urlparse
import re

db = SQLAlchemy()

# Inventory Management Tables
class Warehouse(db.Model):
    __tablename__ = 'warehouse'
    Warehouse_ID = db.Column(db.Integer, primary_key=True)
    Manager_ID = db.Column(db.Integer, nullable=False)
    Location = db.Column(db.String(200), nullable=False)
    
    # Relationship to Inventory
    inventories = db.relationship('Inventory', back_populates='warehouse')

class Category(db.Model):
    __tablename__ = 'category'
    Category_ID = db.Column(db.Integer, primary_key=True)
    Category_Name = db.Column(db.String(100), nullable=False)

    # Relationship to Product
    products = db.relationship('Product', back_populates='category')
    
class SubCategory(db.Model):
    __tablename__ = 'subcategory'
    SubCategory_ID = db.Column(db.Integer, primary_key=True)
    SubCategory_Name = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(255))
    
    # Back-populates relationship
    products = db.relationship('Product', back_populates='subcategory')

class Product(db.Model):
    __tablename__ = 'product'
    Product_ID = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Price = db.Column(db.Float, nullable=False)
    Description = db.Column(db.String(255))
    ImageURL = db.Column(db.String(255))
    Listed = db.Column(db.Boolean, default=True)
    Discount_Percentage = db.Column(db.Integer, default=0)
    
    # Foreign keys to Category and SubCategory
    Category_ID = db.Column(db.Integer, db.ForeignKey('category.Category_ID'), nullable=False)
    SubCategory_ID = db.Column(db.Integer, db.ForeignKey('subcategory.SubCategory_ID'), nullable=False)
    
    # Back-populates relationships
    category = db.relationship('Category', back_populates='products')
    subcategory = db.relationship('SubCategory', back_populates='products')
    inventories = db.relationship('Inventory', back_populates='product')
    order_items = db.relationship('OrderItem', back_populates='product')
    
    @staticmethod
    def validate_image_url(url):
        if not url:
            return True  # Allow empty URLs
            
        try:
            # Parse URL
            parsed = urlparse(url)
            
            # Check URL scheme
            if parsed.scheme not in ['http', 'https']:
                raise ValueError("URL must use http or https protocol")
                
            # Check for valid hostname
            if not parsed.netloc:
                raise ValueError("Invalid URL format")
                
            # Check for common image extensions
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            if not any(url.lower().endswith(ext) for ext in valid_extensions):
                raise ValueError("URL must point to an image file")
                
            # Check for potentially malicious patterns
            dangerous_patterns = [
                'javascript:',
                'data:',
                '<script',
                'onclick=',
                'onerror='
            ]
            if any(pattern in url.lower() for pattern in dangerous_patterns):
                raise ValueError("URL contains potentially malicious content")
                
            return True
            
        except Exception as e:
            raise ValueError(f"Invalid image URL: {str(e)}")

# SQLAlchemy event listener to validate URL before insert/update
@event.listens_for(Product, 'before_insert')
@event.listens_for(Product, 'before_update')
def validate_url_before_save(mapper, connection, target):
    if target.ImageURL:
        target.validate_image_url(target.ImageURL)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    # Composite primary key columns (also foreign keys)
    Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID'), primary_key=True)
    Warehouse_ID = db.Column(db.Integer, db.ForeignKey('warehouse.Warehouse_ID'), primary_key=True)
    
    # Regular columns
    Stock_Level = db.Column(db.Integer, nullable=False)
    
    # Relationships
    product = db.relationship('Product', back_populates='inventories')
    warehouse = db.relationship('Warehouse', back_populates='inventories')



# Order Management Tables
class Order(db.Model):
    __tablename__ = 'order'
    Order_ID = db.Column(db.Integer, primary_key=True)
    Total_Amount = db.Column(db.Float, nullable=False)
    Order_Date = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(50), nullable=False)
    Total_Price = db.Column(db.Float, nullable=False)
    
    # Relationship to OrderItem and Return
    order_items = db.relationship('OrderItem', back_populates='order')

class OrderItem(db.Model):
    __tablename__ = 'order_item'
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Float, nullable=False)
    
    # Composite primary key with Order_ID and Product_ID
    Order_ID = db.Column(db.Integer, db.ForeignKey('order.Order_ID'), primary_key=True)
    Product_ID = db.Column(db.Integer, db.ForeignKey('product.Product_ID'), primary_key=True)
    
    # Back-populates relationships
    order = db.relationship('Order', back_populates='order_items')
    product = db.relationship('Product', back_populates='order_items')

class Return(db.Model):
    __tablename__ = 'return'
    Return_ID = db.Column(db.Integer, primary_key=True)
    Return_Date = db.Column(db.Date, nullable=False)
    Status = db.Column(db.String(50), nullable=False)
    Refund_Amount = db.Column(db.Float, nullable=False)
    

