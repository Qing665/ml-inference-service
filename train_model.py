import os

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

# 创建 model 目录（如果不存在）
os.makedirs("model", exist_ok=True)

# 模拟电商用户行为数据
# 特征：浏览时长(秒)、浏览商品数、加购数、历史购买次数、会员等级、设备类型(0=mobile,1=pc)
np.random.seed(42)
n_samples = 10000

data = {
    "session_duration": np.random.exponential(180, n_samples),  # 平均3分钟
    "product_views": np.random.poisson(5, n_samples),
    "cart_adds": np.random.poisson(1, n_samples),
    "past_purchases": np.random.poisson(2, n_samples),
    "member_level": np.random.randint(0, 4, n_samples),
    "device_type": np.random.randint(0, 2, n_samples),
}

df = pd.DataFrame(data)

# 构造标签：是否购买（基于特征的非线性组合）
logits = (
    -2.0
    + 0.008 * df["session_duration"]
    + 0.3 * df["product_views"]
    + 0.8 * df["cart_adds"]
    + 0.5 * df["past_purchases"]
    + 0.4 * df["member_level"]
    - 0.1 * df["device_type"]
    + np.random.normal(0, 0.5, n_samples)
)
df["purchase"] = (1 / (1 + np.exp(-logits)) > 0.5).astype(int)

print(f"正样本比例: {df['purchase'].mean():.2%}")

# 划分训练集和测试集
X = df.drop("purchase", axis=1)
y = df["purchase"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 训练 XGBoost 模型
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=4,
    learning_rate=0.1,
    objective="binary:logistic",
    use_label_encoder=False,
    eval_metric="logloss",
    random_state=42,
)
model.fit(X_train, y_train)

# 评估
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"测试集准确率: {accuracy:.4f}")
print(classification_report(y_test, y_pred))

# 保存模型
joblib.dump(model, "model/xgb_model.pkl")
print("模型已保存至 model/xgb_model.pkl")

# 保存特征名称供推理使用
with open("model/feature_names.txt", "w") as f:
    f.write(",".join(X.columns.tolist()))
print("特征名称已保存")
