---
name: pharmasim-engine
description: PharmaSim药物上市决策模拟引擎 — 14个FDA药品数据，7维度×28子维度决策模型，多Agent市场仿真
version: 3.4.0
category: simulation
triggers:
  - 药物模拟
  - drug simulation
  - 市场预测
  - 上市决策
  - 仿真分析
test_prompts:
  - "模拟pembrolizumab在中国市场的上市策略"
author: PharmaSim Team
---

# PharmaSim: 药物上市决策模拟引擎

## 输入格式
```json
{
  "drug_name": "Pembrolizumab",
  "indication": "非小细胞肺癌",
  "market": "china",
  "pricing_strategy": "premium"
}
```

## 工作流程

### Step 1: 加载药品数据
从 `~/Desktop/PharmaSim/data/drugs.json` 加载14个FDA药品。

### Step 2: 配置市场参数
从 `~/Desktop/PharmaSim/configs/market_params.yaml` 读取。

⚠️ **确认检查点**: 参数确认后再运行。

### Step 3: 多Agent并行评估
8个Agent: 市场分析/监管/临床/商业/竞争/患者/定价/风险。

### Step 4: 输出7维度评估
市场机会/监管可行性/临床价值/商业可行性/竞争态势/患者获益/综合风险。

## 异常处理
| 场景 | 处理方式 |
|------|----------|
| 数据库连接失败 | 使用缓存数据 |
| Agent超时 | 降级为3-Agent快速评估 |
| 结果不一致 | 触发仲裁Agent |

## 参考文件
- 引擎: `~/Desktop/PharmaSim/engine/`
- 数据: `~/Desktop/PharmaSim/data/`
- 前端: `~/Desktop/PharmaSim/frontend/`
