from locust import HttpUser, between, task


class InferenceUser(HttpUser):
    wait_time = between(0.1, 0.5)  # 每个用户请求间隔0.1-0.5秒

    @task
    def predict(self):
        payload = {
            "session_duration": 300,
            "product_views": 8,
            "cart_adds": 2,
            "past_purchases": 3,
            "member_level": 2,
            "device_type": 1,
        }
        self.client.post("/predict", json=payload)

    @task(3)  # 权重3，表示执行频率是上面的3倍
    def health_check(self):
        self.client.get("/health")

    @task
    def batch_predict(self):
        """批量预测压测"""
        payload = {
            "samples": [
                {
                    "session_duration": 300,
                    "product_views": 8,
                    "cart_adds": 2,
                    "past_purchases": 3,
                    "member_level": 2,
                    "device_type": 1,
                },
                {
                    "session_duration": 120,
                    "product_views": 3,
                    "cart_adds": 0,
                    "past_purchases": 1,
                    "member_level": 1,
                    "device_type": 0,
                },
            ]
        }
        self.client.post("/predict/batch", json=payload)
