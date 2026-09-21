from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)
VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    if not request.data:
        return handle_error_response("JSON body is required.", 415)
    data = request.get_json()
    if data.get("status") is None:
        data["status"] = "pending"
    valid, msg = validate_order(data)
    if not valid:
        return handle_error_response(msg, 400)
    try:
        order_tracker.add_order(
            data.get("order_id"), 
            data.get("item_name"), 
            data.get("quantity"), 
            data.get("customer_id"),
            data.get("status") or "pending"
        )
    except ValueError as e:   
        return handle_error_response(str(e), 409) 
    return jsonify(data), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)
    if order is None:
        return handle_error_response(f"Order not found (ID='{order_id}').", 404)
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    if not request.data:
        return handle_error_response("JSON body is required.", 415)
    json = request.get_json()
    if json is None:
        return handle_error_response("JSON body is required.", 415)
    new_status = json.get("new_status") 
    is_valid, msg = is_valid_status(new_status, "new_status")
    if not is_valid:
        return handle_error_response(msg, 400)
    updated = order_tracker.update_order_status(order_id, new_status)
    if updated is None:
        return handle_error_response(f"Order not found (ID='{order_id}').", 404)
    return jsonify(updated), 200    

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    orders = {}
    status = request.args.get('status')
    if status is not None:
        is_valid, msg = is_valid_status(status)
        if not is_valid:
            return jsonify({ "error": msg}), 400
        orders = order_tracker.list_orders_by_status(status) 
    else:
        orders = order_tracker.list_all_orders()
    return jsonify(orders), 200

def handle_error_response(msg, status):
    return jsonify({"error": msg}), status

def validate_order(order):
    """
    Validates the fields of an order:
        "order_id": str,        # unique ID (non-empty)
        "item_name": str,       # non-empty
        "quantity": int,        # positive integer
        "customer_id": str,     # non-empty
        "status": str           # one of: "pending", "processing", "shipped", "delivered", "cancelled"
    """
    non_empty_string_fields = ["order_id", "item_name", "customer_id"]
    for f in non_empty_string_fields:
        if not is_non_empty_string(order[f]):
            return False, f"'{f}' must be a non-empty string."
    quantity = order["quantity"]
    if not is_positive_integer(quantity):
        return False, "'quantity' must be a positive integer."
    valid_status, msg = is_valid_status(order["status"])
    if not valid_status:
        return False, msg
    return True, ""
    
def is_non_empty_string(s):
    return isinstance(s, str) and not s == ""

def is_positive_integer(n):
    return isinstance(n, int) and n > 0

def is_valid_status(status, field_name = "status"):
    return status in VALID_STATUSES, f'\'{field_name}\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled"].'

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
