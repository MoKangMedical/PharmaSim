"""
PharmaSim - 药物经济学专家 Agent 模块
模拟药物经济学专家从ICER、成本效果、预算影响角度评估新药
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class HEORFocus(Enum):
    COST_EFFECTIVENESS = "成本效果分析"  # ICER/QALY
    BUDGET_IMPACT = "预算影响分析"       # 财务可持续性
    MODELING = "经济学建模"              # Markov/决策树/微观模拟
    HTA = "卫生技术评估"                 # 综合评估框架


class ExpertiseLevel(Enum):
    JUNIOR = "初级"
    INTERMEDIATE = "中级"
    SENIOR = "高级"
    EXPERT = "权威"


@dataclass
class PharmacoeconomicsExpertAgent:
    """药物经济学专家智能体 - 评估药物经济学价值"""

    agent_id: str
    name: str
    focus: HEORFocus
    expertise_level: ExpertiseLevel
    years_experience: int
    wtp_threshold: float                 # 意愿支付阈值(万元/QALY)
    modeling_expertise: str              # "markov" / "decision_tree" / "microsimulation"
    institution_type: str               # "学术" / "药企" / "HTA机构" / "咨询"
    has_hta_submission: bool            # 是否有HTA申报经验

    evaluation_history: List[dict] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """从药物经济学角度评估新药"""
        key_findings = []
        risks = []

        ce_score = self._evaluate_cost_effectiveness(drug, key_findings, risks)
        budget_score = self._evaluate_budget_impact(drug, key_findings, risks)
        modeling_score = self._evaluate_evidence_quality(drug, key_findings, risks)
        hta_score = self._evaluate_hta_readiness(drug, key_findings, risks)

        weights = self._get_weights()
        overall = (ce_score * weights["ce"] + budget_score * weights["budget"] +
                   modeling_score * weights["model"] + hta_score * weights["hta"])

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "药物经济学评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "cost_effectiveness_score": round(ce_score, 3),
            "budget_impact_score": round(budget_score, 3),
            "evidence_quality_score": round(modeling_score, 3),
            "hta_readiness_score": round(hta_score, 3),
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }
        self.evaluation_history.append(result)
        return result

    def _evaluate_cost_effectiveness(self, drug: dict, findings: list, risks: list) -> float:
        """成本效果分析"""
        base = 0.5
        icer = drug.get("icer", None)

        if icer is not None:
            # 对比WTP阈值
            if icer <= self.wtp_threshold:
                ratio = icer / self.wtp_threshold
                base = 0.9 - ratio * 0.2
                findings.append(f"ICER({icer}万/QALY)低于WTP阈值({self.wtp_threshold}万/QALY)")
            elif icer <= self.wtp_threshold * 1.5:
                base = 0.6 - (icer / self.wtp_threshold - 1) * 0.4
                risks.append(f"ICER({icer}万/QALY)略高于WTP阈值")
            elif icer <= self.wtp_threshold * 3:
                base = 0.3
                risks.append(f"ICER({icer}万/QALY)显著超出阈值，经济学依据不足")
            else:
                base = 0.1
                risks.append(f"ICER({icer}万/QALY)严重超标")
        else:
            base = 0.4
            risks.append("缺乏ICER数据")

        # 增量QALY
        incremental_qaly = drug.get("incremental_qaly", None)
        if incremental_qaly is not None:
            if incremental_qaly > 1.0:
                base += 0.05
                findings.append(f"增量QALY={incremental_qaly:.1f}，临床获益显著")
            elif incremental_qaly < 0.1:
                base -= 0.05
                risks.append(f"增量QALY过小({incremental_qaly:.2f})")

        return min(max(base, 0.0), 1.0)

    def _evaluate_budget_impact(self, drug: dict, findings: list, risks: list) -> float:
        """预算影响评估"""
        base = 0.5

        annual_cost = drug.get("estimated_annual_sales", 0)
        budget_threshold = 5e9  # 50亿年销售

        if annual_cost < 1e9:
            base = 0.8
            findings.append("预算影响可控(年<10亿)")
        elif annual_cost < budget_threshold:
            base = 0.6
            findings.append(f"预算影响中等(年≈{annual_cost/1e8:.0f}亿)")
        elif annual_cost < 2 * budget_threshold:
            base = 0.4
            risks.append(f"预算影响较大(年≈{annual_cost/1e8:.0f}亿)")
        else:
            base = 0.2
            risks.append(f"预算影响巨大(年≈{annual_cost/1e8:.0f}亿)")

        # 适用患者人数
        eligible_patients = drug.get("eligible_patient_count", None)
        if eligible_patients is not None:
            per_patient_cost = annual_cost / eligible_patients if eligible_patients > 0 else 0
            if per_patient_cost > 500000:
                risks.append(f"人均年治疗费用过高({per_patient_cost/10000:.1f}万)")

        # 预算节省可能
        if drug.get("reduces_hospitalization", False):
            base += 0.1
            findings.append("可减少住院费用，产生预算节省")

        return min(max(base, 0.0), 1.0)

    def _evaluate_evidence_quality(self, drug: dict, findings: list, risks: list) -> float:
        """经济学证据质量"""
        base = 0.5

        # 研究类型
        study_type = drug.get("heor_study_type", None)
        if study_type == "markov_model":
            base += 0.15
            findings.append("采用Markov模型，方法学规范")
        elif study_type == "decision_tree":
            base += 0.1
            findings.append("采用决策树模型")
        elif study_type is None:
            base -= 0.15
            risks.append("缺乏经济学模型研究")

        # 效用值来源
        utility_source = drug.get("utility_source", None)
        if utility_source == "rct_measured":
            base += 0.1
            findings.append("效用值来自RCT实测")
        elif utility_source == "literature":
            base += 0.05
        elif utility_source is None:
            risks.append("效用值来源不明确")

        # 敏感性分析
        if drug.get("sensitivity_analysis_done", False):
            base += 0.05
            findings.append("已进行敏感性分析")

        return min(max(base, 0.0), 1.0)

    def _evaluate_hta_readiness(self, drug: dict, findings: list, risks: list) -> float:
        """HTA申报准备度"""
        base = 0.5

        if drug.get("hta_dossier_ready", False):
            base += 0.2
            findings.append("HTA申报资料已准备就绪")
        elif drug.get("hta_dossier_in_progress", False):
            base += 0.1
        else:
            risks.append("HTA申报资料尚不完整")

        # 国际HTA结果参考
        international_hta = drug.get("international_hta_results", [])
        if len(international_hta) > 0:
            positive_count = sum(1 for r in international_hta if r.get("approved", False))
            if positive_count > 0:
                base += 0.1
                findings.append(f"{positive_count}个国家/地区HTA通过")

        # 专利保护期
        patent_years = drug.get("patent_remaining_years", 10)
        if patent_years < 5:
            base -= 0.1
            risks.append(f"专利剩余{patent_years}年，经济学回报期短")

        return min(max(base, 0.0), 1.0)

    def _get_weights(self) -> dict:
        if self.focus == HEORFocus.COST_EFFECTIVENESS:
            return {"ce": 0.45, "budget": 0.2, "model": 0.2, "hta": 0.15}
        elif self.focus == HEORFocus.BUDGET_IMPACT:
            return {"ce": 0.2, "budget": 0.45, "model": 0.15, "hta": 0.2}
        elif self.focus == HEORFocus.MODELING:
            return {"ce": 0.25, "budget": 0.15, "model": 0.45, "hta": 0.15}
        elif self.focus == HEORFocus.HTA:
            return {"ce": 0.2, "budget": 0.2, "model": 0.15, "hta": 0.45}
        return {"ce": 0.25, "budget": 0.25, "model": 0.25, "hta": 0.25}

    def _calc_confidence(self) -> float:
        base = 0.5
        bonus = {ExpertiseLevel.JUNIOR: 0.05, ExpertiseLevel.INTERMEDIATE: 0.1,
                 ExpertiseLevel.SENIOR: 0.2, ExpertiseLevel.EXPERT: 0.3}
        base += bonus.get(self.expertise_level, 0)
        if self.has_hta_submission:
            base += 0.1
        return min(base, 1.0)

    def _generate_reasoning(self, score, findings, risks) -> str:
        parts = []
        if score > 0.7:
            parts.append("药物经济学证据充分，具有成本效果优势")
        elif score > 0.5:
            parts.append("经济学证据基本支持")
        else:
            parts.append("药物经济学方面存在不足")
        if findings:
            parts.append("优势: " + "；".join(findings[:3]))
        if risks:
            parts.append("风险: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name,
            "type": "药物经济学专家", "focus": self.focus.value,
            "expertise_level": self.expertise_level.value,
            "wtp_threshold": self.wtp_threshold,
            "institution_type": self.institution_type,
        }
