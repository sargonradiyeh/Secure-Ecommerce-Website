from flask import request, jsonify

# customer creates order items, and when they submit, it creates an order

# create orders:
def create_order():
    from app import db, Order
    """
    Create a new order.
    Expected JSON payload:
    {
        "Total_Amount": 100.0,
        "Order_Date": "2024-11-17",
        "Status": "Pending",
        "Total_Price": 150.0
    }
    """
    try:
        data = request.get_json()

        # Extract and validate required fields
        order_date = data.get('Order_Date')
        status = data.get('Status')

        if not all([order_date, status]):
            return jsonify({'error': 'All fields (Total_Amount, Order_Date, Status, Total_Price) are required'}), 400

        # Create and save the new order
        new_order = Order(
            Total_Amount=0,
            Order_Date=order_date,
            Status=status,
            Total_Price=0
        )
        db.session.add(new_order)
        db.session.commit()

        return jsonify({'message': 'Order created successfully', 'Order_ID': new_order.Order_ID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# update_order:
def update_order_status(order_id):
    from app import db, Order
    """
    Update the status of an order.
    Expected JSON payload:
    {
        "Status": "Completed"
    }
    """
    try:
        data = request.get_json()
        new_status = data.get('Status')

        if not new_status:
            return jsonify({'error': 'Status is required'}), 400

        # Find the order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': f'Order with ID {order_id} not found'}), 404

        # Update the status
        order.Status = new_status
        db.session.commit()

        return jsonify({'message': 'Order status updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# view all orders:
def view_all_orders():
    from app import db, Order, OrderItem
    """
    View all orders in the system and recalculate totals if needed.
    """
    try:
        # Query all orders from the database
        orders = Order.query.all()
        if not orders:
            return jsonify({'message': 'No orders found'}), 200

        # Recalculate totals for all orders
        for order in orders:
            total_price = sum(item.Quantity * item.Price for item in order.order_items)
            total_amount = sum(item.Quantity for item in order.order_items)
            order.Total_Price = total_price
            order.Total_Amount = total_amount

        # Commit updates to the database
        db.session.commit()

        # Serialize the orders
        order_list = [
            {
                'Order_ID': order.Order_ID,
                'Total_Amount': order.Total_Amount,
                'Order_Date': str(order.Order_Date),
                'Status': order.Status,
                'Total_Price': order.Total_Price
            }
            for order in orders
        ]

        return jsonify(order_list), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

    
#create order item:
def create_order_item():
    from app import db, OrderItem, Order
    """
    Create or update an order item.
    Expected JSON payload:
    {
        "Order_ID": 1,
        "Product_ID": 101,
        "Quantity": 2,
        "Price": 50.0
    }
    """
    try:
        data = request.get_json()

        # Extract and validate required fields
        order_id = data.get('Order_ID')
        product_id = data.get('Product_ID')
        quantity = data.get('Quantity')
        price = data.get('Price')

        if not all([order_id, product_id, quantity, price]):
            return jsonify({'error': 'All fields (Order_ID, Product_ID, Quantity, Price) are required'}), 400

        # Check if the product is already in the order
        existing_order_item = OrderItem.query.filter_by(Order_ID=order_id, Product_ID=product_id).first()

        if existing_order_item:
            # If it exists, increment the quantity
            existing_order_item.Quantity += quantity
            db.session.commit()
            message = 'Order item quantity updated successfully'
        else:
            # If it doesn't exist, create a new order item
            new_order_item = OrderItem(
                Order_ID=order_id,
                Product_ID=product_id,
                Quantity=quantity,
                Price=price
            )
            db.session.add(new_order_item)
            db.session.commit()
            message = 'Order item added successfully'

        # Recalculate the total price and total amount of the order
        recalculate_order_total(order_id)

        return jsonify({'message': message}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

def remove_order_item():
    from app import db, OrderItem, Order
    """
    Remove an order item.
    Expected JSON payload:
    {
        "Order_ID": 1,
        "Product_ID": 101
    }
    """
    try:
        data = request.get_json()

        # Extract and validate required fields
        order_id = data.get('Order_ID')
        product_id = data.get('Product_ID')

        if not all([order_id, product_id]):
            return jsonify({'error': 'Order_ID and Product_ID are required'}), 400

        # Find the order item
        order_item = OrderItem.query.filter_by(Order_ID=order_id, Product_ID=product_id).first()

        if not order_item:
            return jsonify({'error': f'Order item with Order_ID {order_id} and Product_ID {product_id} not found'}), 404

        # Delete the order item
        db.session.delete(order_item)
        db.session.commit()

        # Recalculate the total price and total amount of the order
        recalculate_order_total(order_id)

        return jsonify({'message': 'Order item removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500






#remove order item:
def remove_order_item():
    from app import db, OrderItem
    """
    Remove an order item.
    Expected JSON payload:
    {
        "Order_ID": 1,
        "Product_ID": 101
    }
    """
    try:
        data = request.get_json()

        # Extract and validate required fields
        order_id = data.get('Order_ID')
        product_id = data.get('Product_ID')

        if not all([order_id, product_id]):
            return jsonify({'error': 'Order_ID and Product_ID are required'}), 400

        # Find the order item
        order_item = OrderItem.query.filter_by(Order_ID=order_id, Product_ID=product_id).first()

        if not order_item:
            return jsonify({'error': f'Order item with Order_ID {order_id} and Product_ID {product_id} not found'}), 404

        # Delete the order item
        db.session.delete(order_item)
        db.session.commit()
        recalculate_order_total(order_id)
        return jsonify({'message': 'Order item removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
def recalculate_order_total(order_id):
    from app import db, Order, OrderItem

    # Get the order and its items
    order = Order.query.get(order_id)
    if not order:
        return

    # Calculate the new total price and total amount
    total_price = sum(item.Quantity * item.Price for item in order.order_items)
    total_amount = sum(item.Quantity for item in order.order_items)

    # Update the order
    order.Total_Price = total_price
    order.Total_Amount = total_amount  # Assuming this column exists in the `Order` model

    db.session.commit()


# return item, (should delete from orders)
def add_return():
    from app import db, Order, Inventory, Return
    """
    Add a new return.
    Expected JSON payload:
    {
        "Order_ID": 1,
        "Return_Date": "2024-11-17",
        "Status": "Processed",
        "Refund_Amount": 150.0
    }
    """
    try:
        data = request.get_json()

        # Extract and validate required fields
        order_id = data.get('Order_ID')
        return_date = data.get('Return_Date')
        status = data.get('Status')
        refund_amount = data.get('Refund_Amount')

        if not all([order_id, return_date, status, refund_amount]):
            return jsonify({'error': 'All fields (Order_ID, Return_Date, Status, Refund_Amount) are required'}), 400

        # Fetch the order to be returned
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': f'Order with ID {order_id} not found'}), 404

        # Restock inventory for each order item
        for item in order.order_items:
            inventory = Inventory.query.filter_by(
                Product_ID=item.Product_ID, Warehouse_ID=item.product.inventories[0].Warehouse_ID
            ).first()

            if inventory:
                inventory.Stock_Level += item.Quantity
            db.session.delete(item)
            
        # Delete the order from the Order table
        db.session.delete(order)

        # Create a new return
        new_return = Return(
            Return_Date=return_date,
            Status=status,
            Refund_Amount=refund_amount,
        )
        db.session.add(new_return)

        # Commit changes to the database
        db.session.commit()

        return jsonify({'message': 'Return created successfully', 'Return_ID': new_return.Return_ID}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Remove return:
def remove_return(return_id):
    from app import db, Return
    """
    Remove a return by ID.
    """
    try:
        # Fetch the return entry
        return_entry = Return.query.get(return_id)
        if not return_entry:
            return jsonify({'error': f'Return with ID {return_id} not found'}), 404

        # Delete the return entry
        db.session.delete(return_entry)
        db.session.commit()

        return jsonify({'message': f'Return with ID {return_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Update return:
def update_return_status(return_id):
    from app import db, Return
    """
    Update the status of a return.
    Expected JSON payload:
    {
        "Status": "Completed"
    }
    """
    try:
        data = request.get_json()
        new_status = data.get('Status')

        if not new_status:
            return jsonify({'error': 'Status is required'}), 400

        # Fetch the return entry
        return_entry = Return.query.get(return_id)
        if not return_entry:
            return jsonify({'error': f'Return with ID {return_id} not found'}), 404

        # Update the status
        return_entry.Status = new_status
        db.session.commit()

        return jsonify({'message': 'Return status updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# View all returns:
def view_all_returns():
    from app import db, Return
    """
    View all returns in the system.
    """
    try:
        # Query all returns from the database
        returns = Return.query.all()

        if not returns:
            return jsonify({'message': 'No returns found'}), 200

        # Serialize the returns
        return_list = [
            {
                'Return_ID': return_entry.Return_ID,
                'Return_Date': str(return_entry.Return_Date),
                'Status': return_entry.Status,
                'Refund_Amount': return_entry.Refund_Amount,
                # 'Order_ID': return_entry.Order_ID
            }
            for return_entry in returns
        ]

        return jsonify(return_list), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
