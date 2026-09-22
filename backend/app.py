from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage
from backend.validate import validate_order, is_valid_status, validate_filters

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

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
    if not request.args:
        return order_tracker.list_all_orders(), 200
    else:
        valid, errors = validate_filters(request.args)
        if not valid:
            return handle_error_response(errors, 400)
        orders = order_tracker.list_orders_with_filter(request.args)
        return jsonify(orders), 200

def handle_error_response(msg: str, status: int):
    """
    Sends a response with the given error message and status code. The message 
    is wrapped in an { "error" } object.
    """
    return jsonify({"error": msg}), status

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
