# 🧪 PharmaSim — 药物研发全流程模拟平台

> **从靶点到上市，AI 驱动的药物研发全生命周期模拟**

PharmaSim 是一个端到端的药物研发模拟平台，覆盖从靶点发现到上市后监测的完整流程。通过多智能体协作与蒙特卡洛模拟，帮助研发团队在投入真实资源之前评估管线可行性、优化决策路径、量化项目风险。

---

## ✨ 核心功能

| # | 功能模块 | 说明 |
|---|---------|------|
| 1 | 🎯 靶点发现模拟 | 基于基因组学与蛋白组学数据，AI 筛选潜在药物靶点并评估可成药性 |
| 2 | 💊 先导化合物优化 | 虚拟合成 + ADMET 预测，多轮迭代优化先导化合物 |
| 3 | 🔬 临床前研究模拟 | 药效动力学、毒理学、药代动力学的 in silico 模拟 |
| 4 | 📋 临床试验设计 | I/II/III 期试验方案设计、样本量计算、终点选择与适应性设计 |
| 5 | 📑 监管审批模拟 | FDA/NMPA/EMA 审批流程模拟，资料完整性检查 |
| 6 | 📊 上市后监测 | IV 期临床与真实世界数据（RWD）分析模拟 |
| 7 | 💰 成本效益分析 | 药物经济学评估，ICER 计算，预算影响分析 |
| 8 | ⚠️ 风险评估 | 全流程蒙特卡洛模拟，量化技术、市场、监管风险 |

---

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    PharmaSim Platform                    │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Frontend    │  API Gateway │  Simulation  │  Data      │
│  (React)     │  (FastAPI)   │  Engine      │  Layer     │
├──────────────┼──────────────┼──────────────┼────────────┤
│ • 管线仪表盘  │ • REST API   │ • 多智能体   │ • SQLite   │
│ • 可视化面板  │ • WebSocket  │ • 蒙特卡洛   │ • JSON     │
│ • 报告导出    │ • 认证鉴权    │ • 事件驱动   │ • 缓存层   │
└──────────────┴──────────────┴──────────────┴────────────┘
```

### 核心组件

- **多智能体系统** (`src/agents/`) — 药理学、临床、流行病学、药物经济学等专家智能体协作决策
- **模拟引擎** (`src/simulation/`) — 交互引擎、社会网络模拟、仿真引擎
- **数据模型** (`engine/`) — 管线阶段、成功率、药物属性的结构化数据
- **API 服务** (`server.py`) — 基于 FastAPI 的后端服务

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+（前端开发）
- SQLite 3

### 安装

```bash
# 克隆仓库
git clone https://github.com/MoKangMedical/PharmaSim.git
cd PharmaSim

# 安装 Python 依赖
pip install -r requirements.txt

# 启动后端服务
python server.py
```

### 运行模拟

```python
from src.simulation.simulation_engine import SimulationEngine
from src.agents.agent_factory import AgentFactory

# 初始化模拟引擎
engine = SimulationEngine()

# 创建专家智能体
factory = AgentFactory()
agents = factory.create_team([
    "pharmacology", "clinical", "epidemiology",
    "pharmacoeconomics", "market"
])

# 运行药物研发管线模拟
result = engine.run_pipeline(
    drug_name="Compound-X",
    target="EGFR-T790M",
    indication="非小细胞肺癌",
    agents=agents,
    iterations=1000  # 蒙特卡洛迭代次数
)

print(f"综合成功率: {result.success_rate:.1%}")
print(f"预计研发成本: ${result.estimated_cost:,.0f}")
print(f"预计上市时间: {result.time_to_market} 年")
```

---

## 📁 项目结构

```
PharmaSim/
├── src/
│   ├── agents/          # 多智能体系统
│   │   ├── pharmacology_agent.py      # 药理学专家
│   │   ├── clinical_expert_agent.py   # 临床试验专家
│   │   ├── epidemiology_agent.py      # 流行病学专家
│   │   ├── pharmacoeconomics_agent.py # 药物经济学专家
│   │   ├── market_expert_agent.py     # 市场分析专家
│   │   └── agent_factory.py           # 智能体工厂
│   ├── simulation/      # 模拟引擎
│   │   ├── simulation_engine.py       # 核心仿真引擎
│   │   ├── interaction_engine.py      # 智能体交互引擎
│   │   └── social_network.py          # 社会网络模拟
│   └── main.py
├── engine/              # 数据模型与种子数据
│   ├── model.py
│   ├── schema.py
│   ├── seed_data.py
│   └── data/pharmasim.db
├── data/                # 参考数据
│   ├── pipeline-stages.json   # 管线阶段定义
│   └── success-rates.json     # 历史成功率数据
├── docs/                # 文档
├── frontend/            # 前端界面
├── configs/             # 配置文件
└── server.py            # API 服务
```

---

## 🎯 应用场景

### 1. 制药企业 — 管线评估
在立项阶段快速评估新靶点/新分子的开发可行性，与历史数据对比，辅助 Go/No-Go 决策。

### 2. 投资机构 — 尽职调查
模拟目标公司管线的商业化前景，量化成功概率与预期回报，支持投资决策。

### 3. 学术研究 — 方法验证
作为药物研发方法学研究的沙盒环境，测试新的预测模型与优化算法。

### 4. 监管科学 — 政策评估
模拟不同监管政策对药物研发成功率和时间线的影响。

---

## 📊 数据来源

成功率与管线数据基于公开文献与行业报告：

- Clinical Development Success Rates (BIO/Informa, 2016–2024)
- DiMasi et al., *Journal of Health Economics*, 2016
- NMPA 年度药品审评报告
- FDA CDER 年度新药报告

---

## 🤝 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解开发规范与提交流程。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

<p align="center">
  <i>PharmaSim — 让药物研发决策更科学、更高效</i>
</p>
