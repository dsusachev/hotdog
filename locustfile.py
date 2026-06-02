import random

from locust import HttpUser, between, task


class HotdogUser(HttpUser):
    wait_time = between(1, 3)  # пауза между запросами 1-3 секунды

    def on_start(self):
        """При старте создаём уникального пользователя и логинимся"""
        self.email = f"user_{random.randint(1000, 999999)}@example.com"
        self.password = "secret123"
        # Регистрация
        resp = self.client.post(
            "/api/auth/register",
            json={
                "email": self.email,
                "password": self.password,
                "display_name": "Load Test User",
            },
        )
        if resp.status_code == 200:
            self.user_id = resp.json().get("id")
        elif resp.status_code == 400 and "Email already registered" in resp.text:
            # Может быть, если случайно повторили – пробуем логин
            pass
        # Логин
        resp = self.client.post(
            "/api/auth/login", json={"email": self.email, "password": self.password}
        )
        if resp.status_code == 200:
            self.token = resp.json().get("access_token")
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def health(self):
        """Проверка здоровья – частая операция"""
        self.client.get("/health")

    @task(1)
    def get_root(self):
        """Проверка корневого эндпоинта (если есть)"""
        self.client.get("/")

    @task(1)
    def login_again(self):
        """Повторный логин для теста"""
        self.client.post(
            "/api/auth/login", json={"email": self.email, "password": self.password}
        )

    @task(1)
    def register_duplicate(self):
        """Попытка зарегистрировать существующего пользователя – должна вернуть 400"""
        self.client.post(
            "/api/auth/register",
            json={
                "email": self.email,
                "password": self.password,
                "display_name": "Duplicate",
            },
        )

    def on_stop(self):
        """При остановке пользователя можно что-то сделать (опционально)"""
        pass
