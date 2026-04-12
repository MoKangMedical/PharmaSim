"""
PharmaSim - 核心模拟引擎 (v3.0)
1000 Agent多维度仿真 + Aaru风格社交网络交互
"""

import json
import random
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.agent_factory import AgentFactory
from simulation.social_network import SocialNetwork
from simulation.interaction_engine import InteractionEngine, DeliberationResult


@dataclass
class SimulationConfig:
    """模拟配置"""
    drug: dict
    num_agents: int = 1800             # 总Agent数 (400医生 + 1000患者 + 400专家 + 1医保)
    simulation_months: int = 24
    random_seed: int = 42
    parallel_evaluation: bool = True
    max_workers: int = 8
    # 交互参数
    deliberation_rounds: int = 8       # 多轮协商轮次
    convergence_threshold: float = 0.01
    region_focus: List[str] = field(default_factory=lambda: [
        "北京", "上海", "广州", "深圳", "成都", "武汉",
        "杭州", "南京", "重庆", "天津", "西安", "长沙",
    ])


@dataclass
class MonthlySnapshot:
    """月度快照"""
    month: int
    prescription_volume: int
    market_penetration: float
    revenue: float
    doctor_adoption_rate: float
    patient_satisfaction: float
    insurance_coverage: bool
    new_prescribers: int
    cumulative_prescribers: int
    # 社交网络衍生指标
    social_willingness: float = 0.0    # 社交协商后平均意愿
    enthusiast_ratio: float = 0.0      # 积极采纳者占比
    skeptic_ratio: float = 0.0         # 怀疑者占比
    dimension_scores: dict = field(default_factory=dict)
    competitor_response: str = ""


@dataclass
class DimensionResult:
    """单维度评估结果"""
    dimension: str
    avg_score: float
    median_score: float
    std_score: float
    min_score: float
    max_score: float
    confidence: float
    top_findings: List[str] = field(default_factory=list)
    top_risks: List[str] = field(default_factory=list)
    agent_count: int = 0


