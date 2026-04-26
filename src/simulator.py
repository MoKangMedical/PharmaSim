"""
PharmaSim — 药物研发全流程模拟引擎

基于蒙特卡洛模拟的药物研发管线成功率预测与成本估算。
结合历史成功率数据、治疗领域特征、分子类型等因素，
为药物研发决策提供量化支持。
"""

import json
import random
import math
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from enum import Enum


class TherapeuticArea(Enum):
    """治疗领域枚举"""
    ONCOLOGY = "oncology"
    CARDIOVASCULAR = "cardiovascular"
    NEUROLOGY = "neurology"
    INFECTIOUS_DISEASE = "infectious_disease"
    IMMUNOLOGY = "immunology"
    METABOLIC = "metabolic"
    RESPIRATORY = "respiratory"
    OPHTHALMOLOGY = "ophthalmology"
    RARE_DISEASE = "rare_disease"
    GASTROENTEROLOGY = "gastroenterology"


class Modality(Enum):
    """药物模态枚举"""
    SMALL_MOLECULE = "small_molecule"
    MONOCLONAL_ANTIBODY = "monoclonal_antibody"
    GENE_THERAPY = "gene_therapy"
    CELL_THERAPY = "cell_therapy"
    ANTISENSE_RNA = "antisense_rna"
    VACCINE = "vaccine"


@dataclass
class DrugCandidate:
    """药物候选分子描述"""
    name: str
    target: str
    indication: str
    therapeutic_area: TherapeuticArea
    modality: Modality = Modality.SMALL_MOLECULE
    is_first_in_class: bool = False
    is_orphan_drug: bool = False
    has_biomarker: bool = False
    ai_assisted: bool = False
    novelty_score: float = 0.5  # 0-1, 创新程度


@dataclass
class StageResult:
    """单阶段模拟结果"""
    stage_id: str
    stage_name: str
    passed: bool
    duration_months: float
    cost_millions_usd: float
    failure_reason: Optional[str] = None


@dataclass
class SimulationResult:
    """完整管线模拟结果"""
    drug_name: str
    iterations: int
    successes: int
    stage_results: list
    success_rate: float = 0.0
    avg_duration_years: float = 0.0
    avg_cost_millions_usd: float = 0.0
    median_duration_years: float = 0.0
    median_cost_millions_usd: float = 0.0
    time_to_market: float = 0.0
    cost_percentiles: dict = field(default_factory=dict)
    stage_pass_rates: dict = field(default_factory=dict)

    def __post_init__(self):
        self.success_rate = self.successes / self.iterations if self.iterations > 0 else 0.0


