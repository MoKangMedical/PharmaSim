"""
PharmaSim — 临床试验设计模块

提供 I/II/III 期临床试验的设计工具，包括：
- 样本量计算
- 终点选择建议
- 适应性设计方案
- 统计功效分析
- 入排标准建议
"""

import math
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class TrialPhase(Enum):
    """临床试验阶段"""
    PHASE_1 = "phase1"
    PHASE_1_2 = "phase1_2"
    PHASE_2 = "phase2"
    PHASE_2_3 = "phase2_3"
    PHASE_3 = "phase3"


class EndpointType(Enum):
    """终点类型"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    EXPLORATORY = "exploratory"


class DesignType(Enum):
    """试验设计类型"""
    PARALLEL = "parallel"           # 平行组设计
    CROSSOVER = "crossover"         # 交叉设计
    SINGLE_ARM = "single_arm"      # 单臂设计
    ADAPTIVE = "adaptive"           # 适应性设计
    BASKET = "basket"               # 篮式试验
    UMBRELLA = "umbrella"           # 伞式试验
    PLATFORM = "platform"           # 平台试验


class RandomizationType(Enum):
    """随机化类型"""
    SIMPLE = "simple"
    BLOCK = "block"
    STRATIFIED = "stratified"
    MINIMIZATION = "minimization"


@dataclass
class Endpoint:
    """临床终点定义"""
    name: str
    type: EndpointType
    description: str
    is_surrogate: bool = False
    min_clinically_important_diff: Optional[float] = None  # MCID
    baseline_value: Optional[float] = None
    expected_treatment_effect: Optional[float] = None
    standard_deviation: Optional[float] = None


@dataclass
class InclusionCriteria:
    """入排标准"""
    age_min: int = 18
    age_max: int = 75
    required_biomarkers: list = field(default_factory=list)
    required_stage: list = field(default_factory=list)
    ecog_max: int = 2
    organ_function_requirements: dict = field(default_factory=dict)
    prior_therapy_allowed: bool = True
    exclusion_items: list = field(default_factory=list)


@dataclass
class SampleSizeResult:
    """样本量计算结果"""
    per_arm: int
    total: int
    alpha: float
    power: float
    effect_size: float
    dropout_adjusted_total: int
    assumptions: dict = field(default_factory=dict)


@dataclass
class TrialDesign:
    """临床试验设计方案"""
    trial_name: str
    phase: TrialPhase
    indication: str
    design_type: DesignType
    randomization: Optional[RandomizationType] = None
    blinding: str = "open_label"  # open_label, single, double
    primary_endpoint: Optional[Endpoint] = None
    secondary_endpoints: list = field(default_factory=list)
    inclusion_criteria: Optional[InclusionCriteria] = None
    sample_size: Optional[SampleSizeResult] = None
    treatment_arms: list = field(default_factory=list)
    stratification_factors: list = field(default_factory=list)
    interim_analyses: list = field(default_factory=list)
    estimated_duration_months: int = 0
    estimated_cost_millions: float = 0.0


class TrialDesignEngine:
    """
    临床试验设计引擎

    提供样本量计算、试验方案生成、统计功效分析等功能。
    """

    # 常用 Z 值
    Z_VALUES = {
        0.001: 3.291,
        0.005: 2.576,
        0.01: 2.326,
        0.025: 1.960,
        0.05: 1.645,
        0.1: 1.282,
    }

    # 各期试验典型参数
    PHASE_DEFAULTS = {
        TrialPhase.PHASE_1: {
            "typical_n": 30,
            "duration_months": 18,
            "cost_millions": 25,
            "primary_focus": "安全性与耐受性",
            "design": DesignType.SINGLE_ARM,
        },
        TrialPhase.PHASE_1_2: {
            "typical_n": 80,
            "duration_months": 24,
            "cost_millions": 40,
            "primary_focus": "安全性 + 初步疗效",
            "design": DesignType.ADAPTIVE,
        },
        TrialPhase.PHASE_2: {
            "typical_n": 200,
            "duration_months": 30,
            "cost_millions": 50,
            "primary_focus": "概念验证与剂量探索",
            "design": DesignType.ADAPTIVE,
        },
        TrialPhase.PHASE_2_3: {
            "typical_n": 400,
            "duration_months": 36,
            "cost_millions": 100,
            "primary_focus": "无缝设计，剂量确认到注册",
            "design": DesignType.ADAPTIVE,
        },
        TrialPhase.PHASE_3: {
            "typical_n": 800,
            "duration_months": 42,
            "cost_millions": 150,
            "primary_focus": "确证性疗效与安全性",
            "design": DesignType.PARALLEL,
        },
    }

    def calculate_sample_size_continuous(
        self,
        mean_diff: float,
        sd: float,
        alpha: float = 0.05,
        power: float = 0.80,
        allocation_ratio: float = 1.0,
        dropout_rate: float = 0.15,
    ) -> SampleSizeResult:
        """
        连续型终点样本量计算（两独立样本 t 检验）

        Args:
            mean_diff: 两组均值差（临床有意义差值）
            sd: 标准差（假设两组相等）
            alpha: 显著性水平（双侧）
            power: 统计功效
            allocation_ratio: 试验组/对照组分配比
            dropout_rate: 预期脱落率

        Returns:
            SampleSizeResult 样本量结果
        """
        z_alpha = self._get_z(alpha / 2)
        z_beta = self._get_z(1 - power)

        # 基础样本量（每组）
        n_per_arm = ((z_alpha + z_beta) ** 2 * sd**2 * (1 + 1/allocation_ratio)) / (mean_diff**2)
        n_per_arm = math.ceil(n_per_arm)

        # 脱落调整
        total = math.ceil(n_per_arm * (1 + allocation_ratio))
        dropout_adjusted = math.ceil(total / (1 - dropout_rate))

        effect_size = abs(mean_diff) / sd  # Cohen's d

        return SampleSizeResult(
            per_arm=n_per_arm,
            total=total,
            alpha=alpha,
            power=power,
            effect_size=effect_size,
            dropout_adjusted_total=dropout_adjusted,
            assumptions={
                "mean_diff": mean_diff,
                "sd": sd,
                "allocation_ratio": allocation_ratio,
                "dropout_rate": dropout_rate,
                "test": "two_sample_t_test",
            }
        )

    def calculate_sample_size_binary(
        self,
        p_control: float,
        p_treatment: float,
        alpha: float = 0.05,
        power: float = 0.80,
        allocation_ratio: float = 1.0,
        dropout_rate: float = 0.15,
    ) -> SampleSizeResult:
        """
        二分类终点样本量计算（两组比例比较）

        Args:
            p_control: 对照组事件发生率
            p_treatment: 试验组事件发生率
            alpha: 显著性水平（双侧）
            power: 统计功效
            allocation_ratio: 分配比
            dropout_rate: 脱落率

        Returns:
            SampleSizeResult 样本量结果
        """
        z_alpha = self._get_z(alpha / 2)
        z_beta = self._get_z(1 - power)

        p_bar = (p_control + allocation_ratio * p_treatment) / (1 + allocation_ratio)

        n_per_arm = (
            (z_alpha * math.sqrt(p_bar * (1 - p_bar) * (1 + 1/allocation_ratio)) +
             z_beta * math.sqrt(p_control * (1 - p_control) + p_treatment * (1 - p_treatment) / allocation_ratio)) ** 2
            / (p_control - p_treatment) ** 2
        )
        n_per_arm = math.ceil(n_per_arm)

        total = math.ceil(n_per_arm * (1 + allocation_ratio))
        dropout_adjusted = math.ceil(total / (1 - dropout_rate))

        return SampleSizeResult(
            per_arm=n_per_arm,
            total=total,
            alpha=alpha,
            power=power,
            effect_size=abs(p_treatment - p_control),
            dropout_adjusted_total=dropout_adjusted,
            assumptions={
                "p_control": p_control,
                "p_treatment": p_treatment,
                "allocation_ratio": allocation_ratio,
                "dropout_rate": dropout_rate,
                "test": "chi_square_test",
            }
        )

    def calculate_sample_size_survival(
        self,
        median_control: float,
        median_treatment: float,
        alpha: float = 0.05,
        power: float = 0.80,
        allocation_ratio: float = 1.0,
        dropout_rate: float = 0.10,
        follow_up_months: float = 24,
        accrual_months: float = 18,
    ) -> SampleSizeResult:
        """
        生存分析终点样本量计算（Log-rank 检验）

        Args:
            median_control: 对照组中位生存期（月）
            median_treatment: 试验组中位生存期（月）
            alpha: 显著性水平
            power: 统计功效
            allocation_ratio: 分配比
            dropout_rate: 脱落率
            follow_up_months: 随访时间
            accrual_months: 入组时间

        Returns:
            SampleSizeResult 样本量结果
        """
        z_alpha = self._get_z(alpha / 2)
        z_beta = self._get_z(1 - power)

        # 风险比
        hr = median_control / median_treatment

        # 所需事件数（Schoenfeld 公式）
        events = ((z_alpha + z_beta) ** 2 * (1 + allocation_ratio)**2) / (allocation_ratio * (math.log(hr))**2)
        events = math.ceil(events)

        # 估算入组率
        accrual_rate = 1.0  # 假设每月每组 1 人

        # 事件概率（考虑删失）
        lambda_c = -math.log(0.5) / median_control
        lambda_t = -math.log(0.5) / median_treatment

        # 简化估算：样本量 = 事件数 / 事件概率
        event_prob = 0.6  # 保守估计
        total = math.ceil(events / event_prob)
        per_arm = math.ceil(total / (1 + allocation_ratio))
        dropout_adjusted = math.ceil(total / (1 - dropout_rate))

        return SampleSizeResult(
            per_arm=per_arm,
            total=total,
            alpha=alpha,
            power=power,
            effect_size=hr,
            dropout_adjusted_total=dropout_adjusted,
            assumptions={
                "median_control": median_control,
                "median_treatment": median_treatment,
                "hazard_ratio": hr,
                "events_required": events,
                "follow_up_months": follow_up_months,
                "accrual_months": accrual_months,
                "test": "log_rank",
            }
        )

    def design_trial(
        self,
        trial_name: str,
        phase: TrialPhase,
        indication: str,
        primary_endpoint: Endpoint,
        treatment_arms: list = None,
        design_type: Optional[DesignType] = None,
        blinding: str = "double",
        randomization: RandomizationType = RandomizationType.STRATIFIED,
        stratification_factors: list = None,
        inclusion: Optional[InclusionCriteria] = None,
        adaptive_features: Optional[dict] = None,
    ) -> TrialDesign:
        """
        生成完整临床试验设计方案

        Args:
            trial_name: 试验名称
            phase: 试验阶段
            indication: 适应症
            primary_endpoint: 主要终点
            treatment_arms: 治疗组
            design_type: 设计类型
            blinding: 盲法
            randomization: 随机化方式
            stratification_factors: 分层因素
            inclusion: 入排标准
            adaptive_features: 适应性设计特征

        Returns:
            TrialDesign 试验设计方案
        """
        defaults = self.PHASE_DEFAULTS.get(phase, self.PHASE_DEFAULTS[TrialPhase.PHASE_3])

        if design_type is None:
            design_type = defaults["design"]

        if treatment_arms is None:
            treatment_arms = ["试验组", "对照组"]

        # 自动计算样本量
        sample_size = None
        if primary_endpoint.standard_deviation and primary_endpoint.expected_treatment_effect:
            sample_size = self.calculate_sample_size_continuous(
                mean_diff=primary_endpoint.expected_treatment_effect,
                sd=primary_endpoint.standard_deviation,
            )

        design = TrialDesign(
            trial_name=trial_name,
            phase=phase,
            indication=indication,
            design_type=design_type,
            randomization=randomization,
            blinding=blinding,
            primary_endpoint=primary_endpoint,
            inclusion_criteria=inclusion or InclusionCriteria(),
            sample_size=sample_size,
            treatment_arms=treatment_arms,
            stratification_factors=stratification_factors or [],
            estimated_duration_months=defaults["duration_months"],
            estimated_cost_millions=defaults["cost_millions"],
        )

        return design

    def suggest_endpoints(self, indication: str, phase: TrialPhase) -> list[Endpoint]:
        """
        根据适应症和阶段建议临床终点

        Args:
            indication: 适应症
            phase: 试验阶段

        Returns:
            建议的终点列表
        """
        endpoint_db = {
            "oncology": {
                TrialPhase.PHASE_1: [
                    Endpoint("DLT", EndpointType.PRIMARY, "剂量限制性毒性发生率"),
                    Endpoint("MTD", EndpointType.PRIMARY, "最大耐受剂量"),
                    Endpoint("ORR", EndpointType.SECONDARY, "客观缓解率", is_surrogate=True),
                ],
                TrialPhase.PHASE_2: [
                    Endpoint("ORR", EndpointType.PRIMARY, "客观缓解率", is_surrogate=True),
                    Endpoint("PFS", EndpointType.SECONDARY, "无进展生存期", is_surrogate=True),
                    Endpoint("DOR", EndpointType.SECONDARY, "缓解持续时间"),
                    Endpoint("DCR", EndpointType.EXPLORATORY, "疾病控制率"),
                ],
                TrialPhase.PHASE_3: [
                    Endpoint("OS", EndpointType.PRIMARY, "总生存期"),
                    Endpoint("PFS", EndpointType.SECONDARY, "无进展生存期", is_surrogate=True),
                    Endpoint("ORR", EndpointType.SECONDARY, "客观缓解率"),
                    Endpoint("QoL", EndpointType.SECONDARY, "生活质量评分"),
                ],
            },
            "metabolic": {
                TrialPhase.PHASE_2: [
                    Endpoint("HbA1c_change", EndpointType.PRIMARY, "HbA1c 较基线变化", is_surrogate=True),
                    Endpoint("FPG", EndpointType.SECONDARY, "空腹血糖变化"),
                    Endpoint("weight_change", EndpointType.SECONDARY, "体重变化"),
                ],
                TrialPhase.PHASE_3: [
                    Endpoint("MACE", EndpointType.PRIMARY, "主要心血管不良事件"),
                    Endpoint("HbA1c", EndpointType.SECONDARY, "HbA1c 达标率"),
                ],
            },
            "cardiovascular": {
                TrialPhase.PHASE_3: [
                    Endpoint("MACE", EndpointType.PRIMARY, "主要心血管不良事件"),
                    Endpoint("CV_death", EndpointType.SECONDARY, "心血管死亡"),
                    Endpoint("hospitalization", EndpointType.SECONDARY, "心衰住院率"),
                ],
            },
        }

        # 查找适应症对应的终点
        for key, phases in endpoint_db.items():
            if key in indication.lower():
                return phases.get(phase, [])

        # 默认返回通用终点
        return [
            Endpoint("primary_efficacy", EndpointType.PRIMARY, "主要疗效终点"),
            Endpoint("safety", EndpointType.SECONDARY, "安全性评估"),
        }

    def power_analysis(
        self,
        n_per_arm: int,
        sd: float = 1.0,
        alpha: float = 0.05,
    ) -> list[dict]:
        """
        功效分析 — 给定样本量下不同效应量的统计功效

        Args:
            n_per_arm: 每组样本量
            sd: 标准差
            alpha: 显著性水平

        Returns:
            不同效应量下的功效列表
        """
        results = []
        for effect in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]:
            mean_diff = effect * sd
            se = sd * math.sqrt(2 / n_per_arm)
            z_alpha = self._get_z(alpha / 2)
            z_nc = mean_diff / se  # 非中心参数
            # 近似功效
            power = 1 - self._norm_cdf(z_alpha - z_nc)
            results.append({
                "effect_size_cohens_d": effect,
                "mean_diff": mean_diff,
                "power": round(power, 4),
                "interpretation": self._interpret_power(power),
            })
        return results

    def _get_z(self, p: float) -> float:
        """获取 Z 值（近似）"""
        # 查找最近的值
        closest = min(self.Z_VALUES.keys(), key=lambda x: abs(x - p))
        return self.Z_VALUES[closest]

    @staticmethod
    def _norm_cdf(x: float) -> float:
        """标准正态分布 CDF（近似）"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    @staticmethod
    def _interpret_power(power: float) -> str:
        """解释统计功效"""
        if power >= 0.9:
            return "充分（≥90%）"
        elif power >= 0.8:
            return "足够（80-90%）"
        elif power >= 0.7:
            return "偏低（70-80%）"
        else:
            return "不足（<70%）"


