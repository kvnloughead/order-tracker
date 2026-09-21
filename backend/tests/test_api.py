import pytest
from backend.app import app, in_memory_storage, validate_order

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

@pytest.mark.api
def test_add_order_api_success(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    assert response.json['order_id'] == "API001"

@pytest.mark.api
def test_add_order_api_duplicate_id_sends_409(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    _ = client.post('/api/orders', json=order_data)
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 409
    assert response.json.get('error') == f"Order with ID 'API001' already exists."

@pytest.mark.api
def test_add_order_api_bad_request(client):
    orders = [
        {
             "order_id": "", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
        },
        {
             "order_id": 1, "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": "", "quantity": 1, "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": 1, "quantity": 1, "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": "API Laptop", "quantity": 0, "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": "API Laptop", "quantity": -1, "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": "API Laptop", "quantity": 1.23, "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": "API Laptop", "quantity": "1", "customer_id": "APICUST001"
        },
        {
             "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": ""
        },
        {
             "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": 1
        },
    ]
    for order in orders:
        response = client.post('/api/orders', json=order)
        msg = response.json.get('error')
        assert response.status_code == 400
        assert isinstance(msg, str) and msg != ""

@pytest.mark.api
def test_get_order_api_success(client):
    client.post('/api/orders', json={
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json['order_id'] == "GET001"

@pytest.mark.api
def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404

@pytest.mark.api
def test_update_order_status_api_success(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json['status'] == "shipped"

@pytest.mark.api
def test_update_order_api_not_found(client):
    response = client.put('/api/orders/NONEXISTENT/status', json={"new_status": "shipped"})
    assert response.status_code == 404

@pytest.mark.api
def test_update_order_api_invalid_status(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response_1 = client.put('/api/orders/UPDATE001/status', json={"new_status": ""})
    response_2 = client.put('/api/orders/UPDATE001/status', json={"new_status": "foobar"})
    for res in [response_1, response_2]:
        assert res.status_code == 400
        assert res.json.get("error") == '\'new_status\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled"].'

@pytest.mark.api
def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 2

@pytest.mark.api
def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "S001"

@pytest.mark.api
def test_list_orders_by_status_api_invalid_status(client):
    response_1 = client.get('/api/orders?status=foobar')
    response_2 = client.get('/api/orders?status=')
    for res in [response_1, response_2]:
        assert res.status_code == 400
        assert res.json.get("error") == '\'status\' must be one of these options: "pending", "processing", "shipped", "delivered", "cancelled"].'

@pytest.mark.api
def test_missing_json_body(client):
    response_1 = client.put('/api/orders/UPDATE001/status', headers={"Content-Type":"application/json"})
    response_2 = client.post('/api/orders', headers={"Content-Type":"application/json"})
    for res in [response_1, response_2]:
        assert res.status_code == 415
        assert res.json.get("error") == "JSON body is required."

@pytest.mark.api
def test_missing_content_type_and_body(client):
    response_1 = client.put('/api/orders/UPDATE001/status')
    response_2 = client.post('/api/orders')
    for res in [response_1, response_2]:
        assert res.status_code == 415
        assert res.json.get("error") == "JSON body is required."
