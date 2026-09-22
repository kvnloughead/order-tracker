# This file stores code for validating order data.

VALID_STATUSES = ["pending", "processing", "shipped", "delivered", "cancelled"]
ALLOWED_FILTERS = ["status", "customer_id"]

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
    return status in VALID_STATUSES, f'\'{field_name}\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled".'

def validate_filters(filters: dict):
    for k, v in filters.items():
        if k not in ALLOWED_FILTERS:
            return False, { k: f"'{k}' is not an allowed filter."}
        if k == "status":
            is_valid, msg = is_valid_status(v, k)
            if not is_valid:
                return False, { "status": msg }
        if k == "customer_id":
            is_valid = is_non_empty_string(v)
            if not is_valid:
                return False, {"customer_id": "'customer_id' must be a non-empty string."} 
    return True, {}