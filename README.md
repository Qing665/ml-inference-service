================================================================================
                    ML Inference Service - MLOps 实践项目
================================================================================

项目简介
--------------------------------------------------------------------------------
面向电商用户行为预测场景的生产级机器学习推理服务，完整实现从模型训练、
测试、容器化到 CI/CD 自动化的 MLOps 全流程。


技术栈
--------------------------------------------------------------------------------
API 框架        FastAPI + Uvicorn
机器学习        XGBoost + scikit-learn
容器化          Docker 多阶段构建
CI/CD           GitHub Actions
代码质量        pytest + pre-commit
服务编排        Docker Compose


核心指标
--------------------------------------------------------------------------------
指标                数值              实现方式
------------------------------------------------------------------------
推理 QPS            200+              FastAPI 异步 + 4 workers
镜像体积            ~440MB            多阶段构建，压缩 40%
服务恢复时间        < 5 秒            健康检查 + 自动重启
测试覆盖率          85%               pytest + 边界条件测试
迭代周期            2-3 分钟          GitHub Actions 全自动


项目结构
--------------------------------------------------------------------------------
ml-inference-service/
    app/
        main.py              FastAPI 推理服务
    tests/
        test_api.py          单元测试
    .github/workflows/
        mlops-pipeline.yml   CI/CD 流水线配置
    train_model.py           模型训练脚本
    Dockerfile               多阶段构建配置
    docker-compose.yml       服务编排配置
    requirements.txt         项目依赖
    locustfile.py            压测脚本


CI/CD 流水线
--------------------------------------------------------------------------------
代码推送 -> Lint检查 -> 模型训练 -> 单元测试 -> Docker构建 -> 模拟部署
   |           |           |           |            |            |
   v           v           v           v            v            v
 触发      pre-commit   XGBoost     pytest      多阶段构建   制品输出
           + flake8     训练        85%覆盖      440MB


快速开始
--------------------------------------------------------------------------------
1. 训练模型
   python train_model.py

2. 启动服务
   docker-compose up -d

3. 测试接口
   curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"session_duration\":300,\"product_views\":8,\"cart_adds\":2,\"past_purchases\":3,\"member_level\":2,\"device_type\":1}"

4. 查看 API 文档
   浏览器访问 http://localhost:8000/docs

5. 压测验证
   pip install locust
   locust -f locustfile.py --host=http://localhost:8000
   浏览器访问 http://localhost:8001 设置并发数


关键技术实现
--------------------------------------------------------------------------------
1. 多阶段构建 (镜像压缩 40%)
   - 阶段一：安装 gcc 编译工具，pip install 生成依赖
   - 阶段二：仅复制运行时库 (libgomp1) 和编译好的包
   - 效果：733MB -> 440MB

2. 高可用保障
   - lifespan 上下文管理器：模型单例加载，多 worker 共享
   - HEALTHCHECK 指令：30 秒健康探测
   - restart: unless-stopped：异常自动重启

3. CI/CD 自动化
   - 触发条件：push 到 main 分支
   - 质量门禁：pre-commit 检查 + 85% 覆盖率
   - 制品输出：Docker 镜像 + 训练好的模型


面试要点
--------------------------------------------------------------------------------
- 能说清楚多阶段构建的原理和效果
- 能解释 FastAPI 异步与多 worker 的并发模型
- 能展示 GitHub Actions 的运行截图
- 能说明 pytest 覆盖率如何从 70% 提升到 85%
- 能对比传统手动流程 vs CI/CD 自动化的效率差异


相关链接
--------------------------------------------------------------------------------
GitHub 仓库    https://github.com/Qing665/ml-inference-service
Actions 状态   https://github.com/Qing665/ml-inference-service/actions


================================================================================
                                   MIT License
================================================================================