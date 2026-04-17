import time
from contextlib import asynccontextmanager
from pathlib import Path  # 移到顶部
from typing import List  # 删除 Optional，没用到

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

# 全局变量存放模型
model = None
feature_names = None


# 定义请求体结构
class PredictRequest(BaseModel):
    session_duration: float
    product_views: int
    cart_adds: int
    past_purchases: int
    member_level: int
    device_type: int


class BatchPredictRequest(BaseModel):
    samples: List[PredictRequest]


class PredictResponse(BaseModel):
    prediction: int
    probability: float
    inference_time_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool

    model_config = ConfigDict(protected_namespaces=())


# 应用生命周期管理：启动时加载模型
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    global model, feature_names

    # 获取项目根目录（app 的上一级）
    root_dir = Path(__file__).parent.parent

    model_path = root_dir / "model" / "xgb_model.pkl"
    feature_path = root_dir / "model" / "feature_names.txt"

    if model_path.exists():
        model = joblib.load(model_path)
        with open(feature_path, "r") as f:
            feature_names = f.read().strip().split(",")
        print(f"✅ 模型加载成功，特征列表: {feature_names}")
    else:
        print(f"⚠️ 警告：模型文件不存在于 {model_path}，请先运行 train_model.py")
        model = None

    yield

    # 关闭时执行
    print("服务关闭，清理资源")


app = FastAPI(title="ML Inference Service", version="1.0.0", lifespan=lifespan)


# 健康检查端点
@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", model_loaded=model is not None)


@app.get("/ready")
async def readiness_check():
    """就绪探针：检查模型是否已加载"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "ready"}


# 单条预测
@app.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    start_time = time.time()

    # 按特征顺序构造输入
    features = np.array(
        [
            [
                request.session_duration,
                request.product_views,
                request.cart_adds,
                request.past_purchases,
                request.member_level,
                request.device_type,
            ]
        ]
    )

    # 预测
    proba = model.predict_proba(features)[0, 1]
    pred = int(proba > 0.5)

    inference_time = (time.time() - start_time) * 1000

    return PredictResponse(
        prediction=pred, probability=float(proba), inference_time_ms=inference_time
    )


# 批量预测
@app.post("/predict/batch")
async def batch_predict(request: BatchPredictRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(request.samples) == 0:
        return {"predictions": []}

    start_time = time.time()

    features = np.array(
        [
            [
                s.session_duration,
                s.product_views,
                s.cart_adds,
                s.past_purchases,
                s.member_level,
                s.device_type,
            ]
            for s in request.samples
        ]
    )

    probas = model.predict_proba(features)[:, 1]
    preds = (probas > 0.5).astype(int)

    inference_time = (time.time() - start_time) * 1000

    return {
        "predictions": preds.tolist(),
        "probabilities": probas.tolist(),
        "inference_time_ms": inference_time,
        "count": len(request.samples),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # 生产环境关闭热重载
        workers=1,  # 先在单 worker 下测试
    )
