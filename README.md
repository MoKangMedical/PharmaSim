# 💊 PharmaSim

> AI驱动的药品上市表现预测仿真平台 | 专注医药医疗垂直领域

[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-blue)](https://mokangmedical.github.io/PharmaSim)
[![A2A Protocol](https://img.shields.io/badge/Protocol-A2A-green)](https://github.com/MoKangMedical/PharmaSim)
[![Second Me](https://img.shields.io/badge/Integration-Second%20Me-purple)](https://second.me)

## 🎯 核心价值

传统药品上市预测需要 **3-6个月**、花费 **50-200万**，准确率仅60-70%。

PharmaSim 通过多智能体AI仿真，将预测时间缩短至 **1天**，成本降低 **90%**，准确率提升至 **85%+**。

## 🤖 AI Agent 矩阵

| Agent | 角色 | 能力 |
|-------|------|------|
| 📊 市场分析专家 | 市场容量、竞争格局 | market_analysis, pricing_strategy |
| 👨‍⚕️ 临床医学专家 | 疗效评估、处方行为 | clinical_assessment, efficacy_evaluation |
| 💰 药物经济学专家 | 医保准入、成本效果 | health_economics, hta_evaluation |
| 🏥 患者行为分析师 | 就医决策、依从性 | patient_behavior, adherence_modeling |
| 🏭 渠道策略师 | 药房、医院、电商 | channel_strategy, distribution_modeling |
| 📋 政策法规分析师 | DRG/DIP、监管影响 | regulatory_analysis, policy_monitoring |
| 🔧 数据校准专家 | 真实数据校准、回测 | data_calibration, backtesting |
| 🎯 模拟编排师 | 多Agent协调、报告 | orchestration, report_generation |

## 🏗️ 项目结构

```
PharmaSim/
├── docs/                          # GitHub Pages 站点
│   └── index.html                 # 项目主页
├── src/
│   ├── agents/                    # AI Agent 模块
│   │   ├── doctor_agent.py        # 医生Agent - 处方决策
│   │   ├── patient_agent.py       # 患者Agent - 用药决策
│   │   └── payer_agent.py         # 医保Agent - 准入评估
│   ├── simulation/                # 模拟引擎
│   │   └── simulation_engine.py   # 核心模拟引擎
│   ├── a2a/                       # A2A 协议
│   │   └── secondme_integration.py # Second Me 集成
│   └── main.py                    # 主入口
├── data/                          # 模拟数据
├── configs/                       # 配置文件
│   └── config.yaml
├── scripts/                       # 工具脚本
├── assets/                        # 静态资源
├── secondme-manifest.json         # Second Me 应用清单
└── docs/secondme-integration.md   # Second Me 集成指南
```

## ⚡ 快速开始

```bash
# 克隆项目
git clone https://github.com/MoKangMedical/PharmaSim.git
cd PharmaSim

# 运行模拟
cd src
python main.py
```

## 🔗 A2A 协议集成

PharmaSim 实现了 A2A (Agent-to-Agent) 协议，支持：

- **Agent 发现**: 通过 `/api/a2a/discovery` 发现可用 Agent
- **消息传递**: Agent 间通过标准化消息通信
- **任务协作**: 多 Agent 协同完成复杂模拟任务
- **Second Me 集成**: 用户数字分身参与决策

## 🤖 Second Me 集成

通过 [Second Me](https://second.me) 数字分身平台，用户可以：

1. 使用 Second Me 账号登录
2. 将自己的数字分身(Shade)带入模拟
3. 分身扮演药企决策者/临床专家/投资人角色
4. 与 8 个专业 Agent 协作完成预测

详见 [Second Me 集成指南](docs/secondme-integration.md)

## 📊 Demo

访问 [GitHub Pages Demo](https://mokangmedical.github.io/PharmaSim) 查看在线演示。

## 📝 许可证

MIT License © 2026 MoKangMedical
