from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from sqlalchemy import or_
from models import db, User, Role, Permission, ActivityLog
from flask_wtf.csrf import CSRFProtect, generate_csrf
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from db_config import DB_CONFIG
import pyotp
from waitress import serve
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CONFIG
JWT_ALGORITHM = 'HS256'

csrf = CSRFProtect(app)

CORS(app, origins=["https://localhost:3000"], supports_credentials=True)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

cert_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "rbac.crt")
key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certs", "rbac.key")


db.init_app(app)
def create_roles_and_permissions():
    # Permissions
    permission_names = [
        # Inventory permissions
        'add_inventory', 'remove_inventory', 'update_inventory', 'view_inventory',
        'add_warehouse', 'remove_warehouse', 'update_warehouse', 'view_warehouse',
        # Product permissions
        'add_product', 'remove_product', 'update_product', 'view_product',
        'add_category', 'remove_category', 'update_category', 'view_category',
        'add_subcategory', 'remove_subcategory', 'update_subcategory', 'view_subcategory',
        # Order permissions
        'add_order', 'remove_order', 'update_order', 'view_order',
        'add_return', 'remove_return', 'update_return', 'view_return',
    ]

    permissions = {}
    for name in permission_names:
        # Check if the permission already exists
        permission = Permission.query.filter_by(Name=name).first()
        if not permission:
            permission = Permission(Name=name)
            db.session.add(permission)
        permissions[name] = permission

    # Roles
    role_names = ['Admin', 'Product Manager', 'Inventory Manager', 'Order Manager', 'Customer']
    roles = {}
    for name in role_names:
        # Check if the role already exists
        role = Role.query.filter_by(Name=name).first()
        if not role:
            role = Role(Name=name)
            db.session.add(role)
        roles[name] = role

    db.session.commit()  # Commit to assign IDs before setting relationships

    # Assign permissions to roles
    roles['Admin'].permissions = list(permissions.values())

    # Product Manager permissions
    roles['Product Manager'].permissions = [
        permissions['add_product'],
        permissions['remove_product'],
        permissions['update_product'],
        permissions['view_product'],
        permissions['add_category'],
        permissions['remove_category'],
        permissions['update_category'],
        permissions['view_category'],
        permissions['add_subcategory'],
        permissions['remove_subcategory'],
        permissions['update_subcategory'],
        permissions['view_subcategory'],
    ]

    # Inventory Manager permissions
    roles['Inventory Manager'].permissions = [
        permissions['add_inventory'],
        permissions['remove_inventory'],
        permissions['update_inventory'],
        permissions['view_inventory'],
        permissions['add_warehouse'],
        permissions['remove_warehouse'],
        permissions['update_warehouse'],
        permissions['view_warehouse'],
    ]

    # Order Manager permissions
    roles['Order Manager'].permissions = [
        permissions['add_order'],
        permissions['remove_order'],
        permissions['update_order'],
        permissions['view_order'],
        permissions['add_return'],
        permissions['remove_return'],
        permissions['update_return'],
        permissions['view_return'],
    ]

    # Customer permissions
    roles['Customer'].permissions = [
        permissions['view_product'],
        permissions['view_order'],
    ]

    db.session.commit()
    # Helper function to create users
def create_users():
    # Fetch roles from the database
    roles = {}
    role_names = ['Admin', 'Product Manager', 'Inventory Manager', 'Order Manager', 'Customer']
    for name in role_names:
        role = Role.query.filter_by(Name=name).first()
        if role:
            roles[name] = role

    def create_user(username, email, password, role, two_factor_enabled=False):
        user = User.query.filter_by(Username=username).first()
        if not user:
            user = User(Username=username, Email=email, two_factor_enabled=two_factor_enabled)
            user.set_password(password)
            if two_factor_enabled:
                user.two_factor_secret = pyotp.random_base32()
                user.two_factor_setup_complete = False
            db.session.add(user)
            db.session.commit()
            user.roles.append(role)
            db.session.commit()

    # Create users for each role
    #create_user('admin', 'PUTEMAIL', 'admin123', roles['Admin'], two_factor_enabled=True)
    create_user('admin', 'admin@example.com', 'Admin123!', roles['Admin'])
    create_user('product_manager', 'pm@example.com', 'Product123!', roles['Product Manager'])
    create_user('inventory_manager', 'im@example.com', 'Inventory123!', roles['Inventory Manager'])
    create_user('order_manager', 'om@example.com', 'Order123!', roles['Order Manager'])
    create_user('customer', 'customer@example.com', 'Customer123!', roles['Customer'])
