"""
PharmaSim - 医保/支付方 Agent 模块
模拟医保谈判、报销政策决策
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class NegotiationStyle(Enum):
    AGGRESSIVE = "激进压价"     # 大幅压价
    MODERATE = "温和协商"       # 合理谈判
    LENIENT = "相对宽松"        # 鼓励创新


class FundStatus(Enum):
    ABUNDANT = "充裕"
    BALANCED = "平衡"
    TIGHT = "紧张"


@dataclass
class PayerAgent:
    """医保/支付方智能体"""
    
    agent_id: str = "payer-national"
    name: str = "国家医保局"
    
    fund_status: FundStatus = FundStatus.BALANCED
    negotiation_style: NegotiationStyle = NegotiationStyle.MODERATE
    
    annual_budget: float = 2_500_000_000_000  # 年度医保基金(元)
    remaining_budget_ratio: float = 0.4        # 剩余预算比例
    
    # 决策偏好
    priority_diseases: List[str] = field(default_factory=lambda: ["肿瘤", "罕见病", "慢性病"])
    innovation_preference: float = 0.6         # 对创新药的偏好 0-1
    cost_effectiveness_threshold: float = 3.0  # ICER阈值(万元/QALY)
    
    # 历史谈判记录
    negotiation_history: List[dict] = field(default_factory=list)
    
    def evaluate_reimbursement(self, drug: dict) -> dict:
        """
        评估药品医保准入
        
        Returns:
            {
                "will_cover": bool,
                "negotiation_price": float,    # 预期谈判价格
                "reimbursement_ratio": float,  # 报销比例
                "restrictions": list,          # 使用限制
                "confidence": float,
                "reasoning": str,
            }
        """
        score = 0.0
        reasons = []
        restrictions = []
        
        # 1. 临床必要性 (40%)
        clinical_score = self._evaluate_clinical_need(drug)
        score += clinical_score * 0.4
        
        # 2. 药物经济学 (30%)
        heor_score = self._evaluate_cost_effectiveness(drug)
        score += heor_score * 0.3
        
        # 3. 预算影响 (20%)
        budget_score = self._evaluate_budget_impact(drug)
        score += budget_score * 0.2
        
        # 4. 政策导向 (10%)
        policy_score = self._evaluate_policy_fit(drug)
        score += policy_score * 0.1
        
        will_cover = score > 0.55
        
        # 谈判价格估算
        original_price = drug.get("price", 0)
        if self.negotiation_style == NegotiationStyle.AGGRESSIVE:
            negotiation_ratio = 0.5  # 砍价50%
        elif self.negotiation_style == NegotiationStyle.MODERATE:
            negotiation_ratio = 0.65
        else:
            negotiation_ratio = 0.8
        
        negotiated_price = original_price * negotiation_ratio
        
        # 报销比例
        if will_cover:
            if drug.get("is_novel_mechanism", False):
                reimbursement_ratio = 0.7  # 创新药70%报销
            else:
                reimbursement_ratio = 0.8  # 普通药80%报销
        else:
            reimbursement_ratio = 0.0
        
        # 使用限制
        if will_cover and drug.get("is_expensive", False):
            restrictions.append("限定适应症")
            restrictions.append("需要专科处方")
        
        if not will_cover:
            reasons.append("药物经济学证据不足")
            if heor_score < 0.3:
                reasons.append("ICER超出阈值")
        
        return {
            "will_cover": will_cover,
            "negotiation_price": round(negotiated_price, 2),
            "reimbursement_ratio": reimbursement_ratio,
            "restrictions": restrictions,
            "confidence": round(min(abs(score - 0.5) * 2, 1.0), 3),
            "reasoning": "；".join(reasons) if reasons else "综合评估通过",
            "score": round(score, 3),
        }
    
    def _evaluate_clinical_need(self, drug: dict) -> float:
        """临床必要性评估"""
        base = 0.5
        
        # 优先疾病领域
        indication = drug.get("indication_category", "")
        if indication in self.priority_diseases:
            base += 0.2
        
        # 是否有未满足需求
        if drug.get("unmet_need", False):
            base += 0.2
        
        # 是否优于现有疗法
        if drug.get("superior_to_standard", False):
            base += 0.15
        
        return min(max(base, 0.0), 1.0)
    
    def _evaluate_cost_effectiveness(self, drug: dict) -> float:
        """药物经济学评估"""
        icer = drug.get("icer", None)  # 增量成本效果比 (万元/QALY)
        
        if icer is None:
            return 0.5  # 数据不足
        
        if icer <= self.cost_effectiveness_threshold:
            return 0.9
        elif icer <= self.cost_effectiveness_threshold * 1.5:
            return 0.6
        elif icer <= self.cost_effectiveness_threshold * 3:
            return 0.3
        else:
            return 0.1
    
    def _evaluate_budget_impact(self, drug: dict) -> float:
        """预算影响评估"""
        annual_cost = drug.get("estimated_annual_sales", 0)
        budget_impact = annual_cost / self.annual_budget
        
        if budget_impact < 0.001:
            return 0.9
        elif budget_impact < 0.005:
            return 0.7
        elif budget_impact < 0.01:
            return 0.5
        else:
            return 0.3
    
    def _evaluate_policy_fit(self, drug: dict) -> float:
        """政策导向匹配"""
        base = 0.5
        
        if drug.get("is_novel_mechanism", False):
            base += 0.2 * self.innovation_preference
        
        if drug.get("is_domestic", False):
            base += 0.15  # 国产药政策倾斜
        
        if drug.get("orphan_drug", False):
            base += 0.2  # 罕见病用药优先
        
        return min(max(base, 0.0), 1.0)
    
    def simulate_negotiation_round(self, drug: dict, offered_price: float) -> dict:
        """模拟一轮谈判"""
        target_price = drug.get("price", 0) * 0.6  # 医保目标价
        
        if offered_price <= target_price * 1.1:
            return {"accepted": True, "final_price": offered_price}
        else:
            counter_offer = target_price + (offered_price - target_price) * 0.4
            return {
                "accepted": False,
                "counter_offer": round(counter_offer, 2),
                "message": f"建议降价至{counter_offer:.0f}元"
            }