def print_trial_design(design: TrialDesign):
    """打印试验设计方案"""
    print(f"\n{'='*60}")
    print(f"  📋 临床试验设计方案")
    print(f"{'='*60}")
    print(f"  试验名称:  {design.trial_name}")
    print(f"  阶段:      {design.phase.value}")
    print(f"  适应症:    {design.indication}")
    print(f"  设计类型:  {design.design_type.value}")
    print(f"  盲法:      {design.blinding}")
    print(f"  随机化:    {design.randomization.value if design.randomization else 'N/A'}")

    if design.primary_endpoint:
        print(f"\n  📊 主要终点")
        print(f"    名称: {design.primary_endpoint.name}")
        print(f"    描述: {design.primary_endpoint.description}")
        if design.primary_endpoint.expected_treatment_effect:
            print(f"    预期效应: {design.primary_endpoint.expected_treatment_effect}")

    if design.sample_size:
        print(f"\n  👥 样本量")
        print(f"    每组: {design.sample_size.per_arm}")
        print(f"    总计: {design.sample_size.total}")
        print(f"    脱落调整后: {design.sample_size.dropout_adjusted_total}")

    print(f"\n  💰 预估")
    print(f"    研究时长: {design.estimated_duration_months} 个月")
    print(f"    研究成本: ${design.estimated_cost_millions}M")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    engine = TrialDesignEngine()

    # 示例：设计一个 III 期肿瘤临床试验
    primary = Endpoint(
        name="OS",
        type=EndpointType.PRIMARY,
        description="总生存期",
        expected_treatment_effect=3.5,  # 预期延长 3.5 个月
        standard_deviation=8.0,
    )

    design = engine.design_trial(
        trial_name="EGFR-TKI-III-001",
        phase=TrialPhase.PHASE_3,
        indication="非小细胞肺癌（EGFR 突变）",
        primary_endpoint=primary,
        treatment_arms=["EGFR-TKI 新药", "奥希替尼"],
        blinding="open_label",
        randomization=RandomizationType.STRATIFIED,
        stratification_factors=["EGFR 突变类型", "脑转移", "ECOG PS"],
    )

    print_trial_design(design)

    # 功效分析
    if design.sample_size:
        print("📊 功效分析")
        power_results = engine.power_analysis(n_per_arm=design.sample_size.per_arm)
        for r in power_results:
            bar = "█" * int(r["power"] * 30)
            print(f"  d={r['effect_size_cohens_d']:.1f}  {bar} {r['power']:.1%}  {r['interpretation']}")