# Initialize the database
with app.app_context():
    # db.drop_all() to reset the dB
    db.create_all()
    create_roles_and_permissions()  # Ensure roles and permissions are created
    create_users()   # Now create users for each role


@app.route('/api/login', methods=['POST'])
@csrf.exempt
def login():
    data = request.get_json()
    username_or_email = data.get('username')
    password = data.get('password')

    user = User.query.filter(
        or_(User.Username == username_or_email, User.Email == username_or_email)
    ).first()
    
    if user.is_account_locked():
            remaining_time = user.account_locked_until - datetime.utcnow()
            minutes = int(remaining_time.total_seconds() // 60) + 1  # Round up
            return jsonify({
                'error': 'Account is locked.',
                'message': f'Please try again after {minutes} minute(s).'
            }), 403

    if not user or not user.check_password(password):
        # Handle invalid credentials
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                lockout_duration = timedelta(minutes=15)
                user.account_locked_until = datetime.utcnow() + lockout_duration
                user.failed_login_attempts = 0
                db.session.commit()
                return jsonify({
                    'error': 'Account locked due to multiple failed login attempts.',
                    'message': f'Please try again after {lockout_duration.seconds // 60} minutes.'
                }), 403  # 403 Forbidden is more appropriate for locked accounts
            db.session.commit()
        return jsonify({'error': 'Invalid credentials'}), 401


    user.failed_login_attempts = 0
    db.session.commit()

    # Gather roles and permissions
    user_roles = [role.Name for role in user.roles]
    user_permissions = []
    for role in user.roles:
        user_permissions.extend([perm.Name for perm in role.permissions])
    user_permissions = list(set(user_permissions))  # Remove duplicates

    if user.two_factor_enabled:
        if not user.two_factor_setup_complete:
            # Generate provisioning URI for 2FA setup
            import pyotp
            totp = pyotp.TOTP(user.two_factor_secret)
            provisioning_uri = totp.provisioning_uri(name=user.Email, issuer_name="GC Ecommerce")
            return jsonify({
                'message': 'Two-factor authentication setup required',
                'permissions': user_permissions,
                'roles': user_roles,
                'token': None,
                'requires_2fa_setup': True,
                'user_id': user.User_ID,
                'provisioning_uri': provisioning_uri
            }), 200
        else:
            # Require 2FA verification
            return jsonify({
                'message': 'Two-factor authentication required',
                'permissions': user_permissions,
                'roles': user_roles,
                'token': None,
                'requires_2fa': True,
                'user_id': user.User_ID
            }), 200

    # Create the JWT payload
    payload = {
        'user_id': user.User_ID,
        'exp': datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm=JWT_ALGORITHM)

    return jsonify({
        'message': 'Login successful',
        'permissions': user_permissions,
        'roles': user_roles,
        'token': token
    }), 200

@app.route('/api/setup-2fa', methods=['POST'])
@csrf.exempt
def setup_2fa():
    data = request.get_json()
    user_id = data.get('user_id')
    token = data.get('token')  # The TOTP token entered by the user

    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404

    if not user.two_factor_enabled:
        return jsonify({'error': 'Two-factor authentication is not enabled for this user.'}), 400

    if user.two_factor_setup_complete:
        return jsonify({'message': 'Two-factor authentication is already set up.'}), 200

    # Verify the provided TOTP token
    totp = pyotp.TOTP(user.two_factor_secret)
    if totp.verify(token):
        user.two_factor_setup_complete = True
        db.session.commit()
        return jsonify({'message': 'Two-factor authentication has been set up successfully.'}), 200
    else:
        return jsonify({'error': 'Invalid 2FA token.'}), 400

@app.route('/api/verify-2fa', methods=['POST'])
@csrf.exempt
def verify_2fa():
    data = request.get_json()
    user_id = data.get('user_id')
    token = data.get('token')

    user = User.query.get(user_id)
    if not user or not user.two_factor_enabled or not user.two_factor_setup_complete:
        return jsonify({'error': 'Invalid request.'}), 400

    import pyotp
    totp = pyotp.TOTP(user.two_factor_secret)
    if totp.verify(token):
        # Generate JWT token
        jwt_token = jwt.encode({
            'user_id': user.User_ID,
            'exp': datetime.utcnow() + timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm=JWT_ALGORITHM)
        return jsonify({'token': jwt_token}), 200
    else:
        return jsonify({'error': 'Invalid 2FA code.'}), 400

@app.route('/api/request-password-reset', methods=['POST'])
@csrf.exempt
def request_password_reset():
    data = request.get_json()
    email = data.get('email')
    user = User.query.filter_by(Email=email).first()
    
    if user:
        # Generate a secure token
        token = serializer.dumps(email, salt='password-reset-salt')
        reset_link = f"http://localhost:3000/reset-password/{token}"  # Ensure this matches your frontend URL

        # Send password reset email
        msg = Message(
            'Password Reset Request',
            sender='noreply@example.com',
            recipients=[email]
        )
        msg.body = f'Please click the link to reset your password: {reset_link}'
        
        try:
            mail.send(msg)
            app.logger.debug(f"Sent password reset email to {email} with token {token}")
        except Exception as e:
            app.logger.error(f"Failed to send password reset email: {e}")
            return jsonify({'error': 'Failed to send reset email.'}), 500

        # Store the token and its expiration in the user's record
        user.password_reset_token = token
        user.password_reset_expiration = datetime.utcnow() + timedelta(hours=1000)
        db.session.commit()
        app.logger.debug(f"Stored reset token for user {user.Username}")

    # Always return this response to prevent email enumeration
    return jsonify({'message': 'If an account with that email exists, a reset link has been sent.'}), 200

@app.route('/api/reset-password/<token>', methods=['POST'])
@csrf.exempt
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except Exception:
        return jsonify({'error': 'Invalid or expired token.'}), 400

    data = request.get_json()
    new_password = data.get('password')
    user = User.query.filter_by(Email=email).first()

    if user and user.password_reset_token == token:
        user.set_password(new_password)
        user.password_reset_token = None
        user.password_reset_expiration = None
        db.session.commit()
        return jsonify({'message': 'Password has been reset successfully.'}), 200
    else:
        return jsonify({'error': 'Invalid or expired token.'}), 400

@app.route('/api/verify-token', methods=['POST'])
@csrf.exempt
def verify_token():
    data = request.get_json()
    # print(f"Received verify-token request data: {data}")  # Logging received data
    token = data.get('token')
    if not token:
        print("Token is missing in the request.")
        return jsonify({'error': 'Token is missing'}), 400
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=[JWT_ALGORITHM])
        user_id = payload.get('user_id')
        # print(f"Decoded token for user_id: {user_id}")
        # Fetch user from the database
        user = User.query.get(user_id)
        if not user:
            print(f"User with ID {user_id} not found.")
            return jsonify({'error': 'User not found'}), 404
        # Get user's roles and permissions
        roles = [role.Name for role in user.roles]
        permissions = []
        for role in user.roles:
            permissions.extend([perm.Name for perm in role.permissions])
        permissions = list(set(permissions))  # Remove duplicates
        # print(f"User Roles: {roles}")
        # print(f"User Permissions: {permissions}")
        return jsonify({
            'user_id': user_id,
            'roles': roles,
            'permissions': permissions
        }), 200
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        print("Invalid token.")
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/api/log_activity', methods=['POST'])
@csrf.exempt
def log_activity():
    try:
        data = request.get_json()
        if data is None:
            app.logger.error("No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400

        user_id = data.get('user_id')
        endpoint = data.get('endpoint')
        method = data.get('method')
        timestamp = data.get('timestamp')

        if not endpoint or not method:
            app.logger.error(f"Missing required fields in data: {data}")
            return jsonify({'error': 'Missing required fields'}), 400

        if timestamp:
            try:
                timestamp = datetime.utcfromtimestamp(timestamp)
            except (TypeError, ValueError) as e:
                app.logger.error(f"Invalid timestamp value: {timestamp}")
                timestamp = datetime.utcnow()
        else:
            timestamp = datetime.utcnow()

        activity = ActivityLog(
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            timestamp=timestamp
        )
        db.session.add(activity)
        db.session.commit()
        return jsonify({'message': 'Activity logged successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error logging activity: {e}")
        return jsonify({'error': 'Error logging activity'}), 500
    
if __name__ == "__main__":
    app.run(ssl_context=(cert_path, key_path),host='0.0.0.0',port=5001, debug=True)