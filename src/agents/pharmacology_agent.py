"""
PharmaSim - 药物学专家 Agent 模块
模拟药物学专家从药理学、毒理学、药代动力学角度评估新药
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PharmacologyFocus(Enum):
    PHARMACOKINETICS = "药代动力学"      # ADME: 吸收/分布/代谢/排泄
    PHARMACODYNAMICS = "药效动力学"      # 作用机制/靶点/剂量效应
    TOXICOLOGY = "毒理学"                # 安全性/不良反应/药物相互作用
    FORMULATION = "制剂学"               # 剂型/稳定性/生物利用度


class ExpertiseLevel(Enum):
    JUNIOR = "初级"          # 3-5年经验
    INTERMEDIATE = "中级"    # 5-15年经验
    SENIOR = "高级"          # 15-25年经验
    EXPERT = "权威"          # 25+年经验，行业专家


@dataclass
class PharmacologyExpertAgent:
    """药物学专家智能体 - 从药物学角度评估新药"""

    agent_id: str
    name: str
    focus: PharmacologyFocus               # 专业方向
    expertise_level: ExpertiseLevel        # 专业水平
    therapeutic_area: str                  # 治疗领域专长
    years_experience: int                  # 从业年数
    publication_count: int                 # 发表论文数
    has_ind_experience: bool               # 是否有药企经验
    institution_type: str                  # "学术" / "药企" / "CRO" / "监管"

    # 内部状态
    evaluation_history: List[dict] = field(default_factory=list)
    drug_interaction_alerts: List[str] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """
        从药物学角度评估新药

        Returns:
            {
                "dimension": "药物学评估",
                "overall_score": float,
                "pk_score": float,        # 药代动力学得分
                "pd_score": float,        # 药效动力学得分
                "tox_score": float,       # 毒理学得分
                "formulation_score": float,  # 制剂学得分
                "confidence": float,
                "key_findings": list,
                "risks": list,
                "reasoning": str,
            }
        """
        key_findings = []
        risks = []

        # 药代动力学评估
        pk_score = self._evaluate_pk(drug, key_findings, risks)

        # 药效动力学评估
        pd_score = self._evaluate_pd(drug, key_findings, risks)

        # 毒理学评估
        tox_score = self._evaluate_toxicology(drug, key_findings, risks)

        # 制剂学评估
        form_score = self._evaluate_formulation(drug, key_findings, risks)

        # 按专业方向加权
        weights = self._get_dimension_weights()
        overall = (pk_score * weights["pk"] + pd_score * weights["pd"] +
                   tox_score * weights["tox"] + form_score * weights["form"])

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "药物学评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "pk_score": round(pk_score, 3),
            "pd_score": round(pd_score, 3),
            "tox_score": round(tox_score, 3),
            "formulation_score": round(form_score, 3),
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }

        self.evaluation_history.append(result)
        return result

    def _evaluate_pk(self, drug: dict, findings: list, risks: list) -> float:
        """药代动力学评估"""
        base = 0.5
        route = drug.get("administration_route", "口服")

        # 生物利用度
        bioavailability = drug.get("bioavailability", None)
        if bioavailability is not None:
            if bioavailability > 80:
                base += 0.15
                findings.append(f"生物利用度优秀({bioavailability}%)")
            elif bioavailability > 50:
                base += 0.05
            else:
                base -= 0.1
                risks.append(f"生物利用度偏低({bioavailability}%)")

        # 半衰期
        half_life = drug.get("half_life_hours", None)
        if half_life is not None:
            if 12 <= half_life <= 48:
                base += 0.1
                findings.append(f"半衰期适宜({half_life}h)，支持日一次给药")
            elif half_life < 4:
                base -= 0.1
                risks.append(f"半衰期过短({half_life}h)，需频繁给药")

        # 药物相互作用
        interactions = drug.get("drug_interactions", [])
        if len(interactions) > 5:
            base -= 0.15
            risks.append(f"存在{len(interactions)}种药物相互作用风险")
        elif len(interactions) == 0:
            base += 0.05
            findings.append("无显著药物相互作用")

        # 专业水平调整
        if self.expertise_level == ExpertiseLevel.EXPERT:
            base *= 1.02  # 权威专家更细致
        elif self.expertise_level == ExpertiseLevel.JUNIOR:
            base *= 0.98

        return min(max(base, 0.0), 1.0)

    def _evaluate_pd(self, drug: dict, findings: list, risks: list) -> float:
        """药效动力学评估"""
        base = 0.5

        # 靶点验证程度
        target_validation = drug.get("target_validation", "validated")
        validation_scores = {
            "validated": 0.9,       # 已验证靶点
            "partially_validated": 0.65,
            "novel": 0.4,           # 新靶点风险高但潜力大
            "unknown": 0.2,
        }
        base = validation_scores.get(target_validation, 0.5) * 0.7 + base * 0.3

        if target_validation == "validated":
            findings.append("靶点已获临床验证")
        elif target_validation == "novel":
            risks.append("新靶点，临床验证不充分")

        # 选择性
        selectivity = drug.get("selectivity_score", 0.5)
        if selectivity > 0.8:
            base += 0.1
            findings.append("靶点选择性高")
        elif selectivity < 0.3:
            base -= 0.1
            risks.append("选择性不足，可能导致脱靶效应")

        # 剂量-效应关系
        dose_response = drug.get("dose_response_slope", 0.5)
        if dose_response > 0.7:
            base += 0.05
            findings.append("剂量-效应关系明确")

        return min(max(base, 0.0), 1.0)

    def _evaluate_toxicology(self, drug: dict, findings: list, risks: list) -> float:
        """毒理学评估"""
        base = 0.6  # 默认偏安全

        safety = drug.get("safety", {})
        serious_ae = safety.get("serious_ae_rate", 10)

        if serious_ae < 5:
            base += 0.2
            findings.append(f"严重不良反应率低({serious_ae}%)")
        elif serious_ae < 15:
            base += 0.05
        elif serious_ae < 30:
            base -= 0.15
            risks.append(f"严重不良反应率较高({serious_ae}%)")
        else:
            base -= 0.3
            risks.append(f"严重不良反应率过高({serious_ae}%)，需REMS")

        # 黑框警告
        if drug.get("black_box_warning", False):
            base -= 0.2
            risks.append("存在FDA黑框警告")

        # QT延长风险
        if drug.get("qt_prolongation_risk", False):
            base -= 0.1
            risks.append("存在QT间期延长风险")

        # 毒理学专家额外关注
        if self.focus == PharmacologyFocus.TOXICOLOGY:
            # 检查更多毒理信号
            hepatoxicity = safety.get("hepatoxicity_signal", False)
            nephrotoxicity = safety.get("nephrotoxicity_signal", False)
            if hepatoxicity:
                base -= 0.1
                risks.append("肝毒性信号阳性")
            if nephrotoxicity:
                base -= 0.08
                risks.append("肾毒性信号阳性")

        return min(max(base, 0.0), 1.0)

    def _evaluate_formulation(self, drug: dict, findings: list, risks: list) -> float:
        """制剂学评估"""
        base = 0.5

        route = drug.get("administration_route", "口服")
        route_scores = {
            "口服": 0.8,    # 患者依从性好
            "注射": 0.5,    # 需要医疗人员
            "静脉": 0.4,    # 需要住院
            "吸入": 0.7,    # 局部给药
            "外用": 0.75,   # 局部
            "皮下": 0.6,    # 可自行注射
        }
        base = route_scores.get(route, 0.5) * 0.4 + base * 0.6

        # 稳定性
        storage = drug.get("storage_requirement", "room_temp")
        if storage == "cold_chain":
            base -= 0.15
            risks.append("需冷链储运，增加流通成本")
        elif storage == "room_temp":
            base += 0.05
            findings.append("常温储存，便于流通")

        # 生物等效性
        if drug.get("bioequivalence_available", False):
            base += 0.1
            findings.append("已建立生物等效性")

        return min(max(base, 0.0), 1.0)

    def _get_dimension_weights(self) -> dict:
        """根据专业方向调整维度权重"""
        if self.focus == PharmacologyFocus.PHARMACOKINETICS:
            return {"pk": 0.45, "pd": 0.2, "tox": 0.2, "form": 0.15}
        elif self.focus == PharmacologyFocus.PHARMACODYNAMICS:
            return {"pk": 0.15, "pd": 0.45, "tox": 0.25, "form": 0.15}
        elif self.focus == PharmacologyFocus.TOXICOLOGY:
            return {"pk": 0.15, "pd": 0.2, "tox": 0.5, "form": 0.15}
        elif self.focus == PharmacologyFocus.FORMULATION:
            return {"pk": 0.2, "pd": 0.15, "tox": 0.15, "form": 0.5}
        return {"pk": 0.25, "pd": 0.25, "tox": 0.25, "form": 0.25}

    def _calc_confidence(self) -> float:
        """计算评估信心"""
        base = 0.5
        if self.expertise_level == ExpertiseLevel.EXPERT:
            base += 0.3
        elif self.expertise_level == ExpertiseLevel.SENIOR:
            base += 0.2
        elif self.expertise_level == ExpertiseLevel.INTERMEDIATE:
            base += 0.1
        if self.publication_count > 50:
            base += 0.1
        if self.has_ind_experience:
            base += 0.05
        return min(base, 1.0)

    def _generate_reasoning(self, score: float, findings: list, risks: list) -> str:
        """生成评估理由"""
        parts = []
        if score > 0.7:
            parts.append("从药物学角度评估表现良好")
        elif score > 0.5:
            parts.append("药物学特征基本达标")
        else:
            parts.append("药物学方面存在显著风险")
        if findings:
            parts.append("优势: " + "；".join(findings[:3]))
        if risks:
            parts.append("风险: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": "药物学专家",
            "focus": self.focus.value,
            "expertise_level": self.expertise_level.value,
            "therapeutic_area": self.therapeutic_area,
            "years_experience": self.years_experience,
            "institution_type": self.institution_type,
        }
