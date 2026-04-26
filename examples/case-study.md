# 📖 PharmaSim 案例研究：EGFR-TKI 第四代抑制剂管线评估

## 背景

**项目代号**: PHM-401
**靶点**: EGFR C797S 突变（第三代耐药突变）
**适应症**: 非小细胞肺癌（NSCLC）
**模态**: 小分子靶向药
**定位**: 解决奥希替尼（Osimertinib）耐药后的未满足临床需求

---

## 问题

制药公司 A 正在评估是否推进 PHM-401 进入临床前研究。已有的体外数据显示：

- PHM-401 对 EGFR C797S 突变的 IC50 = 8 nM（活性良好）
- 对野生型 EGFR 的选择性 >100 倍
- 口服生物利用度（大鼠）= 42%
- hERG IC50 > 30 μM（心血管安全性良好）
- Ames 试验阴性

**决策问题**: 是否值得投入 ~$15M 推进至 IND 申报？

---

## 模拟设置

### 候选分子参数

```python
from src.simulator import DrugCandidate, TherapeuticArea, Modality

candidate = DrugCandidate(
    name="PHM-401",
    target="EGFR-C797S",
    indication="奥希替尼耐药 NSCLC",
    therapeutic_area=TherapeuticArea.ONCOLOGY,
    modality=Modality.SMALL_MOLECULE,
    is_first_in_class=True,      # 首创机制
    has_biomarker=True,           # EGFR C797S 突变可作为伴随诊断
    ai_assisted=True,             # AI 辅助分子设计
    novelty_score=0.8,
)
```

### 运行模拟

```python
from src.simulator import SimulationEngine, print_report

engine = SimulationEngine()
result = engine.run(candidate, iterations=10000, seed=2026)
print_report(result)
```

---

## 模拟结果

### 总体指标

| 指标 | 数值 |
|------|------|
| 综合成功率（靶点→获批） | **8.7%** |
| 平均研发时间 | **9.8 年** |
| 中位研发成本 | **$423M** |
| P10-P90 成本区间 | $198M — $892M |

### 各阶段通过率

```
靶点发现     ████████████████░░░░  82.3%
苗头化合物   ██████████████░░░░░░  71.5%
先导化合物   ████████████░░░░░░░░  62.1%
临床前       ██████████████░░░░░░  70.8%
I 期临床     ███████████████░░░░░  74.6%
II 期临床    ████████░░░░░░░░░░░░  38.2%  ← 关键瓶颈
III 期临床   ████████████░░░░░░░░  58.4%
监管审批     █████████████████░░░  87.1%
```

### 关键发现

1. **II 期是最大瓶颈** — 38.2% 的通过率反映了肿瘤学 II→III 的高淘汰率
2. **AI 辅助 + 生物标志物加成** — 综合成功率从基线 5.2% 提升至 8.7%（+67%）
3. **First-in-class 风险** — 首创机制使成功率下降约 8%
4. **罕见突变优势** — C797S 突变患者群体较小，可能获得孤儿药认定加速

---

## 临床试验设计建议

基于模拟结果，建议采用以下试验策略：

### I 期：剂量递增 + 扩展队列

```python
from src.trial_design import TrialDesignEngine, TrialPhase, Endpoint, EndpointType

engine = TrialDesignEngine()

# I 期设计
phase1_endpoints = [
    Endpoint("DLT", EndpointType.PRIMARY, "剂量限制性毒性"),
    Endpoint("PK", EndpointType.PRIMARY, "药代动力学参数"),
    Endpoint("ORR", EndpointType.SECONDARY, "客观缓解率"),
]
# 预计 N=45, 18 个月, $28M
```

### II 期：单臂概念验证

- **主要终点**: ORR（客观缓解率）
- **目标**: ORR ≥ 30%（历史对照 ~15%）
- **预计样本量**: 80-100 例
- **预计时长**: 24 个月
- **预计成本**: $45M

### III 期：随机对照

```python
# 生存分析样本量
result = engine.calculate_sample_size_survival(
    median_control=10.0,      # 对照组中位 OS 10 个月
    median_treatment=14.0,    # 试验组预期 14 个月
    alpha=0.05,
    power=0.85,
)
# 预计 N ≈ 580, 42 个月, $180M
```

---

## 风险矩阵

| 风险类别 | 概率 | 影响 | 缓解策略 |
|---------|------|------|---------|
| II 期疗效不达预期 | 62% | 致命 | 前置 PoC 生物标志物验证 |
| 脱靶毒性 | 15% | 高 | 扩展安全药理学筛选 |
| 竞品先发（第四代 TKI） | 35% | 高 | 加速差异化设计 |
| C797S 患者入组困难 | 40% | 中 | 多区域多中心 + ctDNA 筛选 |
| 奥希替尼后续治疗格局变化 | 25% | 中 | 动态跟踪竞品管线 |

---

## 决策建议

### ✅ 推荐推进，但需满足以下前置条件

1. **确认体内药效** — 在 PDX 模型中验证 PHM-401 对 C797S 耐药肿瘤的抑瘤率 ≥ 60%
2. **完善 ADME 资料** — 解决大鼠清除率偏高问题（当前 CL = 45 mL/min/kg，目标 <30）
3. **竞品动态监控** — 密切关注 Blueprint/Novartis 的第四代 TKI 进展
4. **患者分层策略** — 开发 ctDNA-based C797S 伴随诊断试剂

### 预期回报

如果成功上市：
- 目标患者人群：奥希替尼耐药后 C797S 突变患者（约占 EGFR NSCLC 的 15-20%）
- 预期峰值年销售额：$1.2-2.5B
- 风险调整后 NPV：$380M
- 投资回报率（ROI）：2.1x

---

## 附录：敏感性分析

调整关键参数对综合成功率的影响：

| 参数调整 | 成功率变化 |
|---------|-----------|
| 基线 | 8.7% |
| 无 AI 辅助 | 6.1% (-30%) |
| 无生物标志物 | 7.2% (-17%) |
| 非 First-in-class | 9.4% (+8%) |
| 获得孤儿药认定 | 10.5% (+21%) |
| AI + 生物标志物 + 孤儿药 | 12.8% (+47%) |

---

*本案例由 PharmaSim v1.0 模拟生成，数据仅供参考，不构成实际投资或研发决策建议。*
