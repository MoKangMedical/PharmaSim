"""
PharmaSim - 患者 Agent 模块
模拟患者在不同情境下的用药决策行为
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class InsuranceType(Enum):
    URBAN_EMPLOYEE = "城镇职工"    # 报销比例最高
    URBAN_RESIDENT = "城镇居民"    # 中等报销
    NEW_RURAL = "新农合"           # 报销比例较低
    COMMERCIAL = "商业保险"        # 覆盖范围广
    SELF_PAY = "自费"             # 无保险


class EconomicLevel(Enum):
    HIGH = "高收入"        # 年收入>30万
    MIDDLE = "中等收入"    # 年收入10-30万
    LOW = "低收入"         # 年收入<10万


class InformationSource(Enum):
    DOCTOR = "医生推荐"
    PEER_COMMUNITY = "病友社区"
    ONLINE_SEARCH = "网络搜索"
    FAMILY = "家人决定"


@dataclass
class PatientAgent:
    """患者智能体 - 模拟就医和用药决策"""
    
    agent_id: str
    age: int
    gender: str
    disease_type: str               # 疾病类型
    disease_stage: str              # 疾病分期
    insurance_type: InsuranceType
    economic_level: EconomicLevel
    information_source: InformationSource
    adherence_score: float          # 用药依从性 0-1
    brand_preference: str           # "original" / "generic" / "indifferent"
    region: str
    
    # 内部状态
    current_treatment: Optional[str] = None
    treatment_history: List[str] = field(default_factory=list)
    satisfaction: float = 0.5       # 当前治疗满意度
    
    def decide_medication(self, options: list, doctor_recommendation: str = None) -> dict:
        """
        用药决策
        
        Args:
            options: 可选药品列表 [{name, price, insurance_covered, efficacy_rating, ...}]
            doctor_recommendation: 医生推荐的药品名
        
        Returns:
            {
                "chosen_drug": str,
                "will_pay_premium": bool,    # 是否愿意自费差价
                "reasoning": str,
                "confidence": float,
            }
        """
        if not options:
            return {"chosen_drug": None, "reasoning": "无可用药品", "confidence": 0}
        
        scored_options = []
        for opt in options:
            score = self._score_option(opt, doctor_recommendation)
            scored_options.append((opt, score))
        
        scored_options.sort(key=lambda x: x[1], reverse=True)
        best, best_score = scored_options[0]
        
        # 是否愿意自费差价
        will_pay_premium = False
        if not best.get("insurance_covered", True):
            if self.economic_level == EconomicLevel.HIGH:
                will_pay_premium = True
            elif self.economic_level == EconomicLevel.MIDDLE and best_score > 0.7:
                will_pay_premium = True
        
        return {
            "chosen_drug": best.get("name", "unknown"),
            "will_pay_premium": will_pay_premium,
            "reasoning": self._generate_reasoning(best, doctor_recommendation),
            "confidence": min(abs(best_score - 0.5) * 2, 1.0),
            "score": round(best_score, 3),
        }
    
    def _score_option(self, option: dict, doctor_rec: str = None) -> float:
        """给药品选项评分"""
        score = 0.5
        
        # 1. 医生推荐权重 (最高)
        if doctor_rec and option.get("name") == doctor_rec:
            if self.information_source == InformationSource.DOCTOR:
                score += 0.3
            else:
                score += 0.15
        
        # 2. 价格/医保因素
        if option.get("insurance_covered", False):
            score += 0.2
        else:
            # 自费药品, 根据经济水平和价格调整
            price_burden = option.get("monthly_cost", 0) / self._monthly_income()
            if price_burden < 0.05:
                score += 0.15
            elif price_burden < 0.15:
                score += 0.05
            else:
                score -= 0.2
        
        # 3. 疗效因素
        efficacy = option.get("efficacy_rating", 0.5)
        score += efficacy * 0.2
        
        # 4. 品牌偏好
        if self.brand_preference == "original" and option.get("is_original", False):
            score += 0.1
        elif self.brand_preference == "generic" and not option.get("is_original", True):
            score += 0.1
        
        # 5. 剂型便利性
        if option.get("dosing_convenience", 0) > 0.7:
            score += 0.05 * self.adherence_score
        
        return min(max(score, 0.0), 1.0)
    
    def _monthly_income(self) -> float:
        """月收入估算(元)"""
        income_map = {
            EconomicLevel.HIGH: 40000,
            EconomicLevel.MIDDLE: 15000,
            EconomicLevel.LOW: 5000,
        }
        return income_map.get(self.economic_level, 10000)
    
    def _generate_reasoning(self, chosen: dict, doctor_rec: str = None) -> str:
        """生成决策理由"""
        reasons = []
        if doctor_rec and chosen.get("name") == doctor_rec:
            reasons.append("医生推荐")
        if chosen.get("insurance_covered", False):
            reasons.append("医保可报销")
        if chosen.get("efficacy_rating", 0) > 0.7:
            reasons.append("疗效好")
        if self.brand_preference == "original" and chosen.get("is_original"):
            reasons.append("偏好原研药")
        return "；".join(reasons) if reasons else "综合考虑后选择"
    
    def evaluate_satisfaction(self, drug: dict, side_effects: list = None) -> float:
        """评估用药满意度"""
        base = 0.5
        if drug.get("efficacy_rating", 0) > 0.7:
            base += 0.2
        if side_effects and len(side_effects) > 2:
            base -= 0.15
        if drug.get("dosing_convenience", 0.5) > 0.7:
            base += 0.1
        self.satisfaction = min(max(base, 0.0), 1.0)
        return self.satisfaction
    
    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "age": self.age,
            "gender": self.gender,
            "disease_type": self.disease_type,
            "disease_stage": self.disease_stage,
            "insurance_type": self.insurance_type.value,
            "economic_level": self.economic_level.value,
            "region": self.region,
        }
