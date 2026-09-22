import pytest, re
from unittest.mock import Mock
from ..order_tracker import OrderTracker
from ..validate import ALLOWED_FILTERS

# --- Fixtures for Unit Tests ---
ORDER_ID_EXISTING = "ORD_EXISTING"
ORDER_ID_NOT_EXISTING = "ORD_NOT_EXISTING"

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    """ 
    mock = Mock()

    fake_db = {
        ORDER_ID_EXISTING: {
            "order_id": ORDER_ID_EXISTING,
            "item_name": "Item",
            "quantity": 1,
            "customer_id": 1,
            "status": "pending"
        },
    }

    def get_order(order_id):
        return fake_db.get(order_id)
    
    def save_order(order_id, order_data: dict):
        fake_db[order_id] = order_data

    mock.get_order.side_effect = get_order
    mock.save_order.side_effect = save_order
    
    mock.get_all_orders.return_value = fake_db
    
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#
def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    mock_storage.save_order.assert_called_once()

def test_add_order_successfully_non_default_status(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001", "completed")
    found_order = mock_storage.get_order("ORD001")
    assert found_order["status"] == "completed"

def test_add_order_duplicate_order_raises_value_error(order_tracker, mock_storage):
    """Tests that attempting to add an order that already exists results in a ValueError."""
    mock_storage.get_order.return_value = {"order_id": ORDER_ID_EXISTING}
    with pytest.raises(ValueError, match=f"Order with ID '{ORDER_ID_EXISTING}' already exists."):
        order_tracker.add_order(ORDER_ID_EXISTING, "New Item", 1, "CUST001")

def test_get_order_by_id_successfully(order_tracker, mock_storage):
    order_id = "ORD001"
    order_tracker.add_order(order_id, "Laptop", 1, "CUST001")
    found_order = order_tracker.get_order_by_id(order_id)
    assert found_order is not None
    assert found_order["order_id"] == order_id
    assert found_order["item_name"] == "Laptop"
    assert found_order["quantity"] == 1
    assert found_order["customer_id"] == "CUST001"
    assert found_order["status"] == "pending"

def test_get_order_by_id_not_found(order_tracker, mock_storage):
    assert order_tracker.get_order_by_id(ORDER_ID_NOT_EXISTING) == None

def test_update_order_status(order_tracker, mock_storage):
    order_tracker.update_order_status(ORDER_ID_EXISTING, "completed")
    updated = order_tracker.get_order_by_id(ORDER_ID_EXISTING)
    assert updated["status"] == "completed"

def test_update_order_status_not_found(order_tracker, mock_storage):
    assert order_tracker.update_order_status(ORDER_ID_NOT_EXISTING, "shipping") == None

def test_list_all_orders(order_tracker, mock_storage):
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
    orders = order_tracker.list_all_orders()
    assert len(orders) == 2
    assert orders[0]["order_id"] == ORDER_ID_EXISTING
    assert orders[1]["order_id"] == "ORD001"
    assert orders[0]["item_name"] == "Item"

def test_list_orders_with_filter_by_status(order_tracker):
    order_tracker.add_order("ORD_COMPLETED", "Laptop", 1, "CUST001", "completed")
    completed_orders = order_tracker.list_orders_with_filter({"status": "completed"})
    assert len(completed_orders) == 1
    assert completed_orders[0]["order_id"] == "ORD_COMPLETED"

def test_list_orders_with_filter_by_customer_id(order_tracker):
    order_tracker.add_order("ORD_C2", "Laptop", 1, "CUST002", "completed")
    c2_orders = order_tracker.list_orders_with_filter({"customer_id": "CUST002"})
    assert len(c2_orders) == 1
    assert c2_orders[0]["order_id"] == "ORD_C2"

def test_list_orders_with_filter_by_customer_id_and_status(order_tracker):
    order_tracker.add_order("ORD_C2_pending", "Laptop", 1, "CUST002", "pending")
    order_tracker.add_order("ORD_C2_completed", "Laptop", 1, "CUST002", "completed")
    c2_orders = order_tracker.list_orders_with_filter({"customer_id": "CUST002", "status": "completed"})
    assert len(c2_orders) == 1
    assert c2_orders[0]["order_id"] == "ORD_C2_completed"

def test_list_orders_with_filter_and_bad_filter(order_tracker):
    order_tracker.add_order("ORD_C2_pending", "Laptop", 1, "CUST002", "pending")
    order_tracker.add_order("ORD_C2_completed", "Laptop", 1, "CUST002", "completed")
    result = order_tracker.list_orders_with_filter({"foobar": "baz", "status": "completed"})
    assert len(result) == 0

def test_list_orders_with_filter_empty(order_tracker):
    orders = order_tracker.list_orders_with_filter({"status": "completed"})
    assert len(orders) == 0