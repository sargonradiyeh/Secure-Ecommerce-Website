from flask import Flask, jsonify, request, make_response
import csv
from flask import jsonify, request
import csv
import magic
import os
from io import StringIO
import logging
from werkzeug.utils import secure_filename
from functools import wraps
import time
from datetime import datetime

# API to create a category
def create_category():
    from app import Category, db
    """Create a new category."""
    data = request.get_json()
    category_name = data.get('Category_Name')

    # Validate input
    if not category_name:
        return jsonify({'error': 'Category_Name is required'}), 400

    # Check for duplicate category
    existing_category = Category.query.filter_by(Category_Name=category_name).first()
    if existing_category:
        return jsonify({'error': 'Category already exists'}), 409

    # Create and save the new category
    new_category = Category(Category_Name=category_name)
    db.session.add(new_category)
    db.session.commit()

    return jsonify({'message': 'Category created successfully', 'Category_ID': new_category.Category_ID}), 201


# API to create a subcategory
def create_subcategory():
    from app import SubCategory, db
    """Create a new subcategory."""
    data = request.get_json()
    subcategory_name = data.get('SubCategory_Name')
    description = data.get('Description', '')  # Optional field

    # Validate input
    if not subcategory_name:
        return jsonify({'error': 'SubCategory_Name and Category_ID are required'}), 400

    # Check for duplicate subcategory within the same category
    existing_subcategory = SubCategory.query.filter_by(SubCategory_Name=subcategory_name).first()
    if existing_subcategory:
        return jsonify({'error': 'SubCategory already exists under this category'}), 409

    # Create and save the new subcategory
    new_subcategory = SubCategory(
        SubCategory_Name=subcategory_name,
        Description=description,
    )
    db.session.add(new_subcategory)
    db.session.commit()

    return jsonify({'message': 'SubCategory created successfully', 'SubCategory_ID': new_subcategory.SubCategory_ID}), 201


# Get all products:
def get_products():
    from app import Product, db
    """Retrieve all products."""
    products = Product.query.all()
    return jsonify([
        {
            'Product_ID': product.Product_ID,
            'Name': product.Name,
            'Price': product.Price,
            'Description': product.Description,
            'ImageURL': product.ImageURL,
            'Listed': product.Listed,
            'Discount_Percentage': product.Discount_Percentage,
            'Category_ID': product.Category_ID,
            'SubCategory_ID': product.SubCategory_ID
        } for product in products
    ]), 200
    
# Get a single product: 
def get_product(product_id):
    from app import Product, db
    """Retrieve a single product by ID."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404
    return jsonify({
        'Product_ID': product.Product_ID,
        'Name': product.Name,
        'Price': product.Price,
        'Description': product.Description,
        'ImageURL': product.ImageURL,
        'Listed': product.Listed,
        'Discount_Percentage': product.Discount_Percentage,
        'Category_ID': product.Category_ID,
        'SubCategory_ID': product.SubCategory_ID
    }), 200

# Add Product API:
def add_product():
    from app import Product, db, Category, SubCategory
    """Add a new product."""
    data = request.get_json()

    # Extract and validate input
    name = data.get('Name')
    price = data.get('Price')
    description = data.get('Description', '')
    image_url = data.get('ImageURL', '')
    listed = data.get('Listed', True)
    discount_percentage = data.get('Discount_Percentage', 0)
    category_id = data.get('Category_ID')
    subcategory_id = data.get('SubCategory_ID')

    if not name or price is None or category_id is None or subcategory_id is None:
        return jsonify({'error': 'Name, Price, Category_ID, and SubCategory_ID are required'}), 400

    if discount_percentage < 0 or discount_percentage > 100:
        return jsonify({'error': 'Discount_Percentage must be between 0 and 100'}), 400

    # Check for existing category and subcategory
    category = Category.query.get(category_id)
    subcategory = SubCategory.query.get(subcategory_id)

    if not category:
        return jsonify({
            'error': f'Category unavailable'
        }), 400

    if not subcategory:
        return jsonify({
            'error': f'SubCategory unavailable'
        }), 400
                
    # Create a new product
    new_product = Product(
        Name=name,
        Price=price,
        Description=description,
        ImageURL=image_url,
        Listed=listed,
        Discount_Percentage=discount_percentage,
        Category_ID=category_id,
        SubCategory_ID=subcategory_id
    )

    # Save to the database
    db.session.add(new_product)
    db.session.commit()

    return jsonify({'message': 'Product added successfully', 'Product_ID': new_product.Product_ID}), 201

# Update Product API:
def update_product(product_id):
    from app import Product, db, Category, SubCategory
    """Update an existing product."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()

    # Update fields if provided
    product.Name = data.get('Name', product.Name)
    product.Price = data.get('Price', product.Price)
    product.Description = data.get('Description', product.Description)
    product.ImageURL = data.get('ImageURL', product.ImageURL)
    product.Listed = data.get('Listed', product.Listed)
    product.Discount_Percentage = data.get('Discount_Percentage', product.Discount_Percentage)
    product.Category_ID = data.get('Category_ID', product.Category_ID)
    product.SubCategory_ID = data.get('SubCategory_ID', product.SubCategory_ID)

    # Validate discount percentage
    if product.Discount_Percentage < 0 or product.Discount_Percentage > 100:
        return jsonify({'error': 'Discount_Percentage must be between 0 and 100'}), 400

    # Check for existing category and subcategory
    category = Category.query.get(data.get('Category_ID', product.Category_ID))
    subcategory = SubCategory.query.get(data.get('SubCategory_ID', product.SubCategory_ID))

    if not category:
        return jsonify({
            'error': f'Category unavailable'
        }), 400

    if not subcategory:
        return jsonify({
            'error': f'SubCategory unavailable'
        }), 400
        
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'}), 200

