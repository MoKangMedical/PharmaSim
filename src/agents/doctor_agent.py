"""
PharmaSim - 医生 Agent 模块
模拟不同类型医生在面对新药时的处方决策行为
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class PrescriptionStyle(Enum):
    CONSERVATIVE = "保守型"      # 偏好成熟药品，谨慎使用新药
    PROGRESSIVE = "激进型"       # 积极尝试新药，关注最新循证
    FOLLOWER = "跟风型"          # 跟随KOL和同行意见
    EVIDENCE_BASED = "循证型"    # 严格按指南和RCT数据


class InnovationAttitude(Enum):
    EARLY_ADOPTER = "早期采纳者"    # 上市即尝试
    EARLY_MAJORITY = "早期多数"      # 有初步证据后采纳
    LATE_MAJORITY = "晚期多数"       # 成为标准疗法后采纳
    LAGGARD = "滞后采纳者"           # 极少使用新药


@dataclass
class DoctorAgent:
    """医生智能体 - 模拟真实处方决策"""
    
    agent_id: str
    name: str
    specialty: str                        # 科室
    hospital_tier: str                    # 医院等级: 三甲/二甲/社区
    years_experience: int                 # 从业年数
    prescription_style: PrescriptionStyle # 处方风格
    innovation_attitude: InnovationAttitude
    academic_influence: float             # 学术影响力 0-1
    monthly_patient_volume: int           # 月均患者量
    region: str                           # 地区(省/市)
    
    # 内部状态
    current_prescriptions: dict = field(default_factory=dict)  # {drug_id: 占比}
    memory: List[str] = field(default_factory=list)            # 决策记忆
    
    def evaluate_new_drug(self, drug: dict) -> dict:
        """
        评估新药，返回处方决策
        
        Args:
            drug: 药品属性 dict
                - name: 药品名
                - indication: 适应症
                - efficacy: 疗效数据 (ORR, PFS, OS等)
                - safety: 安全性数据
                - price: 价格
                - competitors: 竞品列表
                - evidence_level: 证据等级
        
        Returns:
            decision: {
                "will_prescribe": bool,
                "adoption_speed": str,       # "immediate" / "1-3months" / "3-6months" / "6-12months" / "never"
                "patient_fit_ratio": float,  # 适合该药的患者比例
                "confidence": float,         # 决策信心 0-1
                "reasoning": str,            # 决策理由
                "conditions": list,          # 使用前提条件
            }
        """
        score = 0.0
        reasons = []
        conditions = []
        
        # 1. 疗效评估 (权重 40%)
        efficacy_score = self._evaluate_efficacy(drug)
        score += efficacy_score * 0.4
        if efficacy_score > 0.7:
            reasons.append("疗效数据优异")
        elif efficacy_score < 0.3:
            reasons.append("疗效数据不足")
            conditions.append("需要更多临床数据")
        
        # 2. 安全性评估 (权重 25%)
        safety_score = self._evaluate_safety(drug)
        score += safety_score * 0.25
        if safety_score < 0.5:
            reasons.append("安全性顾虑")
            conditions.append("需要风险评估方案")
        
        # 3. 价格因素 (权重 20%)
        price_score = self._evaluate_price(drug)
        score += price_score * 0.2
        if price_score < 0.4:
            reasons.append("价格过高影响可及性")
            conditions.append("需要医保支持或患者援助项目")
        
        # 4. 创新采纳倾向 (权重 15%)
        innovation_score = self._innovation_factor(drug)
        score += innovation_score * 0.15
        
        # 决策
        will_prescribe = score > 0.5
        
        # 采纳速度
        if score > 0.8:
            adoption = "immediate"
        elif score > 0.65:
            adoption = "1-3months"
        elif score > 0.5:
            adoption = "3-6months"
        elif score > 0.35:
            adoption = "6-12months"
        else:
            adoption = "never"
            will_prescribe = False
        
        # 患者适配比例
        patient_fit = self._estimate_patient_fit(drug)
        
        return {
            "will_prescribe": will_prescribe,
            "adoption_speed": adoption,
            "patient_fit_ratio": patient_fit,
            "confidence": min(abs(score - 0.5) * 2, 1.0),
            "reasoning": "；".join(reasons) if reasons else "综合评估后做出决策",
            "conditions": conditions,
            "score": round(score, 3),
        }
    
    def _evaluate_efficacy(self, drug: dict) -> float:
        """评估疗效 - 基于风格差异化"""
        efficacy = drug.get("efficacy", {})
        
        # 简化评分: 基于ORR/PFS/OS等指标
        base_score = 0.5
        if efficacy.get("orr"):  # 客观缓解率
            orr = efficacy["orr"]
            base_score = min(orr / 100.0, 1.0)
        if efficacy.get("pfs_improvement"):  # PFS改善
            base_score = max(base_score, efficacy["pfs_improvement"] / 10.0)
        
        # 风格调整
        if self.prescription_style == PrescriptionStyle.EVIDENCE_BASED:
            # 循证型: 更关注RCT数据
            if drug.get("evidence_level") == "RCT":
                base_score *= 1.2
            elif drug.get("evidence_level") == "real_world":
                base_score *= 0.8
        elif self.prescription_style == PrescriptionStyle.PROGRESSIVE:
            # 激进型: 对新机制有加成
            if drug.get("is_novel_mechanism"):
                base_score *= 1.1
        
        return min(max(base_score, 0.0), 1.0)
    
    def _evaluate_safety(self, drug: dict) -> float:
        """评估安全性"""
        safety = drug.get("safety", {})
        base_score = 0.7  # 默认安全性
        
        if safety.get("serious_ae_rate"):
            base_score = max(0.1, 1.0 - safety["serious_ae_rate"] / 100.0)
        
        # 经验丰富的医生对安全性更敏感
        if self.years_experience > 15:
            base_score *= 0.95
        
        return min(max(base_score, 0.0), 1.0)
    
    def _evaluate_price(self, drug: dict) -> float:
        """评估价格可及性"""
        price = drug.get("price", 0)
        competitor_prices = drug.get("competitor_prices", [])
        
        if not competitor_prices or price == 0:
            return 0.5
        
        avg_competitor_price = sum(competitor_prices) / len(competitor_prices)
        
        # 价格比
        price_ratio = price / avg_competitor_price if avg_competitor_price > 0 else 1.0
        
        if price_ratio <= 0.8:
            return 0.9  # 比竞品便宜
        elif price_ratio <= 1.2:
            return 0.7  # 价格相当
        elif price_ratio <= 2.0:
            return 0.4  # 明显更贵
        else:
            return 0.2  # 贵很多
    
    def _innovation_factor(self, drug: dict) -> float:
        """创新采纳因子"""
        attitude_scores = {
            InnovationAttitude.EARLY_ADOPTER: 0.9,
            InnovationAttitude.EARLY_MAJORITY: 0.7,
            InnovationAttitude.LATE_MAJORITY: 0.4,
            InnovationAttitude.LAGGARD: 0.2,
        }
        return attitude_scores.get(self.innovation_attitude, 0.5)
    
    def _estimate_patient_fit(self, drug: dict) -> float:
        """估算适合该药的患者比例"""
        # 基础: 科室匹配度
        specialty_match = drug.get("target_specialties", [])
        if self.specialty in specialty_match:
            base_fit = 0.3  # 科室匹配, 30%患者可能适合
        else:
            base_fit = 0.05  # 科室不匹配
        
        # 医院等级调整: 三甲医院患者更复杂, 更可能适合新药
        if self.hospital_tier == "三甲":
            base_fit *= 1.3
        elif self.hospital_tier == "社区":
            base_fit *= 0.7
        
        return min(max(base_fit, 0.0), 1.0)
    
    def update_prescription(self, drug_id: str, proportion: float):
        """更新处方比例"""
        self.current_prescriptions[drug_id] = proportion
        # 记忆
        self.memory.append(f"处方{drug_id}: {proportion:.1%}")
    
    def to_dict(self) -> dict:
        """序列化"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialty": self.specialty,
            "hospital_tier": self.hospital_tier,
            "years_experience": self.years_experience,
            "prescription_style": self.prescription_style.value,
            "innovation_attitude": self.innovation_attitude.value,
            "academic_influence": self.academic_influence,
            "monthly_patient_volume": self.monthly_patient_volume,
            "region": self.region,
        }
