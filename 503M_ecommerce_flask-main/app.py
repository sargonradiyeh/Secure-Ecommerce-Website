from flask import Flask, jsonify, request, session, make_response, url_for
from flask_talisman import Talisman
from functools import wraps
from dotenv import load_dotenv
import jwt
from waitress import serve
import requests
import APIs.inventory
import APIs.orders
import APIs.product
import APIs.warehouse
from db_config import DB_CONFIG
from datetime import datetime, timedelta
from flask_cors import CORS
from models import db, Warehouse, Category, SubCategory, Product, Inventory, Order, OrderItem, Return
import os
import random
import secrets  
import string

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')  # Replace with a secure key
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
JWT_ALGORITHM = 'HS256'
RBAC_SERVICE_URL = 'https://localhost:5001'
CA_CERT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "ca.crt")

db.init_app(app)

def create_sample_data():
    # Check if sample data already exists
    if Category.query.first():
        return

    # Create sample categories
    playstation = Category(Category_Name='Playstation')
    xbox = Category(Category_Name='Xbox')
    nintendo = Category(Category_Name='Nintendo')
    gamecube = Category(Category_Name='GameCube')

    # Create sample subcategories
    console = SubCategory(SubCategory_Name='Console', Description='Gaming consoles')
    controller = SubCategory(SubCategory_Name='Controller', Description='Gaming controllers')
    video_game = SubCategory(SubCategory_Name='Video Game', Description='Games for consoles')

    # Add categories and subcategories to the session
    db.session.add_all([playstation, xbox, nintendo, gamecube, console, controller, video_game])
    db.session.commit()

    # Create sample products
    products = [
        Product(
            Name='Playstation 5 Console',
            Price=499.99,
            Description='Latest Sony Playstation 5 Console',
            ImageURL='https://m.media-amazon.com/images/I/41PYg1k+laL._SX342_SY445_.jpg',
            Category_ID=playstation.Category_ID,
            SubCategory_ID=console.SubCategory_ID
        ),
        Product(
            Name='Xbox Series X Console',
            Price=499.99,
            Description='Latest Microsoft Xbox Series X Console',
            ImageURL='https://m.media-amazon.com/images/I/51bcwM0qLaL._SL1500_.jpg',
            Category_ID=xbox.Category_ID,
            SubCategory_ID=console.SubCategory_ID
        ),
        Product(
            Name='Nintendo Switch Console',
            Price=299.99,
            Description='Nintendo Switch Console',
            ImageURL='https://m.media-amazon.com/images/I/71wpE+ZIehL._SL1500_.jpg',
            Category_ID=nintendo.Category_ID,
            SubCategory_ID=console.SubCategory_ID
        ),
        Product(
            Name='PS5 DualSense Controller',
            Price=69.99,
            Description='Sony PS5 DualSense Wireless Controller',
            ImageURL='https://m.media-amazon.com/images/I/31j0hxQyh2L._SX300_SY300_QL70_FMwebp_.jpg',
            Category_ID=playstation.Category_ID,
            SubCategory_ID=controller.SubCategory_ID
        ),
        Product(
            Name='Xbox Wireless Controller',
            Price=59.99,
            Description='Microsoft Xbox Wireless Controller',
            ImageURL='https://m.media-amazon.com/images/I/51vVALvvHvL._SL1500_.jpg',
            Category_ID=xbox.Category_ID,
            SubCategory_ID=controller.SubCategory_ID
        ),
        Product(
            Name='Nintendo Switch Pro Controller',
            Price=69.99,
            Description='Nintendo Switch Pro Controller',
            ImageURL='https://m.media-amazon.com/images/I/71F5nnoo8gL._SL1300_.jpg',
            Category_ID=nintendo.Category_ID,
            SubCategory_ID=controller.SubCategory_ID
        ),
        Product(
            Name='The Last of Us Part II',
            Price=39.99,
            Description='Action-adventure game for PlayStation',
            ImageURL='https://m.media-amazon.com/images/I/71p8G+YeA6L._SL1500_.jpg',
            Category_ID=playstation.Category_ID,
            SubCategory_ID=video_game.SubCategory_ID
        ),
        Product(
            Name='Halo Infinite',
            Price=59.99,
            Description='First-person shooter game for Xbox',
            ImageURL='https://m.media-amazon.com/images/I/81nWynmiDPL._SL1500_.jpg',
            Category_ID=xbox.Category_ID,
            SubCategory_ID=video_game.SubCategory_ID
        ),
        Product(
            Name='Super Smash Bros. Ultimate',
            Price=59.99,
            Description='Fighting game for Nintendo Switch',
            ImageURL='https://m.media-amazon.com/images/I/815hF0mZBdL._SL1500_.jpg',
            Category_ID=nintendo.Category_ID,
            SubCategory_ID=video_game.SubCategory_ID
        ),
        Product(
            Name='GameCube Controller',
            Price=29.99,
            Description='Classic GameCube controller',
            ImageURL='https://m.media-amazon.com/images/I/31neCVwAC+L.jpg',
            Category_ID=gamecube.Category_ID,
            SubCategory_ID=controller.SubCategory_ID
        ),
    ]

    # Add products to the session
    db.session.add_all(products)
    db.session.commit()
    
    # Create sample warehouses
    warehouse1 = Warehouse(
        Manager_ID=1,
        Location='Los Angeles, CA'
    )
    warehouse2 = Warehouse(
        Manager_ID=3,
        Location='New York, NY'
    )
    db.session.add_all([warehouse1, warehouse2])
    db.session.commit()

    # Create sample inventories
    inventory1 = Inventory(
        Product_ID=products[0].Product_ID,
        Warehouse_ID=warehouse1.Warehouse_ID,
        Stock_Level=50
    )
    db.session.add_all([inventory1])
    db.session.commit()

    # Create sample orders
    order1 = Order(
        Total_Amount=559.98,
        Order_Date=datetime(2024, 3, 15).date(),
        Status='Processing',
        Total_Price=559.98
    )
    order2 = Order(
        Total_Amount=299.99,
        Order_Date=datetime(2024, 2, 28).date(),
        Status='Shipped',
        Total_Price=299.99
    )
    db.session.add_all([order1, order2])
    db.session.commit()

    # Create sample order items
    order_item1 = OrderItem(
        Order_ID=order1.Order_ID,
        Product_ID=products[0].Product_ID,
        Quantity=1,
        Price=499.99
    )
    order_item2 = OrderItem(
        Order_ID=order1.Order_ID,
        Product_ID=products[3].Product_ID,
        Quantity=1,
        Price=59.99
    )
    order_item3 = OrderItem(
        Order_ID=order2.Order_ID,
        Product_ID=products[2].Product_ID,
        Quantity=1,
        Price=299.99
    )
    db.session.add_all([order_item1, order_item2, order_item3])
    db.session.commit()

    # Create sample returns
    return1 = Return(
        Return_Date=datetime(2024, 5, 10).date(),
        Status='Pending',
        Refund_Amount=59.99
    )
    return2 = Return(
        Return_Date=datetime(2024, 7, 19).date(),
        Status='Completed',
        Refund_Amount=299.99
    )
    db.session.add_all([return1, return2])
    db.session.commit()

