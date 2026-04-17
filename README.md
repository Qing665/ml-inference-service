\# ML 推理服务平台 - 端到端 MLOps 实践



\[!\[MLOps CI/CD Pipeline](https://github.com/Qing665/ml-inference-service/actions/workflows/ci-cd-pipeline.yml/badge.svg)](https://github.com/Qing665/ml-inference-service/actions/workflows/ci-cd-pipeline.yml)

\[!\[Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)](https://github.com/Qing665/ml-inference-service/actions)

\[!\[Docker Image Size](https://img.shields.io/badge/image%20size-\~280MB-blue)](https://github.com/Qing665/ml-inference-service)



\## 🎯 项目概述



面向电商用户行为预测场景的\*\*生产级机器学习推理服务\*\*，完整实现从模型训练、测试、容器化到 CI/CD 自动化的 MLOps 全流程。



\## ✨ 核心亮点



| 维度 | 实现 | 数据指标 |

|------|------|----------|

| \*\*高并发推理\*\* | FastAPI + uvicorn 多 worker | QPS 200+ |

| \*\*容器化优化\*\* | Docker 多阶段构建 | 镜像压缩 40% |

| \*\*高可用保障\*\* | 健康检查 + 自动重启 | 恢复时间 < 5s |

| \*\*自动化流水线\*\* | GitHub Actions CI/CD | 迭代周期 30min |

| \*\*代码质量\*\* | pytest + pre-commit | 覆盖率 85% |



\## 🏗️ 架构设计

┌─────────────────────────────────────────────────────────────┐

│ GitHub Actions CI/CD │

│ ┌──────┐ ┌───────┐ ┌──────┐ ┌────────┐ ┌────────┐ │

│ │ Lint │→│ Train │→│ Test │→│ Build │→│ Deploy │ │

│ └──────┘ └───────┘ └──────┘ └────────┘ └────────┘ │

└─────────────────────────────────────────────────────────────┘

↓

┌─────────────────────────────────────────────────────────────┐

│ Docker Container │

│ ┌─────────────────────────────────────────────────────┐ │

│ │ FastAPI Inference Service │ │

│ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │ │

│ │ │ Worker1 │ │ Worker2 │ │ Worker3 │ │Worker4 │ │ │

│ │ └─────────┘ └─────────┘ └─────────┘ └────────┘ │ │

│ │ ↑ │ │

│ │ XGBoost Model (单例加载) │ │

│ └─────────────────────────────────────────────────────┘ │

│ Health Check (30s) │

│ Auto Restart (always) │

└─────────────────────────────────────────────────────────────┘



\## 📦 快速开始



\### 本地运行

```bash

\# 1. 训练模型

python train\_model.py



\# 2. 启动服务

docker-compose up -d



\# 3. 测试接口

curl -X POST http://localhost:8000/predict \\

&#x20; -H "Content-Type: application/json" \\

&#x20; -d '{"session\_duration":300,"product\_views":8,"cart\_adds":2,"past\_purchases":3,"member\_level":2,"device\_type":1}'

