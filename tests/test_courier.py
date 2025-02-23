import allure
import pytest
import requests
from .configuration import COURIER_PATH, COURIER_LOGIN_PATH
from .helpers import register_new_courier_and_return_login_password, generate_random_string

@allure.feature('Курьер')
class TestCourier:
    def setup_method(self):
        self.courier_id = None

    def teardown_method(self):
        if self.courier_id:
            requests.delete(f"{COURIER_PATH}/{self.courier_id}")

    @allure.title('Успешное создание курьера')
    def test_create_courier_success(self):
        courier_data = register_new_courier_and_return_login_password()
        assert len(courier_data) > 0, "Courier creation failed"
        
        login_response = requests.post(COURIER_LOGIN_PATH, 
            json={"login": courier_data[0], "password": courier_data[1]})
        self.courier_id = login_response.json()["id"]

    @allure.title('Невозможно создать двух одинаковых курьеров')
    def test_cannot_create_duplicate_courier(self):
        login = generate_random_string(10)
        password = generate_random_string(10)
        first_name = generate_random_string(10)
        
        payload = {
            "login": login,
            "password": password,
            "firstName": first_name
        }
        
        response = requests.post(COURIER_PATH, json=payload)
        assert response.status_code == 201
        
        login_response = requests.post(COURIER_LOGIN_PATH, 
            json={"login": login, "password": password})
        self.courier_id = login_response.json()["id"]
        
        response = requests.post(COURIER_PATH, json=payload)
        assert response.status_code == 409
        assert "этот логин уже используется" in response.json()["message"].lower()

    @allure.title('Невозможно создать курьера без обязательных полей')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_cannot_create_courier_without_required_field(self, missing_field):
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10),
            "firstName": generate_random_string(10)
        }
        
        del payload[missing_field]
        response = requests.post(COURIER_PATH, json=payload)
        assert response.status_code == 400

    @allure.title('Успешная авторизация курьера')
    def test_courier_login_success(self):
        courier_data = register_new_courier_and_return_login_password()
        assert len(courier_data) > 0
        
        payload = {
            "login": courier_data[0],
            "password": courier_data[1]
        }
        
        response = requests.post(COURIER_LOGIN_PATH, json=payload)
        assert response.status_code == 200
        assert "id" in response.json()
        
        self.courier_id = response.json()["id"]

    @allure.title('Невозможно авторизоваться с неверными учетными данными')
    def test_cannot_login_with_wrong_credentials(self):
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10)
        }
        
        response = requests.post(COURIER_LOGIN_PATH, json=payload)
        assert response.status_code == 404
        assert "учетная запись не найдена" in response.json()["message"].lower()

    @allure.title('Невозможно авторизоваться без обязательных полей')
    @pytest.mark.parametrize('missing_field', ['login', 'password'])
    def test_cannot_login_without_required_field(self, missing_field):
        payload = {
            "login": generate_random_string(10),
            "password": generate_random_string(10)
        }
        
        del payload[missing_field]
        response = requests.post(COURIER_LOGIN_PATH, json=payload)
        assert response.status_code in [400, 504]