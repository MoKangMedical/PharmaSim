"""
PharmaSim - 市场专家 Agent 模块
模拟市场专家从竞争格局、渠道、推广角度评估新药
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class MarketFocus(Enum):
    COMPETITIVE_LANDSCAPE = "竞争格局"   # 竞品分析/差异化
    CHANNEL_STRATEGY = "渠道策略"        # 医院/药房/电商
    COMMERCIAL = "商业化策略"           # 上市推广/学术营销
    MARKET_SIZING = "市场容量"          # TAM/SAM/SOM


class ExpertiseLevel(Enum):
    JUNIOR = "初级"
    INTERMEDIATE = "中级"
    SENIOR = "高级"
    EXPERT = "权威"


@dataclass
class MarketExpertAgent:
    """市场专家智能体 - 评估新药商业化潜力"""

    agent_id: str
    name: str
    focus: MarketFocus
    expertise_level: ExpertiseLevel
    years_experience: int
    therapeutic_expertise: str
    has_launch_experience: bool          # 是否有上市推广经验
    institution_type: str               # "药企" / "咨询" / "投资" / "学术"
    company_type: str                   # "MNC" / "本土大型" / "Biotech" / "独立"

    evaluation_history: List[dict] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """从市场角度评估新药"""
        key_findings = []
        risks = []

        competitive_score = self._evaluate_competitive(drug, key_findings, risks)
        channel_score = self._evaluate_channel(drug, key_findings, risks)
        commercial_score = self._evaluate_commercial(drug, key_findings, risks)
        sizing_score = self._evaluate_market_size(drug, key_findings, risks)

        weights = self._get_weights()
        overall = (competitive_score * weights["comp"] + channel_score * weights["channel"] +
                   commercial_score * weights["comm"] + sizing_score * weights["sizing"])

        peak_sales = self._estimate_peak_sales(drug)
        market_share = self._estimate_market_share(drug)

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "市场评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "competitive_score": round(competitive_score, 3),
            "channel_score": round(channel_score, 3),
            "commercial_score": round(commercial_score, 3),
            "market_sizing_score": round(sizing_score, 3),
            "peak_sales_estimate": peak_sales,
            "market_share_estimate": market_share,
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }
        self.evaluation_history.append(result)
        return result

    def _evaluate_competitive(self, drug: dict, findings: list, risks: list) -> float:
        """竞争格局评估"""
        base = 0.5

        # 竞品数量
        num_competitors = drug.get("num_competitors", 3)
        if num_competitors == 0:
            base = 0.85
            findings.append("蓝海市场，无直接竞品")
        elif num_competitors <= 2:
            base = 0.7
            findings.append(f"竞争温和({num_competitors}个竞品)")
        elif num_competitors <= 5:
            base = 0.5
        elif num_competitors <= 8:
            base = 0.35
            risks.append(f"竞争激烈({num_competitors}个竞品)")
        else:
            base = 0.2
            risks.append(f"红海市场({num_competitors}个竞品)")

        # 差异化优势
        if drug.get("first_in_class", False):
            base += 0.15
            findings.append("首创药物，差异化优势显著")
        elif drug.get("best_in_class", False):
            base += 0.1
            findings.append("最优同类药物")
        elif drug.get("me_too", False):
            base -= 0.1
            risks.append("Me-too药物，差异化不足")

        # 专利保护
        patent_years = drug.get("patent_remaining_years", 10)
        if patent_years > 10:
            base += 0.05
            findings.append(f"专利保护充足(剩余{patent_years}年)")
        elif patent_years < 5:
            base -= 0.15
            risks.append(f"专利即将到期(剩余{patent_years}年)")

        return min(max(base, 0.0), 1.0)

    def _evaluate_channel(self, drug: dict, findings: list, risks: list) -> float:
        """渠道策略评估"""
        base = 0.5

        # 医院准入
        hospital_access = drug.get("hospital_access_ease", 0.5)
        if hospital_access > 0.7:
            base += 0.1
            findings.append("医院准入门槛低")
        elif hospital_access < 0.3:
            base -= 0.1
            risks.append("医院准入困难(新药需药事会审批)")

        # 零售药房可及性
        if drug.get("otc_eligible", False):
            base += 0.1
            findings.append("可转OTC，零售渠道可及性高")
        elif drug.get("retail_available", False):
            base += 0.05

        # DTP药房
        if drug.get("dtp_available", False):
            base += 0.05
            findings.append("DTP药房可及")

        # 电商渠道
        if drug.get("ecommerce_eligible", False):
            base += 0.05
            findings.append("可电商渠道销售")

        # 冷链要求
        if drug.get("storage_requirement") == "cold_chain":
            base -= 0.1
            risks.append("冷链要求增加渠道成本")

        return min(max(base, 0.0), 1.0)

    def _evaluate_commercial(self, drug: dict, findings: list, risks: list) -> float:
        """商业化策略评估"""
        base = 0.5

        # 学术推广难度
        evidence_level = drug.get("evidence_level", "case_series")
        if evidence_level in ["RCT_meta", "RCT"]:
            base += 0.1
            findings.append("高级别证据支撑学术推广")
        elif evidence_level in ["phase2", "case_series"]:
            base -= 0.1
            risks.append("证据不充分，学术推广受限")

        # 目标市场集中度
        target_specialties = drug.get("target_specialties", [])
        if len(target_specialties) <= 2:
            base += 0.05
            findings.append(f"目标科室聚焦({','.join(target_specialties)})，推广效率高")
        elif len(target_specialties) > 5:
            base -= 0.05
            risks.append("目标科室分散，推广成本高")

        # KOL支持
        if drug.get("kol_endorsed", False):
            base += 0.1
            findings.append("获KOL支持，学术推广有利")

        # 公司商业化能力
        company = drug.get("company_type", "")
        if company == "MNC":
            base += 0.1
            findings.append("MNC商业化能力强")
        elif company == "Biotech":
            base -= 0.05
            risks.append("Biotech商业化团队经验有限")

        return min(max(base, 0.0), 1.0)

    def _evaluate_market_size(self, drug: dict, findings: list, risks: list) -> float:
        """市场容量评估"""
        base = 0.5

        # TAM (总可及市场)
        tam = drug.get("tam_billion", None)
        if tam is not None:
            if tam > 50:
                base += 0.2
                findings.append(f"市场容量大(TAM={tam}亿)")
            elif tam > 10:
                base += 0.1
                findings.append(f"市场容量中等(TAM={tam}亿)")
            elif tam > 1:
                base += 0.05
            else:
                base -= 0.1
                risks.append(f"市场容量有限(TAM={tam}亿)")

        # 增长趋势
        cagr = drug.get("market_cagr", None)
        if cagr is not None:
            if cagr > 0.15:
                base += 0.1
                findings.append(f"市场增速高(CAGR={cagr:.0%})")
            elif cagr < 0.03:
                base -= 0.05
                risks.append(f"市场增长缓慢(CAGR={cagr:.0%})")

        # 患者流
        eligible_patients = drug.get("eligible_patient_count", None)
        if eligible_patients is not None:
            if eligible_patients > 1000000:
                findings.append(f"目标患者超{eligible_patients/1e6:.0f}百万")
                base += 0.05
            elif eligible_patients < 10000:
                risks.append(f"目标患者仅{eligible_patients/1e3:.0f}千人")

        return min(max(base, 0.0), 1.0)

    def _estimate_peak_sales(self, drug: dict) -> float:
        """估算峰值销售(亿元)"""
        tam = drug.get("tam_billion", 10)
        # 假设5-15%渗透率
        penetration = 0.1
        if drug.get("first_in_class", False):
            penetration = 0.15
        elif drug.get("best_in_class", False):
            penetration = 0.12
        elif drug.get("me_too", False):
            penetration = 0.05
        return round(tam * penetration, 1)

    def _estimate_market_share(self, drug: dict) -> str:
        """估算市场份额"""
        num_comp = drug.get("num_competitors", 3)
        if num_comp == 0:
            return "100%(独占)"
        elif num_comp <= 2:
            return "30-50%"
        elif num_comp <= 5:
            return "15-25%"
        elif num_comp <= 8:
            return "5-15%"
        else:
            return "3-8%"

    def _get_weights(self) -> dict:
        if self.focus == MarketFocus.COMPETITIVE_LANDSCAPE:
            return {"comp": 0.45, "channel": 0.15, "comm": 0.2, "sizing": 0.2}
        elif self.focus == MarketFocus.CHANNEL_STRATEGY:
            return {"comp": 0.15, "channel": 0.45, "comm": 0.2, "sizing": 0.2}
        elif self.focus == MarketFocus.COMMERCIAL:
            return {"comp": 0.2, "channel": 0.2, "comm": 0.45, "sizing": 0.15}
        elif self.focus == MarketFocus.MARKET_SIZING:
            return {"comp": 0.2, "channel": 0.15, "comm": 0.15, "sizing": 0.5}
        return {"comp": 0.25, "channel": 0.25, "comm": 0.25, "sizing": 0.25}

    def _calc_confidence(self) -> float:
        base = 0.5
        bonus = {ExpertiseLevel.JUNIOR: 0.05, ExpertiseLevel.INTERMEDIATE: 0.1,
                 ExpertiseLevel.SENIOR: 0.2, ExpertiseLevel.EXPERT: 0.3}
        base += bonus.get(self.expertise_level, 0)
        if self.has_launch_experience:
            base += 0.15
        return min(base, 1.0)

    def _generate_reasoning(self, score, findings, risks) -> str:
        parts = []
        if score > 0.7:
            parts.append("商业化前景看好")
        elif score > 0.5:
            parts.append("商业化潜力中等")
        else:
            parts.append("商业化面临较大挑战")
        if findings:
            parts.append("优势: " + "；".join(findings[:3]))
        if risks:
            parts.append("风险: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name,
            "type": "市场专家", "focus": self.focus.value,
            "expertise_level": self.expertise_level.value,
            "therapeutic_expertise": self.therapeutic_expertise,
        }
