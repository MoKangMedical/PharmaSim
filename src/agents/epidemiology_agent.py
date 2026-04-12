"""
PharmaSim - 流行病学专家 Agent 模块
模拟流行病学专家从疾病负担、发病率、人群特征角度评估新药市场
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class EpiFocus(Enum):
    DISEASE_BURDEN = "疾病负担"          # DALY/QALY/发病率
    POPULATION_ANALYSIS = "人群分析"     # 患者分层/亚组/流行病学特征
    REAL_WORLD_EVIDENCE = "真实世界证据" # RWE/登记研究/电子病历
    OUTCOMES_RESEARCH = "结局研究"       # 长期预后/生存分析/生活质量


class ExpertiseLevel(Enum):
    JUNIOR = "初级"
    INTERMEDIATE = "中级"
    SENIOR = "高级"
    EXPERT = "权威"


@dataclass
class EpidemiologyExpertAgent:
    """流行病学专家智能体 - 评估疾病人群和市场潜力"""

    agent_id: str
    name: str
    focus: EpiFocus
    expertise_level: ExpertiseLevel
    disease_expertise: str               # 疾病领域专长
    years_experience: int
    region_expertise: str                # 地区专长
    has_surveillance_experience: bool    # 是否有监测/登记经验
    institution_type: str                # "学术" / "疾控" / "药企" / "WHO"

    evaluation_history: List[dict] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """从流行病学角度评估新药市场"""
        key_findings = []
        risks = []

        # 疾病负担评估
        burden_score = self._evaluate_burden(drug, key_findings, risks)

        # 人群可及性
        population_score = self._evaluate_population(drug, key_findings, risks)

        # 真实世界证据
        rwe_score = self._evaluate_rwe(drug, key_findings, risks)

        # 预后改善
        outcome_score = self._evaluate_outcomes(drug, key_findings, risks)

        weights = self._get_weights()
        overall = (burden_score * weights["burden"] + population_score * weights["pop"] +
                   rwe_score * weights["rwe"] + outcome_score * weights["outcome"])

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "流行病学评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "burden_score": round(burden_score, 3),
            "population_score": round(population_score, 3),
            "rwe_score": round(rwe_score, 3),
            "outcome_score": round(outcome_score, 3),
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }
        self.evaluation_history.append(result)
        return result

    def _evaluate_burden(self, drug: dict, findings: list, risks: list) -> float:
        """疾病负担评估"""
        base = 0.5
        indication = drug.get("indication_category", "")

        # 疾病负担权重
        burden_weights = {
            "肿瘤": 0.9, "罕见病": 0.85, "慢性病": 0.75,
            "精神疾病": 0.7, "感染性疾病": 0.65, "自身免疫": 0.7,
        }
        burden = burden_weights.get(indication, 0.5)
        base = base * 0.4 + burden * 0.6

        if burden > 0.7:
            findings.append(f"{indication}疾病负担高，未满足需求大")

        # 患者池大小
        prevalence = drug.get("prevalence_per_100k", None)
        if prevalence is not None:
            if prevalence > 500:
                base += 0.1
                findings.append(f"患病率较高({prevalence}/10万)，市场容量大")
            elif prevalence < 10:
                base -= 0.05
                risks.append(f"患病率极低({prevalence}/10万)，患者池有限")

        # 诊断率
        diagnosis_rate = drug.get("diagnosis_rate", 0.5)
        if diagnosis_rate < 0.3:
            risks.append(f"诊断率低({diagnosis_rate:.0%})，限制实际用药人群")
        else:
            base += 0.05

        return min(max(base, 0.0), 1.0)

    def _evaluate_population(self, drug: dict, findings: list, risks: list) -> float:
        """人群分析评估"""
        base = 0.5

        # 目标人群特征
        age_range = drug.get("target_age_range", "adult")
        if age_range == "all":
            base += 0.1
            findings.append("适用全年龄段人群")
        elif age_range == "elderly":
            base += 0.05
            findings.append("老年用药市场，人口老龄化趋势利好")

        # 亚组效应
        biomarker_required = drug.get("biomarker_required", False)
        if biomarker_required:
            base += 0.1
            findings.append("需要伴随诊断，精准医疗定位")
            # 但也要考虑检测可及性
            diagnostic_availability = drug.get("diagnostic_availability", 0.5)
            if diagnostic_availability < 0.3:
                base -= 0.1
                risks.append("伴随诊断可及性差，限制用药")

        # 地区分布匹配
        if self.region_expertise in drug.get("target_regions", ["全国"]):
            base += 0.05

        return min(max(base, 0.0), 1.0)

    def _evaluate_rwe(self, drug: dict, findings: list, risks: list) -> float:
        """真实世界证据评估"""
        base = 0.5

        rwe_available = drug.get("rwe_available", False)
        if rwe_available:
            base += 0.15
            findings.append("已有真实世界证据支持")

            rwe_sample_size = drug.get("rwe_sample_size", 0)
            if rwe_sample_size > 10000:
                base += 0.1
                findings.append(f"RWE样本量充足({rwe_sample_size}例)")
            elif rwe_sample_size > 1000:
                base += 0.05

            rwe_consistent = drug.get("rwe_consistent_with_rct", True)
            if rwe_consistent:
                findings.append("RWE与RCT结果一致")
            else:
                base -= 0.05
                risks.append("RWE与RCT结果不一致")
        else:
            risks.append("缺乏真实世界证据")

        # 登记研究
        if drug.get("registry_study_available", False):
            base += 0.05
            findings.append("有疾病登记研究数据")

        return min(max(base, 0.0), 1.0)

    def _evaluate_outcomes(self, drug: dict, findings: list, risks: list) -> float:
        """结局研究评估"""
        base = 0.5

        efficacy = drug.get("efficacy", {})

        # OS改善 (总生存期)
        os_improvement = efficacy.get("os_improvement", None)
        if os_improvement is not None:
            if os_improvement > 3:
                base += 0.2
                findings.append(f"总生存期显著改善(+{os_improvement}月)")
            elif os_improvement > 1:
                base += 0.1
                findings.append(f"总生存期有改善(+{os_improvement}月)")
            else:
                risks.append("OS改善有限")

        # PFS改善
        pfs_improvement = efficacy.get("pfs_improvement", None)
        if pfs_improvement is not None and pfs_improvement > 3:
            base += 0.1
            findings.append(f"PFS显著延长(+{pfs_improvement}月)")

        # 生活质量
        qol_improvement = drug.get("qol_improvement", None)
        if qol_improvement is not None:
            if qol_improvement > 0.1:
                base += 0.1
                findings.append("患者生活质量显著改善")
            elif qol_improvement < 0:
                base -= 0.1
                risks.append("生活质量下降")

        return min(max(base, 0.0), 1.0)

    def _get_weights(self) -> dict:
        if self.focus == EpiFocus.DISEASE_BURDEN:
            return {"burden": 0.45, "pop": 0.25, "rwe": 0.15, "outcome": 0.15}
        elif self.focus == EpiFocus.POPULATION_ANALYSIS:
            return {"burden": 0.2, "pop": 0.45, "rwe": 0.15, "outcome": 0.2}
        elif self.focus == EpiFocus.REAL_WORLD_EVIDENCE:
            return {"burden": 0.15, "pop": 0.15, "rwe": 0.45, "outcome": 0.25}
        elif self.focus == EpiFocus.OUTCOMES_RESEARCH:
            return {"burden": 0.15, "pop": 0.2, "rwe": 0.2, "outcome": 0.45}
        return {"burden": 0.25, "pop": 0.25, "rwe": 0.25, "outcome": 0.25}

    def _calc_confidence(self) -> float:
        base = 0.5
        level_bonus = {ExpertiseLevel.JUNIOR: 0.05, ExpertiseLevel.INTERMEDIATE: 0.1,
                       ExpertiseLevel.SENIOR: 0.2, ExpertiseLevel.EXPERT: 0.3}
        base += level_bonus.get(self.expertise_level, 0)
        if self.has_surveillance_experience:
            base += 0.1
        return min(base, 1.0)

    def _generate_reasoning(self, score, findings, risks) -> str:
        parts = []
        if score > 0.7:
            parts.append("从流行病学角度，该药物市场潜力较大")
        elif score > 0.5:
            parts.append("流行病学特征基本支持上市")
        else:
            parts.append("流行病学方面存在挑战")
        if findings:
            parts.append("利好: " + "；".join(findings[:3]))
        if risks:
            parts.append("挑战: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name,
            "type": "流行病学专家", "focus": self.focus.value,
            "expertise_level": self.expertise_level.value,
            "disease_expertise": self.disease_expertise,
            "years_experience": self.years_experience,
            "region_expertise": self.region_expertise,
        }