class SimulationEngine:
    """药品上市模拟引擎 - 1000 Agent + 社交网络交互仿真"""

    def __init__(self, config: SimulationConfig):
        self.config = config
        self.drug = config.drug
        self.results: List[MonthlySnapshot] = []
        self.agents: dict = {}
        self.dimension_results: Dict[str, DimensionResult] = {}
        self.expert_evaluations: Dict[str, List[dict]] = {}
        self.social_network: Optional[SocialNetwork] = None
        self.deliberation_result: Optional[DeliberationResult] = None

        random.seed(config.random_seed)

    def run(self) -> dict:
        """运行完整模拟"""
        print("=" * 60)
        print(f"🚀 PharmaSim v3.0 多维度社交仿真")
        print(f"   药品: {self.drug.get('name', '未知')}")
        print(f"   模拟时长: {self.config.simulation_months} 个月")
        print("=" * 60)

        # Phase 1: 生成Agent
        print("\n📦 Phase 1: Agent生成")
        factory = AgentFactory(
            drug=self.drug,
            num_agents=self.config.num_agents,
            random_seed=self.config.random_seed,
        )
        self.agents = factory.create_all_agents()

        # Phase 2: 多维度专家评估
        print("\n🔍 Phase 2: 多维度专家评估")
        self._run_expert_evaluations()
        self._aggregate_dimension_scores()

        # Phase 3: 医保决策
        print("\n🏥 Phase 3: 医保准入评估")
        payer = self.agents["payer"]
        payer_decision = payer.evaluate_reimbursement(self.drug)
        print(f"   准入结果: {'✅ 通过' if payer_decision['will_cover'] else '❌ 未通过'}")

        # Phase 4: 构建社交网络
        print("\n🔗 Phase 4: 社交网络构建")
        self.social_network = SocialNetwork(random_seed=self.config.random_seed)
        patients = self.agents["patients"]
        doctors = self.agents["doctors"]
        network_stats = self.social_network.build_patient_network(
            patients=patients,
            doctors=doctors,
            expert_agents=self.agents,
        )
        print(f"   网络统计: {network_stats}")

        # Phase 5: 多轮交互协商 (Aaru核心)
        print("\n🔄 Phase 5: 多轮交互协商")
        multidim_scores = {k: v.avg_score for k, v in self.dimension_results.items()}
        engine = InteractionEngine(
            network=self.social_network,
            random_seed=self.config.random_seed,
        )
        self.deliberation_result = engine.run_deliberation(
            patients=patients,
            drug=self.drug,
            multidim_scores=multidim_scores,
            payer_decision=payer_decision,
            max_rounds=self.config.deliberation_rounds,
            convergence_threshold=self.config.convergence_threshold,
        )
        self._print_deliberation_summary()

        # Phase 6: 逐月市场仿真 (融合社交协商结果)
        print("\n📈 Phase 6: 月度市场仿真")
        self._run_market_simulation(payer_decision)

        # Phase 7: 汇总
        print("\n📋 Phase 7: 结果汇总")
        summary = self._generate_summary()
        multi_dim_summary = self._generate_multidim_summary()
        deliberation_summary = self._generate_deliberation_summary()

        print("\n" + "=" * 60)
        print("✅ 仿真完成!")
        print("=" * 60)

        return {
            "drug_name": self.drug.get("name", "未知"),
            "simulation_months": self.config.simulation_months,
            "num_agents": {
                "total": sum(len(v) if isinstance(v, list) else 1 for v in self.agents.values()),
                "doctors": len(self.agents["doctors"]),
                "patients": len(self.agents["patients"]),
                "experts": sum(len(v) for k, v in self.agents.items()
                              if k not in ["doctors", "patients", "payer"]),
            },
            "monthly_snapshots": [self._snapshot_to_dict(s) for s in self.results],
            "summary": summary,
            "multidim_summary": multi_dim_summary,
            "deliberation_summary": deliberation_summary,
            "payer_decision": payer_decision,
            "dimension_results": {k: self._dim_result_to_dict(v) for k, v in self.dimension_results.items()},
            "network_stats": network_stats,
            "agent_allocation": factory.get_summary(),
            "config": {
                "num_agents": self.config.num_agents,
                "simulation_months": self.config.simulation_months,
                "random_seed": self.config.random_seed,
                "deliberation_rounds": self.config.deliberation_rounds,
            },
        }

    def _run_expert_evaluations(self):
        """运行所有专家Agent的评估"""
        expert_types = [
            ("药物学评估", "pharmacology_experts"),
            ("流行病学评估", "epidemiology_experts"),
            ("药物经济学评估", "pharmacoeconomics_experts"),
            ("医保评估", "insurance_experts"),
            ("临床评估", "clinical_experts"),
            ("定价评估", "pricing_experts"),
            ("市场评估", "market_experts"),
        ]

        for dim_name, agent_key in expert_types:
            experts = self.agents.get(agent_key, [])
            if not experts:
                continue

            evaluations = []
            if self.config.parallel_evaluation and len(experts) > 10:
                evaluations = self._parallel_evaluate(experts)
            else:
                for expert in experts:
                    try:
                        result = expert.evaluate_drug(self.drug)
                        evaluations.append(result)
                    except Exception as e:
                        pass

            self.expert_evaluations[dim_name] = evaluations
            print(f"   {dim_name}: {len(evaluations)}位专家完成评估")

    def _parallel_evaluate(self, experts: list) -> list:
        evaluations = []
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {executor.submit(exp.evaluate_drug, self.drug): exp for exp in experts}
            for future in as_completed(futures):
                try:
                    evaluations.append(future.result())
                except:
                    pass
        return evaluations

    def _aggregate_dimension_scores(self):
        import statistics
        for dim_name, evaluations in self.expert_evaluations.items():
            if not evaluations:
                continue
            scores = [e.get("overall_score", 0.5) for e in evaluations]
            confidences = [e.get("confidence", 0.5) for e in evaluations]
            all_findings = []
            all_risks = []
            for e in evaluations:
                all_findings.extend(e.get("key_findings", []))
                all_risks.extend(e.get("risks", []))
            from collections import Counter
            fc, rc = Counter(all_findings), Counter(all_risks)
            self.dimension_results[dim_name] = DimensionResult(
                dimension=dim_name,
                avg_score=round(statistics.mean(scores), 3),
                median_score=round(statistics.median(scores), 3),
                std_score=round(statistics.stdev(scores), 3) if len(scores) > 1 else 0,
                min_score=round(min(scores), 3),
                max_score=round(max(scores), 3),
                confidence=round(statistics.mean(confidences), 3),
                top_findings=[f for f, _ in fc.most_common(5)],
                top_risks=[r for r, _ in rc.most_common(5)],
                agent_count=len(evaluations),
            )

    def _print_deliberation_summary(self):
        dr = self.deliberation_result
        if not dr:
            return
        print(f"\n   ── 交互协商结果 ──")
        print(f"   协商轮次: {dr.num_rounds}")
        print(f"   收敛: {'是' if dr.convergence_achieved else '否'}")
        print(f"   最终平均意愿: {dr.final_avg_willingness:.3f}")
        print(f"   意愿分布: 积极={dr.willingness_distribution['high']:.1%}, "
              f"中立={dr.willingness_distribution['medium']:.1%}, "
              f"怀疑={dr.willingness_distribution['low']:.1%}")
        if dr.opinion_clusters:
            for cluster, members in dr.opinion_clusters.items():
                print(f"   {cluster}: {len(members)}人")

    def _run_market_simulation(self, payer_decision: dict):
        """逐月市场仿真 - 融合社交协商结果"""
        doctors = self.agents["doctors"]
        patients = self.agents["patients"]
        insurance_coverage_month = 6

        adopted_doctors = set()
        for month in range(1, self.config.simulation_months + 1):
            snapshot = self._simulate_month(
                month=month,
                doctors=doctors,
                patients=patients,
                adopted_doctors=adopted_doctors,
                insurance_active=(month >= insurance_coverage_month and payer_decision["will_cover"]),
                payer_decision=payer_decision,
            )
            self.results.append(snapshot)

            if month % 6 == 0:
                print(f"   📅 第{month}月: 处方量={snapshot.prescription_volume:,}, "
                      f"渗透率={snapshot.market_penetration:.1%}, "
                      f"收入={snapshot.revenue/1e8:.1f}亿, "
                      f"社交意愿={snapshot.social_willingness:.3f}")

    def _simulate_month(self, month: int, doctors: list, patients: list,
                         adopted_doctors: set, insurance_active: bool,
                         payer_decision: dict) -> MonthlySnapshot:
        from agents.doctor_agent import InnovationAttitude

        # 1. 医生采纳
        for doc in doctors:
            if doc.agent_id in adopted_doctors:
                continue
            decision = doc.evaluate_new_drug(self.drug)
            adopt_prob = self._calc_adoption_prob(doc, month, insurance_active, decision)
            # 多维度评分影响
            multi_dim_bonus = self._get_multidim_adoption_bonus()
            adopt_prob *= (1 + multi_dim_bonus)
            # 社交网络影响传播
            if self.deliberation_result:
                social_bonus = (self.deliberation_result.final_avg_willingness - 0.5) * 0.2
                adopt_prob *= (1 + social_bonus)
            if random.random() < adopt_prob:
                adopted_doctors.add(doc.agent_id)

        # 2. 处方量计算 (受社交意愿影响)
        adoption_rate = len(adopted_doctors) / len(doctors) if doctors else 0
        total_potential = sum(d.monthly_patient_volume for d in doctors if d.agent_id in adopted_doctors)

        # 社交协商后的患者接受度
        social_willingness = 0.5
        if self.deliberation_result:
            social_willingness = self.deliberation_result.final_avg_willingness

        # 时间维度：社交意愿随时间演化
        time_factor = min(1.0, month / 12)
        effective_willingness = 0.5 + (social_willingness - 0.5) * time_factor

        patient_fit = 0.15 * effective_willingness * 2
        prescription_volume = int(total_potential * patient_fit * 0.3)

        # 3. 渗透率
        total_addressable = sum(d.monthly_patient_volume for d in doctors) * 0.15
        market_penetration = prescription_volume / total_addressable if total_addressable > 0 else 0

        # 4. 收入
        price = self.drug.get("price", 0)
        effective_price = payer_decision.get("negotiation_price", price) if insurance_active else price
        revenue = prescription_volume * effective_price

        # 5. 患者满意度
        clin_score = self.dimension_results.get("临床评估")
        base_sat = 0.7 + (clin_score.avg_score - 0.5) * 0.2 if clin_score else 0.7
        patient_satisfaction = base_sat + random.uniform(-0.05, 0.05)

        # 6. 社交指标
        dist = self.deliberation_result.willingness_distribution if self.deliberation_result else {}
        enthusiast_ratio = dist.get("high", 0)
        skeptic_ratio = dist.get("low", 0)

        # 7. 竞品反应
        competitor_response = self._simulate_competitor_response(month, market_penetration)

        return MonthlySnapshot(
            month=month,
            prescription_volume=prescription_volume,
            market_penetration=round(market_penetration, 4),
            revenue=revenue,
            doctor_adoption_rate=round(adoption_rate, 4),
            patient_satisfaction=round(patient_satisfaction, 3),
            insurance_coverage=insurance_active,
            new_prescribers=len(adopted_doctors) - (self.results[-1].cumulative_prescribers if self.results else 0),
            cumulative_prescribers=len(adopted_doctors),
            social_willingness=round(social_willingness, 3),
            enthusiast_ratio=enthusiast_ratio,
            skeptic_ratio=skeptic_ratio,
            dimension_scores={k: v.avg_score for k, v in self.dimension_results.items()},
            competitor_response=competitor_response,
        )

    def _calc_adoption_prob(self, doctor, month, insurance_active, decision):
        from agents.doctor_agent import InnovationAttitude
        base_prob = 0.02
        if insurance_active:
            base_prob *= 1.5
        attitude = doctor.innovation_attitude
        if attitude == InnovationAttitude.EARLY_ADOPTER:
            base_prob *= 3.0 if month <= 3 else 1.5
        elif attitude == InnovationAttitude.EARLY_MAJORITY:
            base_prob *= 2.0 if month > 3 else 0.8
        elif attitude == InnovationAttitude.LATE_MAJORITY:
            base_prob *= 1.5 if month > 6 else 0.3
        else:
            base_prob *= 1.0 if month > 12 else 0.05
        if decision.get("score", 0) > 0.6:
            base_prob *= 1.3
        return min(base_prob, 0.5)

    def _get_multidim_adoption_bonus(self):
        if not self.dimension_results:
            return 0
        weights = {"临床评估": 0.3, "药物学评估": 0.2, "定价评估": 0.15,
                   "医保评估": 0.15, "市场评估": 0.1, "药物经济学评估": 0.05, "流行病学评估": 0.05}
        bonus = 0
        for dim, w in weights.items():
            dr = self.dimension_results.get(dim)
            if dr:
                bonus += (dr.avg_score - 0.5) * w * 2
        return bonus

    def _simulate_competitor_response(self, month, penetration):
        if penetration > 0.1 and month == 3:
            return "竞品A启动降价促销"
        elif penetration > 0.2 and month == 6:
            return "竞品B发布新适应症数据"
        elif penetration > 0.3 and month == 9:
            return "竞品C申请医保谈判"
        elif penetration > 0.4 and month == 12:
            return "竞品D推出差异化产品"
        return ""

    def _generate_summary(self):
        if not self.results:
            return {}
        peak = max(self.results, key=lambda s: s.prescription_volume)
        final = self.results[-1]
        y1 = sum(s.revenue for s in self.results[:12])
        y2 = sum(s.revenue for s in self.results[12:24]) if len(self.results) >= 24 else 0
        return {
            "peak_month": peak.month,
            "peak_prescription_volume": peak.prescription_volume,
            "peak_market_penetration": peak.market_penetration,
            "final_adoption_rate": final.doctor_adoption_rate,
            "final_market_penetration": final.market_penetration,
            "year1_revenue": y1,
            "year2_revenue": y2,
            "total_revenue": y1 + y2,
            "insurance_impact": "显著" if any(s.insurance_coverage for s in self.results) else "无",
            "avg_patient_satisfaction": round(sum(s.patient_satisfaction for s in self.results) / len(self.results), 3),
            "final_social_willingness": final.social_willingness,
            "final_enthusiast_ratio": final.enthusiast_ratio,
        }

    def _generate_multidim_summary(self):
        summary = {}
        for dim_name, dr in self.dimension_results.items():
            risk = "低风险" if dr.avg_score > 0.7 else ("中等风险" if dr.avg_score > 0.5 else "高风险")
            summary[dim_name] = {
                "avg_score": dr.avg_score, "median_score": dr.median_score,
                "std_score": dr.std_score, "confidence": dr.confidence,
                "risk_level": risk, "agent_count": dr.agent_count,
                "top_findings": dr.top_findings[:3], "top_risks": dr.top_risks[:3],
            }
        if self.dimension_results:
            all_scores = [dr.avg_score for dr in self.dimension_results.values()]
            overall = sum(all_scores) / len(all_scores)
            summary["综合评估"] = {
                "overall_score": round(overall, 3),
                "recommendation": "推荐上市" if overall > 0.65 else ("有条件推荐" if overall > 0.5 else "建议暂缓"),
                "num_dimensions": len(self.dimension_results),
                "total_experts": sum(dr.agent_count for dr in self.dimension_results.values()),
            }
        return summary

    def _generate_deliberation_summary(self):
        dr = self.deliberation_result
        if not dr:
            return {}
        return {
            "num_rounds": dr.num_rounds,
            "convergence_achieved": dr.convergence_achieved,
            "final_avg_willingness": round(dr.final_avg_willingness, 3),
            "willingness_distribution": dr.willingness_distribution,
            "opinion_clusters": {k: len(v) for k, v in dr.opinion_clusters.items()},
            "top_influencers": [(aid, round(score, 1)) for aid, score in dr.influencer_ranking[:10]],
            "round_history": [{
                "round": r.round_num,
                "avg_willingness": r.avg_willingness,
                "opinion_shifts": r.opinion_shifts,
                "convergence_rate": r.convergence_rate,
            } for r in dr.round_history],
        }

    @staticmethod
    def _snapshot_to_dict(s):
        return {
            "month": s.month, "prescription_volume": s.prescription_volume,
            "market_penetration": s.market_penetration, "revenue": s.revenue,
            "doctor_adoption_rate": s.doctor_adoption_rate,
            "patient_satisfaction": s.patient_satisfaction,
            "insurance_coverage": s.insurance_coverage,
            "new_prescribers": s.new_prescribers,
            "cumulative_prescribers": s.cumulative_prescribers,
            "social_willingness": s.social_willingness,
            "enthusiast_ratio": s.enthusiast_ratio,
            "skeptic_ratio": s.skeptic_ratio,
            "dimension_scores": s.dimension_scores,
            "competitor_response": s.competitor_response,
        }

    @staticmethod
    def _dim_result_to_dict(dr):
        return {
            "dimension": dr.dimension, "avg_score": dr.avg_score,
            "median_score": dr.median_score, "std_score": dr.std_score,
            "min_score": dr.min_score, "max_score": dr.max_score,
            "confidence": dr.confidence,
            "top_findings": dr.top_findings, "top_risks": dr.top_risks,
            "agent_count": dr.agent_count,
        }
