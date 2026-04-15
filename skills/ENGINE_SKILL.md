---
name: pharmasim-simulation-engine
description: PharmaSim药物上市决策模拟引擎 — 多Agent协同模拟市场环境，输出7维度专家评估报告
version: 3.4.0
category: simulation
triggers:
  - 药物模拟
  - drug simulation
  - 市场预测
  - 上市决策
  - 仿真分析
author: PharmaSim Team
test_prompts:
  - "模拟pembrolizumab在中国市场的上市策略"
  - "评估PD-L1抑制剂的商业可行性"
---

# PharmaSim: 药物上市决策模拟引擎

## 输入格式
```json
{
  "drug_name": "Pembrolizumab",
  "indication": "非小细胞肺癌",
  "market": "china",
  "pricing_strategy": "premium",
  "competitors": ["Nivolumab", "Atezolizumab", "Durvalumab"]
}
```

## 工作流程

### Step 1: 加载药品数据
```python
# 数据源: ~/Desktop/PharmaSim/data/drugs.json
drug = load_drug("pembrolizumab")  # 14个FDA药品数据
# 返回: 适应症、定价、竞品、临床数据
```

参考文件: `~/Desktop/PharmaSim/data/drugs.json`

### Step 2: 配置市场参数
通过 `~/Desktop/PharmaSim/configs/market_params.yaml` 配置：
```yaml
china:
  population: 1400000000
  lung_cancer_incidence: 820000  # 年新发病例
  insurance_coverage: 0.65
  avg_treatment_cost: 150000  # RMB/year
  regulatory_timeline_months: 18
```

⚠️ **确认检查点**: 参数配置后展示摘要，等用户确认再运行模拟。

### Step 3: 运行多Agent模拟
8个Agent并行评估，参考 `~/Desktop/PharmaSim/engine/agents/`:

| Agent | 职责 | 输出 |
|-------|------|------|
| MarketAnalyst | 市场规模、增长预测 | TAM/SAM/SOM |
| RegulatoryExpert | 审批路径、时间线 | 审批概率、预计时间 |
| ClinicalExpert | 临床价值评估 | 疗效评分、安全性评分 |
| BusinessStrategist | 商业模式、收入预测 | 5年收入曲线 |
| CompetitionAnalyst | 竞品分析 | 市场份额预测 |
| PatientInsight | 患者需求、支付意愿 | 患者获益评分 |
| PricingExpert | 定价策略 | 最优价格区间 |
| RiskAssessor | 综合风险 | 风险矩阵 |

### Step 4: 生成7维度评估
```json
{
  "market_opportunity": {"score": 85, "confidence": 0.9, "detail": "..."},
  "regulatory_feasibility": {"score": 72, "confidence": 0.85, "detail": "..."},
  "clinical_value": {"score": 91, "confidence": 0.95, "detail": "..."},
  "commercial_viability": {"score": 78, "confidence": 0.8, "detail": "..."},
  "competitive_landscape": {"score": 65, "confidence": 0.75, "detail": "..."},
  "patient_benefit": {"score": 88, "confidence": 0.9, "detail": "..."},
  "overall_risk": {"score": 35, "confidence": 0.85, "detail": "..."}
}
```

### Step 5: 输出决策建议
```json
{
  "recommendation": "CONDITIONAL_GO",
  "confidence": 0.82,
  "key_success_factors": ["医保谈判成功", "差异化定位"],
  "main_risks": ["竞品先发优势", "定价压力"],
  "action_items": ["启动NMPA沟通", "制定医保策略"]
}
```

## 异常处理

| 场景 | 处理方式 |
|------|----------|
| 数据库连接失败 | 使用 `~/Desktop/PharmaSim/data/cache/` 缓存数据 |
| Agent超时(>60s) | 降级为3-Agent快速评估 |
| Agent结果不一致 | 触发仲裁Agent，取中位数 |
| 药品不在数据库 | 提示用户手动输入关键参数 |

## 确认检查点
1. ⚠️ 参数配置后确认
2. ⚠️ 模拟开始前确认预算(计算资源)
3. ⚠️ 结果生成后等待确认再展示详情
4. ⚠️ 导出报告前确认格式和语言

## 实测用例

### 测试1: Pembrolizumab中国市场
**输入**: `{"drug": "Pembrolizumab", "market": "china"}`
**期望**: 7维度评分均>60，recommendation为GO或CONDITIONAL_GO

### 测试2: 未知药物
**输入**: `{"drug": "UnknownDrug123"}`
**期望**: 提示用户输入参数，走手动配置流程
