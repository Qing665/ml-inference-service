import sys  # noqa: E402
from pathlib import Path  # noqa: E402

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).parent.parent))  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


# 关键修改：使用 fixture 确保 lifespan 完整执行
@pytest.fixture(scope="module")
def client():
    """创建测试客户端，确保 lifespan 完整执行"""
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_predict_endpoint(client):
    """测试单条预测"""
    payload = {
        "session_duration": 300,
        "product_views": 8,
        "cart_adds": 2,
        "past_purchases": 3,
        "member_level": 2,
        "device_type": 1,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "probability" in data
    assert data["prediction"] in [0, 1]
    assert 0 <= data["probability"] <= 1


def test_batch_predict(client):
    """测试批量预测"""
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
                "session_duration": 100,
                "product_views": 2,
                "cart_adds": 0,
                "past_purchases": 0,
                "member_level": 1,
                "device_type": 0,
            },
        ]
    }
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predictions" in data
    assert "probabilities" in data
    assert len(data["predictions"]) == 2


def test_invalid_input(client):
    """测试错误输入处理"""
    payload = {
        "session_duration": "not_a_number",  # 错误类型
        "product_views": 8,
        "cart_adds": 2,
        "past_purchases": 3,
        "member_level": 2,
        "device_type": 1,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422  # FastAPI 的验证错误码
