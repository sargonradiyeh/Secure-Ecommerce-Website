
# NOT AVAILABLE FOR ANY ROLE, ONLY USED BY US TO ADD A WAREHOUSE (NB OF WAREHOUSES IS FIXED)

# All those functions work normally

from flask import Flask, jsonify, request, make_response


# View all warehouses: 
def get_warehouses():
    from app import Warehouse, db
    warehouses = Warehouse.query.all()
    
    # Manually serialize the data
    # Can be put insead in the model
    warehouse_list = [
        {
            "Warehouse_ID": w.Warehouse_ID,
            "Manager_ID": w.Manager_ID,
            "Location": w.Location,
        }
        for w in warehouses
    ]

    # Return the serialized list as a JSON response
    return jsonify(warehouse_list)


# View a single warehouse
def get_warehouse(warehouse_id):
    from app import Warehouse, db
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404
    return jsonify({
        'Warehouse_ID': warehouse.Warehouse_ID,
        'Manager_ID': warehouse.Manager_ID,
        'Location': warehouse.Location
    }), 200

# Create a warehouse:
def create_warehouse():
    from app import Warehouse, db
    data = request.get_json()
    warehouse = Warehouse(
        Manager_ID=data['Manager_ID'],
        Location=data['Location']
    )
    db.session.add(warehouse)
    db.session.commit()
    return jsonify("warehouse added successfuly"), 201

# Update a warehouse
def update_warehouse(warehouse_id):
    from app import Warehouse, db
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404

    data = request.get_json()
    warehouse.Manager_ID = data.get('Manager_ID', warehouse.Manager_ID)
    warehouse.Location = data.get('Location', warehouse.Location)
    db.session.commit()
    return jsonify({'message': 'Warehouse updated successfully'}), 200

# Delete a warehouse
def delete_warehouse(warehouse_id):
    from app import Warehouse, db
    warehouse = Warehouse.query.get(warehouse_id)
    if not warehouse:
        return jsonify({'error': 'Warehouse not found'}), 404

    db.session.delete(warehouse)
    db.session.commit()
    return jsonify({'message': 'Warehouse deleted successfully'}), 200
