"""
PharmaSim - 定价专家 Agent 模块
模拟定价专家从价格策略、价值定价角度评估新药
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PricingFocus(Enum):
    VALUE_BASED = "价值定价"            # 基于临床价值定价
    COMPETITIVE = "竞争定价"            # 竞品对标定价
    MARKET_ACCESS = "市场准入定价"      # 医保谈判导向定价
    INTERNATIONAL = "国际参考定价"      # 全球价格体系


class ExpertiseLevel(Enum):
    JUNIOR = "初级"
    INTERMEDIATE = "中级"
    SENIOR = "高级"
    EXPERT = "权威"


@dataclass
class PricingExpertAgent:
    """定价专家智能体 - 评估新药价格策略"""

    agent_id: str
    name: str
    focus: PricingFocus
    expertise_level: ExpertiseLevel
    years_experience: int
    therapeutic_expertise: str           # 治疗领域
    has_launch_experience: bool          # 是否有上市定价经验
    institution_type: str               # "药企" / "咨询" / "学术"

    evaluation_history: List[dict] = field(default_factory=list)

    def evaluate_drug(self, drug: dict) -> dict:
        """从定价角度评估新药"""
        key_findings = []
        risks = []

        value_score = self._evaluate_value_pricing(drug, key_findings, risks)
        competitive_score = self._evaluate_competitive(drug, key_findings, risks)
        access_score = self._evaluate_access_pricing(drug, key_findings, risks)
        intl_score = self._evaluate_international(drug, key_findings, risks)

        weights = self._get_weights()
        overall = (value_score * weights["value"] + competitive_score * weights["comp"] +
                   access_score * weights["access"] + intl_score * weights["intl"])

        optimal_price = self._estimate_optimal_price(drug)

        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "dimension": "定价评估",
            "focus": self.focus.value,
            "overall_score": round(overall, 3),
            "value_pricing_score": round(value_score, 3),
            "competitive_score": round(competitive_score, 3),
            "access_pricing_score": round(access_score, 3),
            "international_score": round(intl_score, 3),
            "optimal_price_estimate": optimal_price,
            "current_price": drug.get("price", 0),
            "price_position": self._assess_price_position(drug, optimal_price),
            "confidence": self._calc_confidence(),
            "key_findings": key_findings,
            "risks": risks,
            "reasoning": self._generate_reasoning(overall, key_findings, risks),
        }
        self.evaluation_history.append(result)
        return result

    def _evaluate_value_pricing(self, drug: dict, findings: list, risks: list) -> float:
        """价值定价评估"""
        base = 0.5

        # 临床价值 vs 价格
        efficacy = drug.get("efficacy", {})
        orr = efficacy.get("orr", 0)
        os_improvement = efficacy.get("os_improvement", 0)

        value_score = (orr / 100 * 0.4 + min(os_improvement / 5, 1) * 0.6) if orr > 0 else 0.3

        price = drug.get("price", 0)
        if price > 0:
            value_per_yuan = value_score / (price / 10000)
            if value_per_yuan > 0.5:
                base = 0.7
                findings.append("性价比良好")
            elif value_per_yuan > 0.2:
                base = 0.55
            else:
                base = 0.35
                risks.append("价值-价格比偏低")

        # 创新溢价
        if drug.get("first_in_class", False):
            base += 0.15
            findings.append("首创药物，享有创新溢价")
        elif drug.get("best_in_class", False):
            base += 0.1
            findings.append("最优同类药物，有定价优势")

        # 突破性疗法
        if drug.get("breakthrough_therapy", False):
            base += 0.1
            findings.append("突破性疗法认定，支撑溢价")

        return min(max(base, 0.0), 1.0)

    def _evaluate_competitive(self, drug: dict, findings: list, risks: list) -> float:
        """竞争定价评估"""
        base = 0.5

        competitor_prices = drug.get("competitor_prices", [])
        if competitor_prices:
            avg_price = sum(competitor_prices) / len(competitor_prices)
            price = drug.get("price", 0)

            if price <= avg_price * 0.8:
                base = 0.75
                findings.append(f"价格低于竞品均价({avg_price:.0f})，竞争优势明显")
            elif price <= avg_price * 1.2:
                base = 0.6
                findings.append("价格与竞品基本持平")
            elif price <= avg_price * 1.5:
                base = 0.4
                risks.append("价格高于竞品均价，需强有力价值支撑")
            else:
                base = 0.25
                risks.append("价格显著高于竞品，市场接受度风险高")

            # 差异化空间
            if drug.get("superior_to_standard", False) and price <= avg_price * 1.3:
                base += 0.1
                findings.append("疗效优势支撑溢价空间")
        else:
            base = 0.6
            findings.append("竞品价格数据不足，定价自由度大")

        return min(max(base, 0.0), 1.0)

    def _evaluate_access_pricing(self, drug: dict, findings: list, risks: list) -> float:
        """市场准入定价评估"""
        base = 0.5
        price = drug.get("price", 0)

        # 医保支付意愿
        icer = drug.get("icer", None)
        wtp = 3.0  # 万元/QALY
        if icer is not None:
            if icer < wtp:
                base += 0.15
                findings.append("ICER低于医保WTP阈值")
            elif icer < wtp * 1.5:
                base += 0.05
            else:
                base -= 0.1
                risks.append("ICER超出医保WTP，需降价谈判")

        # 患者自付可及性
        if price < 1000:
            base += 0.1
            findings.append("患者自付可及性高")
        elif price > 30000:
            base -= 0.1
            risks.append("患者自付负担重，依从性风险")

        # 患者援助项目可行性
        if drug.get("pap_eligible", False):
            base += 0.05
            findings.append("可设患者援助项目(PAP)改善可及性")

        return min(max(base, 0.0), 1.0)

    def _evaluate_international(self, drug: dict, findings: list, risks: list) -> float:
        """国际参考定价"""
        base = 0.5

        intl_prices = drug.get("international_prices", {})
        if intl_prices:
            us_price = intl_prices.get("us", None)
            jp_price = intl_prices.get("japan", None)
            eu_price = intl_prices.get("eu", None)

            if us_price:
                china_ratio = drug.get("price", 0) / us_price
                if china_ratio < 0.3:
                    findings.append(f"中国价格为美国的{china_ratio:.0%}，有提价空间")
                    base += 0.1
                elif china_ratio > 0.7:
                    risks.append("中国价格接近国际水平，提价空间有限")
                    base -= 0.05

            if len(intl_prices) >= 3:
                base += 0.05
                findings.append(f"已获{len(intl_prices)}国定价参考")
        else:
            base = 0.45

        return min(max(base, 0.0), 1.0)

    def _estimate_optimal_price(self, drug: dict) -> float:
        """估算最优定价"""
        competitor_prices = drug.get("competitor_prices", [])
        if competitor_prices:
            avg_comp = sum(competitor_prices) / len(competitor_prices)
        else:
            avg_comp = drug.get("price", 10000)

        # 基于价值调整
        multiplier = 1.0
        if drug.get("superior_to_standard", False):
            multiplier *= 1.15
        if drug.get("first_in_class", False):
            multiplier *= 1.2
        if drug.get("breakthrough_therapy", False):
            multiplier *= 1.1

        return round(avg_comp * multiplier, 2)

    def _assess_price_position(self, drug: dict, optimal: float) -> str:
        price = drug.get("price", 0)
        if price == 0:
            return "未定价"
        ratio = price / optimal if optimal > 0 else 1
        if ratio < 0.8:
            return "偏低-有提价空间"
        elif ratio < 1.1:
            return "合理"
        elif ratio < 1.3:
            return "偏高-需价值支撑"
        else:
            return "过高-降价风险"

    def _get_weights(self) -> dict:
        if self.focus == PricingFocus.VALUE_BASED:
            return {"value": 0.45, "comp": 0.2, "access": 0.2, "intl": 0.15}
        elif self.focus == PricingFocus.COMPETITIVE:
            return {"value": 0.2, "comp": 0.45, "access": 0.2, "intl": 0.15}
        elif self.focus == PricingFocus.MARKET_ACCESS:
            return {"value": 0.2, "comp": 0.15, "access": 0.45, "intl": 0.2}
        elif self.focus == PricingFocus.INTERNATIONAL:
            return {"value": 0.15, "comp": 0.2, "access": 0.2, "intl": 0.45}
        return {"value": 0.25, "comp": 0.25, "access": 0.25, "intl": 0.25}

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
            parts.append("定价策略合理，市场竞争力强")
        elif score > 0.5:
            parts.append("定价基本合理，有优化空间")
        else:
            parts.append("定价策略需调整")
        if findings:
            parts.append("优势: " + "；".join(findings[:3]))
        if risks:
            parts.append("风险: " + "；".join(risks[:3]))
        return "。".join(parts)

    def to_dict(self):
        return {
            "agent_id": self.agent_id, "name": self.name,
            "type": "定价专家", "focus": self.focus.value,
            "expertise_level": self.expertise_level.value,
            "therapeutic_expertise": self.therapeutic_expertise,
        }