#Delete API:
def delete_product(product_id):
    from app import Product, db
    """Delete a product."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'error': 'Product not found'}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'}), 200


# for csv files/Bulk update:
# Constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = ['text/csv', 'application/csv']
REQUIRED_HEADERS = ['Name', 'Price', 'Category_ID', 'SubCategory_ID']
UPLOAD_RATE_LIMIT = 60  # seconds
MAX_PRODUCTS_PER_UPLOAD = 1000

# Rate limiting decorator
def rate_limit(seconds):
    last_upload = {}
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            now = time.time()
            if 'last' in last_upload and now - last_upload['last'] < seconds:
                return jsonify({'error': 'Rate limit exceeded. Please wait before uploading again.'}), 429
            last_upload['last'] = now
            return f(*args, **kwargs)
        return wrapper
    return decorator

def validate_csv_structure(headers):
    """Validate CSV headers"""
    missing_headers = set(REQUIRED_HEADERS) - set(headers)
    if missing_headers:
        raise ValueError(f"Missing required headers: {missing_headers}")

def sanitize_input(value):
    """Basic input sanitization"""
    if isinstance(value, str):
        return value.strip()
    return value

@rate_limit(UPLOAD_RATE_LIMIT)
def upload_products():
    from app import db, Product, Category, SubCategory

    try:
        # File validation
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Secure filename
        filename = secure_filename(file.filename)
        if not filename.endswith('.csv'):
            return jsonify({'error': 'Invalid file type. Only CSV files are allowed'}), 400

        # Check file size
        file_content = file.read()
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({'error': 'File size exceeds maximum limit'}), 400

        # Verify MIME type
        mime_type = magic.from_buffer(file_content, mime=True)
        if mime_type not in ALLOWED_MIME_TYPES:
            return jsonify({'error': 'Invalid file type'}), 400

        # Process CSV file
        stream = StringIO(file_content.decode('utf-8', errors='strict'))
        csv_reader = csv.DictReader(stream)
        
        # Validate CSV structure
        validate_csv_structure(csv_reader.fieldnames)
        
        products_added = []
        for row_number, row in enumerate(csv_reader, 1):
            if row_number > MAX_PRODUCTS_PER_UPLOAD:
                return jsonify({'error': 'Maximum number of products exceeded'}), 400

            try:
                # Sanitize and validate required fields
                name = sanitize_input(row.get('Name'))
                price = sanitize_input(row.get('Price'))
                category_id = sanitize_input(row.get('Category_ID'))
                subcategory_id = sanitize_input(row.get('SubCategory_ID'))

                if not all([name, price, category_id, subcategory_id]):
                    logging.warning(f"Row {row_number}: Missing required fields")
                    continue

                # Type conversion with validation
                try:
                    price = float(price)
                    category_id = int(category_id)
                    subcategory_id = int(subcategory_id)
                except ValueError as e:
                    logging.warning(f"Row {row_number}: Invalid data types - {str(e)}")
                    continue

                if price <= 0:
                    logging.warning(f"Row {row_number}: Invalid price value")
                    continue

                # Optional fields with sanitization
                description = sanitize_input(row.get('Description', ''))
                image_url = sanitize_input(row.get('ImageURL', ''))
                listed = str(sanitize_input(row.get('Listed', 'True'))).lower() == 'true'
                discount_percentage = int(sanitize_input(row.get('Discount_Percentage', '0')))

                if not (0 <= discount_percentage <= 100):
                    logging.warning(f"Row {row_number}: Invalid discount percentage")
                    continue

                # Verify foreign key constraints
                category = db.session.query(Category).get(category_id)
                subcategory = db.session.query(SubCategory).get(subcategory_id)

                if not category or not subcategory:
                    logging.warning(f"Row {row_number}: Invalid category or subcategory ID")
                    continue

                # Create product with sanitized data
                product = Product(
                    Name=name,
                    Price=price,
                    Description=description,
                    ImageURL=image_url,
                    Listed=listed,
                    Discount_Percentage=discount_percentage,
                    Category_ID=category_id,
                    SubCategory_ID=subcategory_id
                )
                db.session.add(product)
                products_added.append(product)

            except Exception as row_error:
                logging.error(f"Error processing row {row_number}: {str(row_error)}")
                continue

        # Commit transaction if products were added
        if products_added:
            db.session.commit()
            logging.info(f"Successfully added {len(products_added)} products")
            return jsonify({'message': f'{len(products_added)} products added successfully'}), 201
        else:
            return jsonify({'error': 'No valid products found in the CSV file'}), 400

    except Exception as e:
        db.session.rollback()
        logging.error(f"Upload failed: {str(e)}")
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    finally:
        db.session.close()