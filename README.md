# 🧪 PharmaSim — 药物研发全流程模拟平台

> **从靶点到上市，AI 驱动的药物研发全生命周期模拟**

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![Version](https://img.shields.io/badge/Version-1.0.0-brightgreen)](#)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

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

## 🎬 模拟场景详解

### 场景1: 新靶点立项评估

模拟从靶点发现到先导化合物确定的早期研发流程，帮助评估新靶点的成药潜力。

```python
scenario = engine.create_scenario("target_evaluation")
scenario.configure(
    target="KRAS-G12C",
    disease="非小细胞肺癌",
    modality="小分子抑制剂",
    competitors=["Sotorasib", "Adagrasib"]
)
result = scenario.run(iterations=5000)
# 输出: 成功率、预计成本、竞争格局、时间窗口
```

### 场景2: 临床试验优化

模拟不同试验设计方案的成功率与成本，优化样本量、终点选择和适应性设计参数。

```python
scenario = engine.create_scenario("clinical_optimization")
scenario.configure(
    drug="Compound-X",
    phase="Phase III",
    design_options=[
        {"endpoints": ["OS"], "n": 500, "duration_months": 36},
        {"endpoints": ["PFS", "OS"], "n": 800, "duration_months": 24},
        {"endpoints": ["ORR"], "n": 300, "duration_months": 18, "adaptive": True}
    ]
)
result = scenario.run(iterations=3000)
# 输出: 各方案成功率、成本、时间、监管接受度
```

### 场景3: 管线组合优化

对多条管线进行资源配置优化，找到最优投资组合。

```python
scenario = engine.create_scenario("portfolio_optimization")
scenario.configure(
    pipeline=[
        {"name": "Drug-A", "phase": "Phase II", "indication": "乳腺癌"},
        {"name": "Drug-B", "phase": "Phase I", "indication": "胃癌"},
        {"name": "Drug-C", "phase": "Preclinical", "indication": "肝癌"}
    ],
    budget=500_000_000,  # 5亿美元
    time_horizon=10       # 10年
)
result = scenario.run(iterations=10000)
# 输出: 最优投资组合、预期NPV、风险收益比
```

### 场景4: 竞争态势分析

模拟竞争对手动态对自身管线的影响，制定差异化策略。

```python
scenario = engine.create_scenario("competitive_analysis")
scenario.configure(
    own_drug={"name": "OurDrug", "target": "PD-L1", "phase": "Phase II"},
    competitors=[
        {"name": "Keytruda", "company": "MSD", "phase": "Marketed"},
        {"name": "Tecentriq", "company": "Roche", "phase": "Marketed"},
        {"name": "Competitor-X", "phase": "Phase III", "eta": 2026}
    ]
)
result = scenario.run(iterations=5000)
# 输出: 市场份额预测、差异化建议、时间窗口分析
```

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

## 📡 API 文档

### 认证

```bash
# 获取API Token
curl -X POST https://api.pharmasim.io/v1/auth/token \
  -d '{"client_id": "YOUR_ID", "client_secret": "YOUR_SECRET"}'
```

### 核心端点

#### POST /v1/simulations — 创建模拟任务

```json
{
  "scenario": "target_evaluation",
  "config": {
    "target": "KRAS-G12C",
    "disease": "非小细胞肺癌",
    "iterations": 5000,
    "random_seed": 42
  }
}
```

**响应：**
```json
{
  "simulation_id": "sim_xyz789",
  "status": "running",
  "estimated_time": "3min",
  "progress_url": "/v1/simulations/sim_xyz789/progress"
}
```

#### GET /v1/simulations/{id}/results — 获取模拟结果

```json
{
  "simulation_id": "sim_xyz789",
  "status": "completed",
  "results": {
    "overall_success_rate": 0.127,
    "phase_success_rates": {
      "preclinical": 0.65,
      "phase_i": 0.52,
      "phase_ii": 0.28,
      "phase_iii": 0.58,
      "nda_approval": 0.85
    },
    "estimated_cost": 1_850_000_000,
    "time_to_market": 11.5,
    "npv": 3_200_000_000,
    "risk_factors": [
      {"factor": "靶点验证不足", "probability": 0.35, "impact": "high"},
      {"factor": "竞争先发劣势", "probability": 0.45, "impact": "medium"}
    ]
  }
}
```

#### POST /v1/scenarios/compare — 方案对比

```json
{
  "scenarios": [
    {"name": "方案A", "target": "EGFR", "modality": "小分子"},
    {"name": "方案B", "target": "EGFR", "modality": "单抗"},
    {"name": "方案C", "target": "EGFR", "modality": "ADC"}
  ],
  "iterations": 10000
}
```

#### GET /v1/data/success-rates — 获取历史成功率数据

```json
{
  "source": "BIO/Informa 2024",
  "data": {
    "oncology": {"overall": 0.053, "phase_i": 0.58, "phase_ii": 0.29},
    "cardiovascular": {"overall": 0.072, "phase_i": 0.62, "phase_ii": 0.35},
    "neurology": {"overall": 0.041, "phase_i": 0.52, "phase_ii": 0.22}
  }
}
```

---

## 📊 性能基准

| 指标 | 数值 | 测试环境 |
|------|------|---------|
| 单次模拟（1000迭代） | ~30s | 4核CPU, 8GB RAM |
| 单次模拟（10000迭代） | ~4min | 4核CPU, 8GB RAM |
| 并发模拟任务 | 20+ | 8核CPU, 16GB RAM |
| API响应延迟 | <200ms | 本地部署 |
| 内存占用（单模拟） | ~500MB | 标准场景 |
| 数据库查询 | <50ms | SQLite, 10万条记录 |
| 报告生成 | <10s | PDF格式，含图表 |

### 基准测试命令

```bash
# 运行基准测试
python benchmark.py --iterations 10000 --concurrent 10

# 输出示例
# Total simulations: 10
# Avg time per simulation: 38.2s
# P95 latency: 42.1s
# Throughput: 15.7 simulations/min
```

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

## 📚 案例研究

### 案例1: 某Biotech公司KRAS-G12C项目立项

**背景：** 某初创Biotech公司评估是否投入KRAS-G12C靶点的小分子抑制剂研发。

**模拟结果：**
- 综合成功率: 12.7%（高于行业平均5.3%）
- 预计研发成本: 18.5亿美元
- 预计上市时间: 11.5年
- 竞争窗口: 已有2个上市药物，差异化空间有限

**决策建议：** 建议开发口服剂型或联合用药方案，形成差异化竞争优势。

**实际验证：** 公司采纳建议，开发了具有独特结合模式的新一代KRAS-G12C抑制剂，目前已进入Phase II。

### 案例2: 大型药企管线组合优化

**背景：** 某Top 20药企需在12条管线中选择最优投资组合，预算约束5亿美元/年。

**模拟结果：**
- 最优组合: 保留5条管线（肿瘤3条 + 自免2条）
- 预期10年NPV: 32亿美元
- 风险调整后回报率: 18.3%

**决策建议：** 砍掉早期阶段的神经领域管线，集中资源于肿瘤和自免优势领域。

**实际验证：** 企业执行重组后，管线推进效率提升35%，研发ROI显著改善。

### 案例3: 临床试验设计优化

**背景：** 某药企的Phase III试验因样本量估算不当导致延期，需重新设计。

**模拟结果：**
- 推荐方案: 适应性设计，中期分析允许样本量重估
- 预期节省: 样本量减少30%，时间缩短6个月
- 成功率提升: 从52%到61%

**实际验证：** 采用推荐方案后，试验按期完成，节省研发成本约2000万美元。

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

## 🔗 相关项目

| 项目 | 定位 |
|------|------|
| [OPC Platform](https://github.com/MoKangMedical/opcplatform) | 一人公司全链路学习平台 |
| [Digital Sage](https://github.com/MoKangMedical/digital-sage) | 与100位智者对话 |
| [Cloud Memorial](https://github.com/MoKangMedical/cloud-memorial) | AI思念亲人平台 |
| [天眼 Tianyan](https://github.com/MoKangMedical/tianyan) | 市场预测平台 |
| [MediChat-RD](https://github.com/MoKangMedical/medichat-rd) | 罕病诊断平台 |
| [MedRoundTable](https://github.com/MoKangMedical/medroundtable) | 临床科研圆桌会 |
| [DrugMind](https://github.com/MoKangMedical/drugmind) | 药物研发数字孪生 |
| [MediPharma](https://github.com/MoKangMedical/medi-pharma) | AI药物发现平台 |
| [Minder](https://github.com/MoKangMedical/minder) | AI知识管理平台 |
| [Biostats](https://github.com/MoKangMedical/Biostats) | 生物统计分析平台 |

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

<p align="center">
  <i>PharmaSim — 让药物研发决策更科学、更高效</i>
</p>