class SimulationEngine:
    """
    药物研发管线模拟引擎

    使用蒙特卡洛方法模拟药物研发全流程，考虑：
    - 各阶段历史成功率
    - 治疗领域与分子类型的影响
    - 创新程度与 AI 辅助的修正
    - 时间与成本的随机波动
    """

    STAGES = [
        "target_discovery",
        "hit_identification",
        "lead_optimization",
        "preclinical",
        "phase1",
        "phase2",
        "phase3",
        "regulatory",
    ]

    STAGE_NAMES = {
        "target_discovery": "靶点发现",
        "hit_identification": "苗头化合物发现",
        "lead_optimization": "先导化合物优化",
        "preclinical": "临床前研究",
        "phase1": "I 期临床",
        "phase2": "II 期临床",
        "phase3": "III 期临床",
        "regulatory": "监管审批",
    }

    # 基础成功率（preclinical → approval 通道）
    BASE_RATES = {
        "target_discovery": 0.65,
        "hit_identification": 0.55,
        "lead_optimization": 0.45,
        "preclinical": 0.57,
        "phase1": 0.632,
        "phase2": 0.307,
        "phase3": 0.578,
        "regulatory": 0.853,
    }

    # 治疗领域修正系数
    AREA_MODIFIERS = {
        TherapeuticArea.ONCOLOGY: {
            "phase1": 0.82, "phase2": 0.78, "phase3": 0.86, "regulatory": 0.94
        },
        TherapeuticArea.RARE_DISEASE: {
            "phase1": 1.19, "phase2": 1.47, "phase3": 1.25, "regulatory": 1.08
        },
        TherapeuticArea.NEUROLOGY: {
            "phase1": 0.92, "phase2": 0.72, "phase3": 0.83, "regulatory": 0.91
        },
        TherapeuticArea.CARDIOVASCULAR: {
            "phase1": 1.11, "phase2": 1.14, "phase3": 1.07, "regulatory": 1.03
        },
        TherapeuticArea.INFECTIOUS_DISEASE: {
            "phase1": 1.14, "phase2": 1.30, "phase3": 1.18, "regulatory": 1.05
        },
    }

    # 平均阶段耗时（月）
    BASE_DURATIONS = {
        "target_discovery": 24,
        "hit_identification": 12,
        "lead_optimization": 18,
        "preclinical": 24,
        "phase1": 18,
        "phase2": 30,
        "phase3": 36,
        "regulatory": 14,
    }

    # 平均阶段成本（百万美元）
    BASE_COSTS = {
        "target_discovery": 5,
        "hit_identification": 3,
        "lead_optimization": 8,
        "preclinical": 15,
        "phase1": 25,
        "phase2": 50,
        "phase3": 150,
        "regulatory": 15,
    }

    # 失败原因分布
    FAILURE_REASONS = {
        "phase1": {"pharmacokinetics": 0.25, "safety_toxicity": 0.40, "strategic": 0.20, "operational": 0.15},
        "phase2": {"lack_of_efficacy": 0.52, "safety": 0.24, "strategic": 0.15, "operational": 0.09},
        "phase3": {"lack_of_efficacy": 0.48, "safety": 0.18, "strategic": 0.12, "operational": 0.10, "commercial": 0.12},
        "regulatory": {"incomplete_data": 0.35, "safety_concern": 0.25, "efficacy_insufficient": 0.25, "cmc_issues": 0.15},
    }

    def __init__(self, data_dir: Optional[str] = None):
        """初始化模拟引擎，加载历史数据"""
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.pipeline_data = self._load_json("pipeline-stages.json")
        self.success_data = self._load_json("success-rates.json")

    def _load_json(self, filename: str) -> dict:
        """加载 JSON 数据文件"""
        filepath = self.data_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _get_adjusted_rate(self, stage: str, candidate: DrugCandidate) -> float:
        """
        根据治疗领域、分子类型等因素调整阶段成功率

        Args:
            stage: 阶段 ID
            candidate: 药物候选分子

        Returns:
            调整后的成功率 (0-1)
        """
        base = self.BASE_RATES.get(stage, 0.5)

        # 治疗领域修正
        area_mods = self.AREA_MODIFIERS.get(candidate.therapeutic_area, {})
        area_factor = area_mods.get(stage, 1.0)

        # 罕见病加成
        orphan_bonus = 1.1 if candidate.is_orphan_drug else 1.0

        # 生物标志物加成
        biomarker_bonus = 1.08 if candidate.has_biomarker else 1.0

        # AI 辅助加成
        ai_bonus = 1.12 if candidate.ai_assisted else 1.0

        # First-in-class 稍低成功率（机制不明确风险）
        fic_penalty = 0.92 if candidate.is_first_in_class else 1.0

        # 计算最终成功率
        adjusted = base * area_factor * orphan_bonus * biomarker_bonus * ai_bonus * fic_penalty

        # 限制在合理范围
        return max(0.01, min(0.99, adjusted))

    def _sample_duration(self, stage: str, candidate: DrugCandidate) -> float:
        """采样阶段耗时（月），加入随机波动"""
        base = self.BASE_DURATIONS.get(stage, 18)
        # 使用正态分布，标准差为均值的 25%
        duration = random.gauss(base, base * 0.25)
        # 罕见病通常更快（入组容易）
        if candidate.is_orphan_drug and stage in ("phase1", "phase2", "phase3"):
            duration *= 0.8
        return max(6, duration)

    def _sample_cost(self, stage: str, candidate: DrugCandidate) -> float:
        """采样阶段成本（百万美元），加入随机波动"""
        base = self.BASE_COSTS.get(stage, 10)
        # 使用对数正态分布模拟成本分布
        log_mean = math.log(base) - 0.5 * (0.4 ** 2)
        cost = random.lognormvariate(log_mean, 0.4)
        # 罕见病成本稍低
        if candidate.is_orphan_drug and stage in ("phase1", "phase2", "phase3"):
            cost *= 0.75
        return max(0.5, cost)

    def _sample_failure_reason(self, stage: str) -> Optional[str]:
        """采样失败原因"""
        reasons = self.FAILURE_REASONS.get(stage)
        if not reasons:
            return None
        r = random.random()
        cumulative = 0.0
        for reason, prob in reasons.items():
            cumulative += prob
            if r <= cumulative:
                return reason
        return list(reasons.keys())[-1]

    def run(
        self,
        candidate: DrugCandidate,
        iterations: int = 10000,
        stages: Optional[list] = None,
        seed: Optional[int] = None,
    ) -> SimulationResult:
        """
        运行蒙特卡洛模拟

        Args:
            candidate: 药物候选分子描述
            iterations: 模拟迭代次数
            stages: 要模拟的阶段列表（默认全部）
            seed: 随机种子（用于结果复现）

        Returns:
            SimulationResult 模拟结果
        """
        if seed is not None:
            random.seed(seed)

        stages = stages or self.STAGES
        all_stage_results = []
        successes = 0
        durations = []
        costs = []
        stage_pass_counts = {s: 0 for s in stages}

        for i in range(iterations):
            iteration_passed = True
            iteration_duration = 0.0
            iteration_cost = 0.0
            iteration_stages = []

            for stage in stages:
                # 计算调整后的成功率
                rate = self._get_adjusted_rate(stage, candidate)
                passed = random.random() < rate

                # 采样耗时与成本
                duration = self._sample_duration(stage, candidate)
                cost = self._sample_cost(stage, candidate)

                failure_reason = None
                if not passed:
                    iteration_passed = False
                    failure_reason = self._sample_failure_reason(stage)

                stage_result = StageResult(
                    stage_id=stage,
                    stage_name=self.STAGE_NAMES.get(stage, stage),
                    passed=passed,
                    duration_months=duration,
                    cost_millions_usd=cost,
                    failure_reason=failure_reason,
                )
                iteration_stages.append(stage_result)
                iteration_duration += duration
                iteration_cost += cost

                stage_pass_counts[stage] += 1 if passed else 0

                if not passed:
                    break  # 失败则终止管线

            all_stage_results.extend(iteration_stages)

            if iteration_passed:
                successes += 1
                # 成功项目加上上市后监测时间（12个月）
                iteration_duration += 12
                iteration_cost += 5

            durations.append(iteration_duration)
            costs.append(iteration_cost)

        # 计算统计数据
        durations.sort()
        costs.sort()

        result = SimulationResult(
            drug_name=candidate.name,
            iterations=iterations,
            successes=successes,
            stage_results=all_stage_results,
            avg_duration_years=sum(durations) / len(durations) / 12,
            avg_cost_millions_usd=sum(costs) / len(costs),
            median_duration_years=durations[len(durations) // 2] / 12,
            median_cost_millions_usd=costs[len(costs) // 2],
            time_to_market=durations[len(durations) // 2] / 12,
            cost_percentiles={
                "p10": costs[int(len(costs) * 0.1)],
                "p25": costs[int(len(costs) * 0.25)],
                "p50": costs[int(len(costs) * 0.5)],
                "p75": costs[int(len(costs) * 0.75)],
                "p90": costs[int(len(costs) * 0.9)],
            },
            stage_pass_rates={
                stage: count / iterations for stage, count in stage_pass_counts.items()
            },
        )

        return result

    def batch_run(
        self,
        candidates: list[DrugCandidate],
        iterations: int = 10000,
        seed: Optional[int] = None,
    ) -> list[SimulationResult]:
        """
        批量模拟多个候选分子

        Args:
            candidates: 候选分子列表
            iterations: 每个候选分子的模拟次数
            seed: 随机种子

        Returns:
            模拟结果列表
        """
        results = []
        for i, candidate in enumerate(candidates):
            result = self.run(
                candidate=candidate,
                iterations=iterations,
                seed=seed + i if seed is not None else None,
            )
            results.append(result)
        return results

    def compare(self, results: list[SimulationResult]) -> dict:
        """
        对比多个候选分子的模拟结果

        Args:
            results: 模拟结果列表

        Returns:
            对比分析字典
        """
        comparison = {
            "candidates": [],
            "ranking_by_success_rate": [],
            "ranking_by_cost": [],
            "ranking_by_time": [],
        }

        for r in results:
            comparison["candidates"].append({
                "name": r.drug_name,
                "success_rate": f"{r.success_rate:.1%}",
                "avg_cost_millions": f"${r.avg_cost_millions_usd:.1f}M",
                "avg_time_years": f"{r.avg_duration_years:.1f}y",
                "time_to_market_years": f"{r.time_to_market:.1f}y",
            })

        # 按成功率排序
        sorted_by_sr = sorted(results, key=lambda x: x.success_rate, reverse=True)
        comparison["ranking_by_success_rate"] = [
            {"rank": i + 1, "name": r.drug_name, "rate": f"{r.success_rate:.1%}"}
            for i, r in enumerate(sorted_by_sr)
        ]

        # 按成本排序（低→高）
        sorted_by_cost = sorted(results, key=lambda x: x.avg_cost_millions_usd)
        comparison["ranking_by_cost"] = [
            {"rank": i + 1, "name": r.drug_name, "cost": f"${r.avg_cost_millions_usd:.1f}M"}
            for i, r in enumerate(sorted_by_cost)
        ]

        # 按时间排序（短→长）
        sorted_by_time = sorted(results, key=lambda x: x.avg_duration_years)
        comparison["ranking_by_time"] = [
            {"rank": i + 1, "name": r.drug_name, "time": f"{r.avg_duration_years:.1f}y"}
            for i, r in enumerate(sorted_by_time)
        ]

        return comparison


# === 便捷函数 ===

def quick_simulate(
    drug_name: str,
    target: str,
    indication: str,
    therapeutic_area: str = "oncology",
    modality: str = "small_molecule",
    iterations: int = 10000,
    **kwargs,
) -> SimulationResult:
    """
    快速模拟接口 — 一行代码完成管线模拟

    Args:
        drug_name: 药物名称
        target: 靶点
        indication: 适应症
        therapeutic_area: 治疗领域
        modality: 药物模态
        iterations: 迭代次数
        **kwargs: 其他候选分子属性

    Returns:
        SimulationResult 模拟结果
    """
    engine = SimulationEngine()
    candidate = DrugCandidate(
        name=drug_name,
        target=target,
        indication=indication,
        therapeutic_area=TherapeuticArea(therapeutic_area),
        modality=Modality(modality),
        **kwargs,
    )
    return engine.run(candidate, iterations=iterations)


def print_report(result: SimulationResult):
    """打印模拟报告"""
    print(f"\n{'='*60}")
    print(f"  🧪 PharmaSim 模拟报告 — {result.drug_name}")
    print(f"{'='*60}")
    print(f"\n📊 总体结果")
    print(f"  模拟次数:      {result.iterations:,}")
    print(f"  成功次数:      {result.successes:,}")
    print(f"  综合成功率:    {result.success_rate:.1%}")
    print(f"\n⏱️  时间预估")
    print(f"  平均研发时间:  {result.avg_duration_years:.1f} 年")
    print(f"  中位研发时间:  {result.median_duration_years:.1f} 年")
    print(f"\n💰 成本预估")
    print(f"  平均研发成本:  ${result.avg_cost_millions_usd:,.1f}M")
    print(f"  中位研发成本:  ${result.median_cost_millions_usd:,.1f}M")
    print(f"  P10-P90 区间:  ${result.cost_percentiles['p10']:,.1f}M — ${result.cost_percentiles['p90']:,.1f}M")
    print(f"\n📈 各阶段通过率")
    for stage, rate in result.stage_pass_rates.items():
        name = SimulationEngine.STAGE_NAMES.get(stage, stage)
        bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))
        print(f"  {name:12s} {bar} {rate:.1%}")
    print(f"\n{'='*60}\n")


# === 主程序入口 ===

if __name__ == "__main__":
    # 示例：模拟一个 NSCLC 的 EGFR 靶点小分子药物
    candidate = DrugCandidate(
        name="Simertinib-Next",
        target="EGFR-T790M/C797S",
        indication="非小细胞肺癌（NSCLC）",
        therapeutic_area=TherapeuticArea.ONCOLOGY,
        modality=Modality.SMALL_MOLECULE,
        is_first_in_class=True,
        has_biomarker=True,
        ai_assisted=True,
    )

    engine = SimulationEngine()
    result = engine.run(candidate, iterations=10000, seed=42)
    print_report(result)
