"""
PharmaSim - 医保专家 Agent 模块
模拟医保专家从准入、报销、政策角度评估新药医保策略
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class InsuranceFocus(Enum):
    ACCESS_POLICY = "准入政策"          # 医保目录/谈判准入
    REIMBURSEMENT = "报销策略"          # 报销比例/自付比例/限定支付
    FUND_MANAGEMENT = "基金管理"        # 医保基金可持续性
    DRG_DIP = "DRG/DIP支付"            # 按病种付费影响


class ExpertiseLevel(Enum):
    JUNIOR = "初级"
    INTERMEDIATE = "中级"
    SENIOR = "高级"
    EXPERT = "权威"


@dataclass
class InsuranceExpertAgent:
    """医保专家智能体 - 评估医保准入和报销策略"""

    agent_id: str
    name: str
    focus: InsuranceFocus
    expertise_level: ExpertiseLevel
    years_experience: int
    region_expertise: str               # 地区专长
    has_negotiation_experience: bool    # 是否参与过谈判
    institution_type: str               # "医保局" / "学术" / "药企" / "咨询"
    fund_region: str                    # 负责地区基金

    evaluation_history: List[dict] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """从医保角度评估新药"""
        key_findings = []
        risks = []

        access_score = self._evaluate_access(drug, key_findings, risks)
        reimb_score = self._evaluate_reimbursement(drug, key_findings, risks)
        fund_score = self._evaluate_fund_impact(drug, key_findings, risks)
        drg_score = self._evaluate_drg_impact(drug, key_findings, risks)

        weights = self._get_weights()
        overall = (access_score * weights["access"] + reimb_score * weights["reimb"] +
                   fund_score * weights["fund"] + drg_score * weights["drg"])

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "医保评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "access_score": round(access_score, 3),
            "reimbursement_score": round(reimb_score, 3),
            "fund_impact_score": round(fund_score, 3),
            "drg_dip_score": round(drg_score, 3),
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }
        self.evaluation_history.append(result)
        return result

    def _evaluate_access(self, drug: dict, findings: list, risks: list) -> float:
        """准入评估"""
        base = 0.5
        indication = drug.get("indication_category", "")

        # 优先领域
        priority_areas = ["肿瘤", "罕见病", "慢性病", "儿童用药"]
        if indication in priority_areas:
            base += 0.15
            findings.append(f"{indication}属于医保优先领域")

        # 创新药快速通道
        if drug.get("is_novel_mechanism", False):
            base += 0.1
            findings.append("创新药可走快速准入通道")

        # 竞品是否已纳入
        competitors_covered = drug.get("competitors_in_insurance", 0)
        if competitors_covered > 3:
            base -= 0.1
            risks.append("同类药品已有多个纳入医保，空间有限")

        # 未满足需求
        if drug.get("unmet_need", False):
            base += 0.15
            findings.append("存在重大未满足需求，准入概率高")

        return min(max(base, 0.0), 1.0)

    def _evaluate_reimbursement(self, drug: dict, findings: list, risks: list) -> float:
        """报销策略评估"""
        base = 0.5
        price = drug.get("price", 0)

        # 价格水平判断
        if price < 1000:
            base += 0.15
            findings.append("价格较低，自付负担小")
        elif price < 10000:
            base += 0.05
        elif price < 50000:
            base -= 0.05
            risks.append("价格较高，可能需限定支付")
        else:
            base -= 0.15
            risks.append("高价格药品，报销受限")

        # 限定支付条件
        if drug.get("restricted_use", False):
            base -= 0.1
            risks.append("预计设置限定支付条件")

        # 门诊/住院报销
        outpatient_eligible = drug.get("outpatient_eligible", True)
        if outpatient_eligible:
            base += 0.1
            findings.append("可门诊报销，患者可及性高")

        return min(max(base, 0.0), 1.0)

    def _evaluate_fund_impact(self, drug: dict, findings: list, risks: list) -> float:
        """医保基金影响"""
        base = 0.5

        annual_cost = drug.get("estimated_annual_sales", 0)
        fund_size = 2.5e12  # 2.5万亿年度基金

        impact_ratio = annual_cost / fund_size if fund_size > 0 else 0
        if impact_ratio < 0.0001:
            base = 0.9
            findings.append("基金影响极小")
        elif impact_ratio < 0.001:
            base = 0.7
        elif impact_ratio < 0.005:
            base = 0.5
        elif impact_ratio < 0.01:
            base = 0.3
            risks.append("基金影响较大")
        else:
            base = 0.15
            risks.append("基金影响巨大，需审慎评估")

        # 节省效应
        if drug.get("reduces_total_cost", False):
            savings = drug.get("estimated_savings", 0)
            base += 0.1
            findings.append(f"预计年节省医保支出{savings/1e8:.1f}亿")

        return min(max(base, 0.0), 1.0)

    def _evaluate_drg_impact(self, drug: dict, findings: list, risks: list) -> float:
        """DRG/DIP支付影响"""
        base = 0.5

        if drug.get("drg_exempt", False):
            base += 0.15
            findings.append("可获DRG豁免，不占病组额度")
        else:
            price = drug.get("price", 0)
            drg_weight = drug.get("drg_weight", 1.0)
            if price > 30000 and drg_weight < 2:
                base -= 0.15
                risks.append("药品费用超出DRG病组支付标准")

        # 创新药除外支付
        if drug.get("innovation_exemption", False):
            base += 0.1
            findings.append("创新药除外支付，不受DRG限制")

        return min(max(base, 0.0), 1.0)

    def _get_weights(self) -> dict:
        if self.focus == InsuranceFocus.ACCESS_POLICY:
            return {"access": 0.45, "reimb": 0.2, "fund": 0.2, "drg": 0.15}
        elif self.focus == InsuranceFocus.REIMBURSEMENT:
            return {"access": 0.2, "reimb": 0.45, "fund": 0.15, "drg": 0.2}
        elif self.focus == InsuranceFocus.FUND_MANAGEMENT:
            return {"access": 0.15, "reimb": 0.15, "fund": 0.5, "drg": 0.2}
        elif self.focus == InsuranceFocus.DRG_DIP:
            return {"access": 0.15, "reimb": 0.2, "fund": 0.2, "drg": 0.45}
        return {"access": 0.25, "reimb": 0.25, "fund": 0.25, "drg": 0.25}

    def _calc_confidence(self) -> float:
        base = 0.5
        bonus = {ExpertiseLevel.JUNIOR: 0.05, ExpertiseLevel.INTERMEDIATE: 0.1,
                 ExpertiseLevel.SENIOR: 0.2, ExpertiseLevel.EXPERT: 0.3}
        base += bonus.get(self.expertise_level, 0)
        if self.has_negotiation_experience:
            base += 0.15
        return min(base, 1.0)

    def _generate_reasoning(self, score, findings, risks) -> str:
        parts = []
        if score > 0.7:
            parts.append("医保准入前景乐观")
        elif score > 0.5:
            parts.append("医保准入有希望但需策略优化")
        else:
            parts.append("医保准入面临较大挑战")
        if findings:
            parts.append("利好: " + "；".join(findings[:3]))
        if risks:
            parts.append("风险: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name,
            "type": "医保专家", "focus": self.focus.value,
            "expertise_level": self.expertise_level.value,
            "region_expertise": self.region_expertise,
        }
