"""
PharmaSim - 临床专家 Agent 模块
模拟临床专家从疗效、安全性、指南依从角度评估新药
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ClinicalFocus(Enum):
    EFFICACY = "疗效评估"               # 临床终点/缓解率/生存获益
    SAFETY = "安全性评估"               # 不良事件/风险管理
    GUIDELINE = "指南与循证"            # 指南推荐/证据等级
    REAL_WORLD = "真实临床实践"         # 临床可操作性/依从性


class ExpertiseLevel(Enum):
    JUNIOR = "初级"
    INTERMEDIATE = "中级"
    SENIOR = "高级"
    EXPERT = "权威"


@dataclass
class ClinicalExpertAgent:
    """临床专家智能体 - 评估新药的临床价值"""

    agent_id: str
    name: str
    focus: ClinicalFocus
    expertise_level: ExpertiseLevel
    specialty: str                       # 专业科室
    years_experience: int
    publication_count: int
    has_kol_status: bool                 # 是否为KOL
    institution_type: str                # "三甲" / "二甲" / "学术" / "药企"

    evaluation_history: List[dict] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """从临床角度评估新药"""
        key_findings = []
        risks = []

        efficacy_score = self._evaluate_efficacy(drug, key_findings, risks)
        safety_score = self._evaluate_safety(drug, key_findings, risks)
        guideline_score = self._evaluate_guideline(drug, key_findings, risks)
        practice_score = self._evaluate_practicality(drug, key_findings, risks)

        weights = self._get_weights()
        overall = (efficacy_score * weights["efficacy"] + safety_score * weights["safety"] +
                   guideline_score * weights["guideline"] + practice_score * weights["practice"])

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "临床评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "efficacy_score": round(efficacy_score, 3),
            "safety_score": round(safety_score, 3),
            "guideline_score": round(guideline_score, 3),
            "practicality_score": round(practice_score, 3),
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }
        self.evaluation_history.append(result)
        return result

    def _evaluate_efficacy(self, drug: dict, findings: list, risks: list) -> float:
        """疗效评估"""
        base = 0.5
        efficacy = drug.get("efficacy", {})

        # ORR (客观缓解率)
        orr = efficacy.get("orr", None)
        if orr is not None:
            if orr > 60:
                base += 0.2
                findings.append(f"ORR优异({orr}%)")
            elif orr > 40:
                base += 0.1
                findings.append(f"ORR良好({orr}%)")
            elif orr > 20:
                base += 0.0
            else:
                base -= 0.1
                risks.append(f"ORR偏低({orr}%)")

        # 与标准治疗比较
        superiority = drug.get("superior_to_standard", False)
        non_inferiority = drug.get("non_inferior_to_standard", False)
        if superiority:
            base += 0.15
            findings.append("优于标准治疗")
        elif non_inferiority:
            base += 0.05
            findings.append("非劣于标准治疗")
        elif drug.get("first_in_class", False):
            base += 0.1
            findings.append("首创药物，无标准治疗对比")

        # 统计学显著性
        if drug.get("primary_endpoint_met", True):
            base += 0.05
        else:
            base -= 0.15
            risks.append("主要终点未达到统计学显著性")

        # KOL影响力加成
        if self.has_kol_status and drug.get("evidence_level") == "RCT":
            base *= 1.05

        return min(max(base, 0.0), 1.0)

    def _evaluate_safety(self, drug: dict, findings: list, risks: list) -> float:
        """安全性评估"""
        base = 0.6
        safety = drug.get("safety", {})

        serious_ae = safety.get("serious_ae_rate", 10)
        if serious_ae < 5:
            base += 0.2
            findings.append(f"安全性良好(SAE率{serious_ae}%)")
        elif serious_ae < 10:
            base += 0.1
        elif serious_ae < 20:
            base -= 0.05
        elif serious_ae < 30:
            base -= 0.15
            risks.append(f"SAE率较高({serious_ae}%)")
        else:
            base -= 0.25
            risks.append(f"SAE率过高({serious_ae}%)")

        # 停药率
        discontinuation = safety.get("treatment_discontinuation_rate", 10)
        if discontinuation < 5:
            findings.append("停药率低，耐受性好")
        elif discontinuation > 15:
            base -= 0.1
            risks.append(f"停药率较高({discontinuation}%)")

        # 黑框警告
        if drug.get("black_box_warning", False):
            base -= 0.15
            risks.append("存在黑框警告")

        return min(max(base, 0.0), 1.0)

    def _evaluate_guideline(self, drug: dict, findings: list, risks: list) -> float:
        """指南与循证评估"""
        base = 0.5

        evidence_level = drug.get("evidence_level", "case_series")
        evidence_scores = {
            "RCT_meta": 0.95,     # Meta分析
            "RCT": 0.85,           # RCT
            "phase3": 0.7,         # III期
            "phase2": 0.5,         # II期
            "real_world": 0.6,     # 真实世界
            "case_series": 0.3,    # 病例系列
        }
        base = evidence_scores.get(evidence_level, 0.5) * 0.7 + base * 0.3

        if evidence_level in ["RCT_meta", "RCT"]:
            findings.append(f"证据等级高({evidence_level})")

        # 指南推荐
        guideline_rec = drug.get("guideline_recommendation", None)
        if guideline_rec == "category_1":
            base += 0.15
            findings.append("获指南1类推荐")
        elif guideline_rec == "category_2a":
            base += 0.1
            findings.append("获指南2A类推荐")
        elif guideline_rec is None:
            risks.append("尚未获指南推荐")

        # 多国批准
        countries_approved = drug.get("countries_approved", 0)
        if countries_approved > 10:
            base += 0.05
            findings.append(f"已获{countries_approved}个国家批准")

        return min(max(base, 0.0), 1.0)

    def _evaluate_practicality(self, drug: dict, findings: list, risks: list) -> float:
        """临床可操作性"""
        base = 0.5

        # 给药便利性
        dosing = drug.get("dosing_convenience", 0.5)
        if dosing > 0.7:
            base += 0.1
            findings.append("给药方案简便")
        elif dosing < 0.3:
            base -= 0.1
            risks.append("给药方案复杂")

        # 是否需要特殊设备
        if drug.get("requires_special_equipment", False):
            base -= 0.1
            risks.append("需要特殊设备，基层推广受限")

        # 伴随诊断
        if drug.get("biomarker_required", False):
            diag_avail = drug.get("diagnostic_availability", 0.5)
            if diag_avail < 0.3:
                base -= 0.1
                risks.append("伴随诊断可及性差")

        # 患者依从性
        if drug.get("oral_administration", False):
            base += 0.05
            findings.append("口服给药，依从性好")

        return min(max(base, 0.0), 1.0)

    def _get_weights(self) -> dict:
        if self.focus == ClinicalFocus.EFFICACY:
            return {"efficacy": 0.5, "safety": 0.2, "guideline": 0.15, "practice": 0.15}
        elif self.focus == ClinicalFocus.SAFETY:
            return {"efficacy": 0.2, "safety": 0.5, "guideline": 0.15, "practice": 0.15}
        elif self.focus == ClinicalFocus.GUIDELINE:
            return {"efficacy": 0.2, "safety": 0.15, "guideline": 0.5, "practice": 0.15}
        elif self.focus == ClinicalFocus.REAL_WORLD:
            return {"efficacy": 0.15, "safety": 0.2, "guideline": 0.15, "practice": 0.5}
        return {"efficacy": 0.3, "safety": 0.25, "guideline": 0.25, "practice": 0.2}

    def _calc_confidence(self) -> float:
        base = 0.5
        bonus = {ExpertiseLevel.JUNIOR: 0.05, ExpertiseLevel.INTERMEDIATE: 0.1,
                 ExpertiseLevel.SENIOR: 0.2, ExpertiseLevel.EXPERT: 0.3}
        base += bonus.get(self.expertise_level, 0)
        if self.has_kol_status:
            base += 0.15
        if self.publication_count > 30:
            base += 0.05
        return min(base, 1.0)

    def _generate_reasoning(self, score, findings, risks) -> str:
        parts = []
        if score > 0.7:
            parts.append("临床价值明确，有望获得积极推荐")
        elif score > 0.5:
            parts.append("具有一定临床价值")
        else:
            parts.append("临床价值尚需更多证据支持")
        if findings:
            parts.append("优势: " + "；".join(findings[:3]))
        if risks:
            parts.append("顾虑: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name,
            "type": "临床专家", "focus": self.focus.value,
            "specialty": self.specialty,
            "expertise_level": self.expertise_level.value,
            "has_kol_status": self.has_kol_status,
        }