# Initialize the database and create sample data
with app.app_context():
    # db.drop_all() to reset the dB
    db.create_all()
    create_sample_data()
    APIs.inventory.initialize_inventory()

def verify_csrf(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        csrf_token_session = session.get('_csrf_token', None)
        csrf_token_header = request.headers.get('X-CSRFToken', None)
        
        if not csrf_token_header or not csrf_token_session:
            return jsonify({
                'error': 'Missing CSRF token.',
                'csrf_token_header': csrf_token_header,
                'csrf_token_session': csrf_token_session
            }), 400

        if csrf_token_header != csrf_token_session:
            return jsonify({'error': 'Invalid CSRF token.'}), 400

        return f(*args, **kwargs)
    return decorated_function


def role_required(required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            authenticated, user_data = is_authenticated()
            if not authenticated:
                return jsonify({'error': 'Unauthorized'}), 401
            user_roles = user_data.get('roles', [])
            if not any(role in user_roles for role in required_roles):
                return jsonify({'error': 'Forbidden: Insufficient role'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(required_permissions):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            authenticated, user_data = is_authenticated()
            if not authenticated:
                return jsonify({'error': 'Unauthorized'}), 401
            user_permissions = user_data.get('permissions', [])
            if not any(perm in user_permissions for perm in required_permissions):
                return jsonify({'error': 'Forbidden: Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def send_log_to_rbac(user_id, endpoint, method):
    data = {
        'user_id': user_id,
        'endpoint': endpoint,
        'method': method,
        'timestamp': datetime.utcnow().timestamp(),
    }
    try:
        response = requests.post(f'{RBAC_SERVICE_URL}/api/log_activity', json=data, verify=CA_CERT_PATH)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        pass

@app.before_request
def before_request():
    if request.endpoint and not request.endpoint.startswith(('static', 'favicon')):
        user_id = session.get('user_id')
        if not user_id and 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            token = auth_header.split()[1] if 'Bearer' in auth_header else auth_header
            try:
                decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[JWT_ALGORITHM])
                user_id = decoded.get('user_id')
            except jwt.InvalidTokenError:
                pass
        endpoint = request.path
        method = request.method
        send_log_to_rbac(user_id, endpoint, method)

# Set up the path to your certificates
cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "flask.crt")
key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "flask.key")
# print(cert_path, key_path)
# Enforce HTTPS with Flask-Talisman for security headers
Talisman(app, content_security_policy={
    'default-src': ["'self'"],
    'img-src': ["'self'", "data:"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'script-src': ["'self'"]
})

# Enable CORS for React frontend (assuming it's running on https://localhost:3000)
CORS(app, origins=["https://localhost:3000"], supports_credentials=True)

def is_authenticated():
    token = request.cookies.get('token')
    if not token:
        # Check the Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
        else:
            print("No token found in cookies or Authorization header.")
            return False, None

    try:
        response = requests.post(
            f'{RBAC_SERVICE_URL}/api/verify-token',
            json={'token': token},
            verify=CA_CERT_PATH
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Authentication successful for user_id: {data.get('user_id')}")
            return True, data  # Includes 'user_id', 'roles', 'permissions'
        else:
            print(f"Authentication failed with status {response.status_code}: {response.json()}")
            return False, None
    except requests.exceptions.RequestException as e:
        print(f"Error verifying token with RBAC service: {e}")
        return False, None

def generate_admin_url():
    return '/admin-' + ''.join(random.choices(string.ascii_letters + string.digits, k=12))

admin_url = generate_admin_url()
# print(f"Admin URL: {admin_url}")  # For server logs only

@app.route('/api/get-csrf-token', methods=['GET'])
def get_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_urlsafe(32)
    csrf_token = session['_csrf_token']
    response = jsonify({'csrf_token': csrf_token})
    # Set the CSRF token in a secure cookie
    response.set_cookie('csrf_token', csrf_token, httponly=False, secure=True, samesite='Lax')
    return response

@app.route('/api/login', methods=['POST'])
def login():
    try:
        # Forward the login request to the RBAC service
        response = requests.post(
            f'{RBAC_SERVICE_URL}/api/login',
            json=request.get_json(),
            headers={
                'Content-Type': 'application/json',
                'X-CSRFToken': request.headers.get('X-CSRFToken')
            },
            cookies=request.cookies,
            verify=CA_CERT_PATH
        )

        # Create a response object to return to the client
        resp = make_response(response.content, response.status_code)

        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            roles = data.get('roles', [])
            permissions = data.get('permissions', [])

            if token:
                # Set the token cookie for the main application
                resp.set_cookie(
                    'token',
                    token,
                    httponly=True,
                    secure=True,
                    samesite='Strict'  # Changed from 'Strict' to 'None'
                )

        return resp
    except requests.exceptions.RequestException as e:
        print(f"Error contacting RBAC service: {e}")
        return jsonify({'error': 'Authentication service unavailable'}), 503

@app.route('/api/setup-2fa', methods=['POST'])
def proxy_setup_two_factor():
    data = request.get_json()
    response = requests.post(f'{RBAC_SERVICE_URL}/api/setup-2fa', json=data, verify=CA_CERT_PATH)
    return (response.content, response.status_code, response.headers.items())

@app.route('/api/verify-2fa', methods=['POST'])
def proxy_verify_two_factor():
    data = request.get_json()
    response = requests.post(f'{RBAC_SERVICE_URL}/api/verify-2fa', json=data, verify=CA_CERT_PATH)
    return (response.content, response.status_code, response.headers.items())

@app.route('/api/request-password-reset', methods=['POST'])
def proxy_request_password_reset():
    data = request.get_json()
    response = requests.post(f'{RBAC_SERVICE_URL}/api/request-password-reset', json=data, verify=CA_CERT_PATH)
    return (response.content, response.status_code, response.headers.items())

@app.route('/api/reset-password/<token>', methods=['POST'])
def proxy_reset_password(token):
    data = request.get_json()
    response = requests.post(f'{RBAC_SERVICE_URL}/api/reset-password/{token}', json=data, verify=CA_CERT_PATH)
    return (response.content, response.status_code, response.headers.items())
    
@app.route('/api/get-admin-url', methods=['GET'])
def get_admin_url():
    authenticated, user_data = is_authenticated()
    if not authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'admin_url': admin_url})

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    authenticated, user_data = is_authenticated()
    if authenticated:
        return jsonify({
            'authenticated': True,
            'user_id': user_data.get('user_id'),
            'roles': user_data.get('roles'),
            'permissions': user_data.get('permissions')
        }), 200
    else:
        return jsonify({'authenticated': False}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    response = make_response(jsonify({'message': 'Logged out successfully'}), 200)
    response.set_cookie('token', '', expires=0, httponly=True, secure=True, samesite='Strict')
    response.set_cookie('csrf_token', '', expires=0, httponly=False, secure=True, samesite='Strict')
    response.set_cookie('session', '', expires=0, httponly=True, secure=True, samesite='Strict')
    return response

# Test Route
@app.route('/api/data')
def get_data():
    return jsonify({"message": "Secure data transfer over HTTPS!"})

@app.route('/api/dashboard', methods=['GET'])
@role_required(['Admin'])  # Restrict access to Admin role
def get_dashboard():
    from app import db, Product, Order

    try:
        # Query total products
        total_products = db.session.query(Product).count()
        
        # Query pending orders
        pending_orders = db.session.query(Order).filter_by(Status='Pending').count()

        # # Query orders placed today
        # today = datetime.utcnow().date()
        # orders_today = db.session.query(Order).filter(Order.Order_Date == today).count()
        orders_today = 0
        
        # Query total customers, for now it will show 0
        total_customers = 0

        

        # Prepare the dashboard data
        dashboard_data = {
            'totalProducts': total_products,
            'ordersToday': orders_today,
            'totalCustomers': total_customers,
            'pendingOrders': pending_orders
        }

        return jsonify(dashboard_data), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
#API Calls:
# import APIS:
import APIs

#warehouses:
def get_warehouse(warehouse_id):
    return APIs.warehouse.get_warehouse(warehouse_id)

@app.route('/api/warehouses', methods=['GET'])
@permission_required(['view_warehouse'])
def get_warehouses():
    authenticated, user_data = is_authenticated()
    if not authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = user_data.get('user_id')
    user_roles = user_data.get('roles', [])
    if 'Admin' in user_roles:
        return APIs.warehouse.get_warehouses()
    else:
        return APIs.warehouse.get_warehouse(user_id)





@app.route('/api/create_warehouse', methods=['POST'])
@permission_required(['add_warehouse'])
@verify_csrf
def create_warehouse():
    return APIs.warehouse.create_warehouse()

@app.route('/api/update_warehouse/<int:warehouse_id>', methods=['PUT'])
@permission_required(['update_warehouse'])
@verify_csrf
def update_warehouse(warehouse_id):
    return APIs.warehouse.update_warehouse(warehouse_id)

@app.route('/api/delete_warehouse/<int:warehouse_id>', methods=['DELETE'])
@permission_required(['remove_warehouse'])

@verify_csrf
def delete_warehouse(warehouse_id):
    return APIs.warehouse.delete_warehouse(warehouse_id)

#Create a Category:
@app.route('/api/categories', methods=['POST'])
@permission_required(['add_category'])
@verify_csrf
def create_category():
    return APIs.product.create_category()

#Create a SubCategory:
@app.route('/api/subcategories', methods=['POST'])
@permission_required(['add_subcategory'])
@verify_csrf
def create_subcategory():
    return APIs.product.create_subcategory()


# Products:
# Get All prducts:
@app.route('/api/view_products', methods=['GET'])
@permission_required(['view_product'])
def get_products():
    return APIs.product.get_products()

# Get a single product: 
@app.route('/api/view_product/<int:product_id>', methods=['GET'])
@permission_required(['view_product'])
def get_product(product_id):
    return APIs.product.get_product(product_id)

# Add Product API:
@app.route('/api/add_product', methods=['POST'])
@permission_required(['add_product'])
@verify_csrf
def add_product():
    return APIs.product.add_product()

# Update Product API:
@app.route('/api/update_product/<int:product_id>', methods=['PUT'])
@permission_required(['update_product'])
@verify_csrf
def update_product(product_id):
    return APIs.product.update_product(product_id)

#Delete Product API:
@app.route('/api/delete_product/<int:product_id>', methods=['DELETE'])
@permission_required(['remove_product'])
@verify_csrf
def delete_product(product_id):
    return APIs.product.delete_product(product_id)

#Bulk upload / CSV File:
@app.route('/api/upload_products', methods=['POST'])
@role_required(['Product Manager', 'Admin'])
@verify_csrf
def upload_products():
    return APIs.product.upload_products()


#inventory:
@permission_required(['view_warehouse'])
def fetch_warehouse_by_user_id(user_id):
    """
    Retrieve the Warehouse_ID based on the given user ID (Manager_ID).
    :param user_id: The ID of the user managing the warehouse.
    :return: Tuple containing (data_dict, error_message)
    """
    try:
        # Query the warehouse using the user_id as Manager_ID
        warehouse = Warehouse.query.filter_by(Manager_ID=user_id).first()

        if not warehouse:
            return None, f'No warehouse found for user_id {user_id}'

        # Return the warehouse details
        return {'Warehouse_ID': warehouse.Warehouse_ID}, None

    except Exception as e:
        return None, f'An error occurred: {str(e)}'

def get_warehouse_by_user_id_route(user_id):
    data, error = fetch_warehouse_by_user_id(user_id)
    
    if error:
        status_code = 404 if 'No warehouse found' in error else 500
        return jsonify({'error': error}), status_code
    
    return jsonify(data), 200

@app.route('/api/edit_inventory_by_id', methods=['PUT'])
@permission_required(['update_inventory'])
@verify_csrf
def edit_inventory_by_id():
    authenticated, user_data = is_authenticated()
    if not authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = user_data.get('user_id')
    
    # Fetch warehouse data using the helper function
    data, error = fetch_warehouse_by_user_id(user_id)

    if error:
        status_code = 404 if 'No warehouse found' in error else 500
        return jsonify({'error': error}), status_code

    warehouse_id = data['Warehouse_ID']
    return APIs.inventory.edit_inventory(warehouse_id)

@app.route('/api/view_inventory', methods=['GET'])
@permission_required(['view_inventory'])
@verify_csrf
def view_inventory_by_id():
    authenticated, user_data = is_authenticated()
    if not authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    user_id = user_data.get('user_id')
    user_roles = user_data.get('roles', [])
    # Fetch warehouse data using the helper function
    data, error = fetch_warehouse_by_user_id(user_id)
    if error:
        status_code = 404 if 'No warehouse found' in error else 500
        return jsonify({'error': error}), status_code
    if 'Admin' in user_roles:
        return APIs.inventory.view_inventory()
    else:
        warehouse_id = data['Warehouse_ID']
        return APIs.inventory.view_inventory(warehouse_id)

# for the inventory reports:
@app.route('/api/inventory/turnover', methods=['GET'])
@permission_required(['view_inventory'])
@verify_csrf
def monthly_inventory_report_by_id():
    authenticated, user_data = is_authenticated()
    if not authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = user_data.get('user_id')
    # Fetch warehouse data using the helper function
    data, error = fetch_warehouse_by_user_id(user_id)
    if error:
        print("errorrr i am done here")
        status_code = 404 if 'No warehouse found' in error else 500
        return jsonify({'error': error}), status_code

    warehouse_id = data['Warehouse_ID']
    return APIs.inventory.get_monthly_inventory_turnover(warehouse_id) 

# for the most popular products:
@app.route('/api/inventory/popular-products', methods=['GET'])
@permission_required(['view_inventory'])
@verify_csrf
def most_popular_products_by_id():
    """
    Retrieve the most popular products for the inventory managed by the given user.
    """
    authenticated, user_data = is_authenticated()
    if not authenticated:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = user_data.get('user_id')
    
    # Fetch warehouse data using the helper function
    data, error = fetch_warehouse_by_user_id(user_id)

    if error:
        status_code = 404 if 'No warehouse found' in error else 500
        return jsonify({'error': error}), status_code

    warehouse_id = data['Warehouse_ID']
    return APIs.inventory.get_most_popular_products(warehouse_id)


# Orders Management:
@app.route('/api/create_order', methods=['POST'])
@permission_required(['add_order'])
@verify_csrf
def create_order():
    return APIs.orders.create_order()

@app.route('/api/update_order_status/<int:order_id>', methods=['PUT'])
@permission_required(['update_order'])
@verify_csrf
def update_order(order_id):
    return APIs.orders.update_order_status(order_id)

@app.route('/api/view_all_orders', methods=['GET'])
@permission_required(['view_order'])
@verify_csrf
def view_orders():
    return APIs.orders.view_all_orders()

@app.route('/api/create_order_item', methods=['POST'])
@permission_required(['add_order'])
@verify_csrf
def create_order_item():
    return APIs.orders.create_order_item()

@app.route('/api/remove_order_item', methods=['DELETE'])
@permission_required(['remove_order'])
@verify_csrf
def remove_order_item():
    return APIs.orders.remove_order_item()

# Returns APIs:
@app.route('/api/add_return', methods=['POST'])
@permission_required(['add_return'])
@verify_csrf
def add_return():
    return APIs.orders.add_return()

@app.route('/api/remove_return/<int:return_id>', methods=['DELETE'])
@permission_required(['remove_return'])
@verify_csrf
def remove_return(return_id):
    return APIs.orders.remove_return(return_id)

@app.route('/api/update_return/<int:return_id>', methods=['PUT'])
@permission_required(['update_return'])
@verify_csrf
def update_return(return_id):
    return APIs.orders.update_return_status(return_id)

@app.route('/api/view_return', methods=['GET'])
@permission_required(['view_return'])
@verify_csrf
def view_return():
    return APIs.orders.view_all_returns()



if __name__ == "__main__":
    app.run(ssl_context=(cert_path, key_path), host='0.0.0.0', port=5000, debug=True)