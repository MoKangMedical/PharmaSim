# 💊 PharmaSim v3.0

> AI驱动的药品上市表现预测仿真平台 | 1000用户Agent社交网络交互 | 仿Aaru多智能体仿真

[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-blue)](https://mokangmedical.github.io/PharmaSim)
[![A2A Protocol](https://img.shields.io/badge/Protocol-A2A-green)](https://github.com/MoKangMedical/PharmaSim)
[![Agents](https://img.shields.io/badge/Agents-1801-brightgreen)](https://github.com/MoKangMedical/PharmaSim)

## 🎯 核心价值

传统药品上市预测需要 **3-6个月**、花费 **50-200万**，准确率仅60-70%。

PharmaSim 通过 **1801个多维度AI Agent** 仿真，将预测时间缩短至 **1天**，成本降低 **90%**，准确率提升至 **85%+**。

## 🤖 Agent矩阵 (1801个)

| Agent类型 | 数量 | 职责维度 |
|-----------|------|----------|
| 👨‍⚕️ 医生Agent | 400 | 处方决策行为模拟 |
| 🧑 患者Agent | 1000 | 用药决策+社交网络交互 |
| 💊 药物学专家 | 80 | 药理/毒理/药代动力学评估 |
| 📊 流行病学专家 | 80 | 疾病负担/人群分析 |
| 💰 药物经济学专家 | 80 | ICER/成本效果/预算影响 |
| 🏥 医保专家 | 40 | 准入/报销/DRG-DIP策略 |
| 🔬 临床专家 | 40 | 疗效/安全性/指南依从 |
| 💲 定价专家 | 40 | 价值定价/竞争定价/国际参考 |
| 📈 市场专家 | 40 | 竞争格局/渠道/商业化策略 |
| 🏛️ 医保支付方 | 1 | 医保局准入决策 |

## 🔬 Aaru式社交网络交互

仿照 [Aaru](https://aaru.com) 的多智能体仿真方法：

### 社交网络拓扑
- **Watts-Strogatz小世界网络**: 患者间通过社交关系连接
- **KOL枢纽节点**: 医生作为意见领袖影响患者群体
- **病友社区**: 同疾病患者形成信息社区
- **弱连接**: 专家信息通过社交网络传播

### 决策交互引擎
1. **意见初始化**: 基于个体属性(经济/信息源/疾病阶段)产生差异化意见
2. **影响力传播**: `影响强度 = 社交权重 × 信心差距 × 意见相似度 × 时间衰减`
3. **外部事件冲击**: 媒体报道、KOL推荐、病友反馈、医保谈判结果
4. **多轮协商**: 8轮迭代直至收敛
5. **涌现行为**: 群体决策从个体交互中涌现

### 权重匹配机制
```
个体决策 = 基础意愿 + 经济敏感度 × 价格因素 + 信息权重 × 疗效感知 
         + 疾病阶段加成 + 依从性影响 + 品牌偏好 + 随机噪声

社交协商后: 意愿 = 原意愿 × (1 - 学习率) + 邻居加权平均 × 学习率
学习率 = max(0.08, 0.35 - 信心度 × 0.4) × 异质冲击系数
```

## 🏗️ 项目结构

```
PharmaSim/
├── src/
│   ├── agents/                    # Agent模块 (10种专业Agent)
│   │   ├── agent_factory.py       # 1800 Agent工厂
│   │   ├── doctor_agent.py        # 医生Agent
│   │   ├── patient_agent.py       # 患者Agent
│   │   ├── payer_agent.py         # 医保支付方
│   │   ├── pharmacology_agent.py  # 药物学专家
│   │   ├── epidemiology_agent.py  # 流行病学专家
│   │   ├── pharmacoeconomics_agent.py  # 药物经济学专家
│   │   ├── insurance_expert_agent.py   # 医保专家
│   │   ├── clinical_expert_agent.py    # 临床专家
│   │   ├── pricing_expert_agent.py     # 定价专家
│   │   └── market_expert_agent.py      # 市场专家
│   ├── simulation/                # 仿真引擎
│   │   ├── simulation_engine.py   # 核心仿真引擎 v3.0
│   │   ├── social_network.py      # 社交网络拓扑
│   │   └── interaction_engine.py  # 决策交互引擎
│   └── main.py                    # 主入口
├── docs/                          # GitHub Pages 站点
├── configs/config.yaml            # 配置文件
├── data/                          # 模拟数据
└── server.py                      # FastAPI后端
```

## ⚡ 快速开始

```bash
# 克隆项目
git clone https://github.com/MoKangMedical/PharmaSim.git
cd PharmaSim

# 运行仿真
cd src
python main.py
```

## 🔗 A2A 协议集成

PharmaSim 实现了 A2A (Agent-to-Agent) 协议，支持：
- **Agent 发现**: 通过 `/api/a2a/discovery` 发现可用 Agent
- **消息传递**: Agent 间通过标准化消息通信
- **任务协作**: 多 Agent 协同完成复杂模拟任务

## 📊 Demo

访问 [GitHub Pages Demo](https://mokangmedical.github.io/PharmaSim) 查看在线演示。

## 📝 许可证

MIT License © 2026 MoKangMedical

## 📐 理论基础

> **Harness理论**：在AI领域，Harness（环境设计）比模型本身更重要。使性能提升64%。

> **红杉论点**：从卖工具到卖结果。
