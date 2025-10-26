import allure
import pytest
import requests
from .configuration import ORDER_PATH
from .helpers import generate_random_string

@allure.feature('Заказы')
class TestOrders:
    def setup_method(self):
        self.track = None

    def teardown_method(self):
        if self.track:
            requests.put(f"{ORDER_PATH}/cancel", json={"track": self.track})

    @pytest.mark.parametrize('color', [
        ['BLACK'],
        ['GREY'],
        ['BLACK', 'GREY'],
        []
    ])
    @allure.title('Создание заказа с разными цветами')
    def test_create_order_with_different_colors(self, color):
        payload = {
            "firstName": generate_random_string(10),
            "lastName": generate_random_string(10),
            "address": "Test address",
            "metroStation": 4,
            "phone": "+7 800 355 35 35",
            "rentTime": 5,
            "deliveryDate": "2024-06-06",
            "comment": "Test comment",
            "color": color
        }

        response = requests.post(ORDER_PATH, json=payload)
        assert response.status_code == 201
        assert "track" in response.json()
        
        self.track = response.json()["track"]

    @allure.title('Получение списка заказов')
    def test_get_orders_list(self):
        payload = {
            "firstName": generate_random_string(10),
            "lastName": generate_random_string(10),
            "address": "Test address",
            "metroStation": 4,
            "phone": "+7 800 355 35 35",
            "rentTime": 5,
            "deliveryDate": "2024-06-06",
            "comment": "Test comment",
            "color": ["BLACK"]
        }

        create_response = requests.post(ORDER_PATH, json=payload)
        assert create_response.status_code == 201
        self.track = create_response.json()["track"]

        response = requests.get(ORDER_PATH)
        assert response.status_code == 200
        assert "orders" in response.json()
        assert isinstance(response.json()["orders"], list)
        assert len(response.json()["orders"]) > 0