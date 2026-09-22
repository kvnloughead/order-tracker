from backend.app import validate_order, validate_filters

def test_validate_order_invalid_id():
    """Verifies that only non-empty strings are valid order IDs."""
    empty_id_order = {
        "order_id": "", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    non_string_id_order = {
        "order_id": 1, "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    valid_1, msg_1 = validate_order(empty_id_order)
    assert valid_1 == False
    assert msg_1 == "'order_id' must be a non-empty string."
    valid_2, msg_2 = validate_order(non_string_id_order)
    assert valid_2 == False
    assert msg_2 == "'order_id' must be a non-empty string."

def test_validate_order_nonempty_item_name():
    empty_item_name = {
        "order_id": "ORD001", "item_name": "", "quantity": 1, "customer_id": "APICUST001"
    }
    non_string_item_name = {
        "order_id": "ORD001", "item_name": 1, "quantity": 1, "customer_id": "APICUST001"
    }
    valid_1, msg_1 = validate_order(empty_item_name)
    assert valid_1 == False
    assert msg_1 == "'item_name' must be a non-empty string."
    valid_2, msg_2 = validate_order(non_string_item_name)
    assert valid_2 == False
    assert msg_2 == "'item_name' must be a non-empty string."

def test_validate_order_non_empty_string_fields():
    order = {
        "order_id": "ORD001", "item_name": "stuff", "quantity": 1, "customer_id": "APICUST001"
    }
    fields = ["order_id", "item_name", "customer_id"]
    for field in fields:
        with_empty_field = order.copy()
        with_empty_field[field] = ""
        valid, msg = validate_order(with_empty_field)
        assert valid == False
        assert msg == f"'{field}' must be a non-empty string."

        with_non_string_field = order.copy()
        with_non_string_field[field] = 1
        valid, msg = validate_order(with_non_string_field)
        assert valid == False
        assert msg == f"'{field}' must be a non-empty string."

def test_validate_order_quantity_positive_integer():
    orders = [
        {
            "order_id": "ORD001", "item_name": "stuff", "quantity": 0, "customer_id": "APICUST001"
        },
        {
            "order_id": "ORD001", "item_name": "stuff", "quantity": -1, "customer_id": "APICUST001"
        },
        {
            "order_id": "ORD001", "item_name": "stuff", "quantity": 1.23, "customer_id": "APICUST001"
        },
        {
            "order_id": "ORD001", "item_name": "stuff", "quantity": "1", "customer_id": "APICUST001"
        },
    ]
    for order in orders:
        valid, msg = validate_order(order)
        assert valid == False
        assert msg == "'quantity' must be a positive integer."

def test_validate_order_validates_status_enum():
    order =  {
        "order_id": "ORD001", "item_name": "stuff", "quantity": 1, "customer_id": "APICUST001", "status": "bad status"
    }
    valid, msg = validate_order(order)
    assert valid == False
    assert msg == '\'status\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled".'

def test_validate_filters_valid_filters():
    filters = { "customer_id": "CUST001", "status": "pending"}
    valid, error = validate_filters(filters)
    assert valid == True
    assert error == {}

def test_validate_filters_unknown_filter():
    filters = { "customer_id": "CUST001", "foobar": "baz"}
    valid, error = validate_filters(filters)
    assert valid == False
    assert error == {"foobar": "'foobar' is not an allowed filter."}

def test_validate_filters_invalid_status():
    filters = { "customer_id": "CUST001", "status": "..."}
    valid, error = validate_filters(filters)
    assert valid == False
    # assert error == {"status": '\'status\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled".' }
    assert error["status"] == '\'status\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled".'

def test_validate_filters_invalid_customer_id():
    filters = { "customer_id": ""}
    valid, error = validate_filters(filters)
    assert valid == False
    assert error == {"customer_id": "'customer_id' must be a non-empty string."}