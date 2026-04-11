"""
PharmaSim - 核心模拟引擎
协调多智能体模拟药品上市后的市场表现
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, field

from agents.doctor_agent import DoctorAgent, PrescriptionStyle, InnovationAttitude
from agents.patient_agent import PatientAgent, InsuranceType, EconomicLevel, InformationSource
from agents.payer_agent import PayerAgent, FundStatus, NegotiationStyle


@dataclass
class SimulationConfig:
    """模拟配置"""
    drug: dict                              # 目标药品属性
    num_doctors: int = 500                  # 医生Agent数量
    num_patients: int = 5000                # 患者Agent数量
    simulation_months: int = 24             # 模拟时长(月)
    random_seed: int = 42                   # 随机种子
    region_focus: List[str] = field(default_factory=lambda: ["北京", "上海", "广州", "深圳", "成都", "武汉"])


@dataclass
class MonthlySnapshot:
    """月度快照"""
    month: int
    prescription_volume: int
    market_penetration: float
    revenue: float
    doctor_adoption_rate: float
    patient_satisfaction: float
    insurance_coverage: bool
    new_prescribers: int
    cumulative_prescribers: int
    competitor_response: str = ""


class SimulationEngine:
    """药品上市模拟引擎"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.drug = config.drug
        self.results: List[MonthlySnapshot] = []
        self.doctors: List[DoctorAgent] = []
        self.patients: List[PatientAgent] = []
        self.payer = PayerAgent()
        
        random.seed(config.random_seed)
    
    def initialize_agents(self):
        """初始化所有Agent"""
        self._create_doctor_agents()
        self._create_patient_agents()
        self._configure_payer()
        print(f"✅ 初始化完成: {len(self.doctors)} 医生 + {len(self.patients)} 患者 + 1 医保方")
    
    def _create_doctor_agents(self):
        """批量生成医生Agent"""
        specialties = self.drug.get("target_specialties", ["肿瘤科", "内科"])
        tiers = ["三甲", "三甲", "三甲", "二甲", "二甲", "社区"]  # 三甲权重更高
        styles = list(PrescriptionStyle)
        attitudes = list(InnovationAttitude)
        
        for i in range(self.config.num_doctors):
            doctor = DoctorAgent(
                agent_id=f"doc-{uuid.uuid4().hex[:8]}",
                name=f"医生_{i+1}",
                specialty=random.choice(specialties),
                hospital_tier=random.choice(tiers),
                years_experience=random.randint(3, 35),
                prescription_style=random.choice(styles),
                innovation_attitude=random.choice(attitudes),
                academic_influence=random.betavariate(2, 5),  # 偏低分布
                monthly_patient_volume=random.randint(50, 300),
                region=random.choice(self.config.region_focus),
            )
            self.doctors.append(doctor)
    
    def _create_patient_agents(self):
        """批量生成患者Agent"""
        disease_types = [self.drug.get("indication", "肿瘤")]
        
        for i in range(self.config.num_patients):
            patient = PatientAgent(
                agent_id=f"pt-{uuid.uuid4().hex[:8]}",
                age=random.randint(18, 80),
                gender=random.choice(["男", "女"]),
                disease_type=random.choice(disease_types),
                disease_stage=random.choice(["早期", "中期", "晚期"]),
                insurance_type=random.choice(list(InsuranceType)),
                economic_level=random.choice(list(EconomicLevel)),
                information_source=random.choice(list(InformationSource)),
                adherence_score=random.betavariate(3, 2),  # 偏高
                brand_preference=random.choice(["original", "generic", "indifferent"]),
                region=random.choice(self.config.region_focus),
            )
            self.patients.append(patient)
    
    def _configure_payer(self):
        """配置医保方"""
        self.payer = PayerAgent(
            fund_status=FundStatus.BALANCED,
            negotiation_style=NegotiationStyle.MODERATE,
        )
    
    def run(self) -> dict:
        """
        运行完整模拟
        
        Returns:
            {
                "drug_name": str,
                "simulation_months": int,
                "monthly_snapshots": [MonthlySnapshot, ...],
                "summary": {...},
            }
        """
        print(f"🚀 开始模拟: {self.drug.get('name', '未知药品')}")
        print(f"   模拟时长: {self.config.simulation_months} 个月")
        
        # 初始化
        self.initialize_agents()
        
        # 医保评估(第0个月)
        payer_decision = self.payer.evaluate_reimbursement(self.drug)
        insurance_coverage_month = 6  # 假设第6个月纳入医保
        
        # 医生初始评估
        initial_adopters = []
        for doc in self.doctors:
            decision = doc.evaluate_new_drug(self.drug)
            if decision["will_prescribe"] and decision["adoption_speed"] in ["immediate", "1-3months"]:
                initial_adopters.append(doc)
        
        # 逐月模拟
        cumulative_prescribers = 0
        adopted_doctors = set()
        
        for month in range(1, self.config.simulation_months + 1):
            snapshot = self._simulate_month(
                month=month,
                adopted_doctors=adopted_doctors,
                insurance_active=(month >= insurance_coverage_month and payer_decision["will_cover"]),
                payer_decision=payer_decision,
            )
            self.results.append(snapshot)
            
            # 进度
            if month % 3 == 0:
                print(f"   📅 第{month}月: 处方量={snapshot.prescription_volume}, 渗透率={snapshot.market_penetration:.1%}")
        
        # 汇总
        summary = self._generate_summary()
        print(f"✅ 模拟完成!")
        
        return {
            "drug_name": self.drug.get("name", "未知"),
            "simulation_months": self.config.simulation_months,
            "monthly_snapshots": [self._snapshot_to_dict(s) for s in self.results],
            "summary": summary,
            "payer_decision": payer_decision,
            "config": {
                "num_doctors": self.config.num_doctors,
                "num_patients": self.config.num_patients,
                "random_seed": self.config.random_seed,
            }
        }
    
    def _simulate_month(self, month: int, adopted_doctors: set,
                         insurance_active: bool, payer_decision: dict) -> MonthlySnapshot:
        """模拟单月"""
        
        # 1. 医生采纳过程
        for doc in self.doctors:
            if doc.agent_id in adopted_doctors:
                continue
            
            decision = doc.evaluate_new_drug(self.drug)
            adopt_probability = self._calculate_adoption_probability(doc, month, insurance_active, decision)
            
            if random.random() < adopt_probability:
                adopted_doctors.add(doc.agent_id)
        
        # 2. 计算处方量
        adoption_rate = len(adopted_doctors) / len(self.doctors)
        total_potential_patients = sum(d.monthly_patient_volume for d in self.doctors if d.agent_id in adopted_doctors)
        patient_fit_ratio = 0.15  # 平均适配比例
        prescription_volume = int(total_potential_patients * patient_fit_ratio * 0.3)  # 30%转换率
        
        # 3. 渗透率
        total_addressable = sum(d.monthly_patient_volume for d in self.doctors) * patient_fit_ratio
        market_penetration = prescription_volume / total_addressable if total_addressable > 0 else 0
        
        # 4. 收入
        price = self.drug.get("price", 0)
        if insurance_active:
            effective_price = payer_decision.get("negotiation_price", price)
        else:
            effective_price = price
        revenue = prescription_volume * effective_price
        
        # 5. 患者满意度
        patient_satisfaction = 0.7 + random.uniform(-0.1, 0.1)
        
        # 6. 竞品反应
        competitor_response = self._simulate_competitor_response(month, market_penetration)
        
        return MonthlySnapshot(
            month=month,
            prescription_volume=prescription_volume,
            market_penetration=round(market_penetration, 4),
            revenue=revenue,
            doctor_adoption_rate=round(adoption_rate, 4),
            patient_satisfaction=round(patient_satisfaction, 3),
            insurance_coverage=insurance_active,
            new_prescribers=len(adopted_doctors) - (self.results[-1].cumulative_prescribers if self.results else 0),
            cumulative_prescribers=len(adopted_doctors),
            competitor_response=competitor_response,
        )
    
    def _calculate_adoption_probability(self, doctor: DoctorAgent, month: int,
                                         insurance_active: bool, decision: dict) -> float:
        """计算医生当月采纳概率"""
        base_prob = 0.02  # 基础月采纳率 2%
        
        # 纳入医保加速采纳
        if insurance_active:
            base_prob *= 1.5
        
        # 早期采纳者更快
        if doctor.innovation_attitude == InnovationAttitude.EARLY_ADOPTER:
            if month <= 3:
                base_prob *= 3.0
        elif doctor.innovation_attitude == InnovationAttitude.EARLY_MAJORITY:
            if month > 3:
                base_prob *= 2.0
        elif doctor.innovation_attitude == InnovationAttitude.LATE_MAJORITY:
            if month > 6:
                base_prob *= 1.5
            else:
                base_prob *= 0.3
        else:  # LAGGARD
            if month > 12:
                base_prob *= 1.0
            else:
                base_prob *= 0.05
        
        # KOL影响: 学术影响力高的医生采纳后, 带动其他人
        kol_count = sum(1 for d in self.doctors 
                       if d.agent_id in {doc.agent_id for doc in self.doctors} 
                       and d.academic_influence > 0.7)
        if kol_count > 5:
            base_prob *= (1 + 0.05 * kol_count)
        
        # 模拟得分加成
        if decision.get("score", 0) > 0.6:
            base_prob *= 1.3
        
        return min(base_prob, 0.5)  # 上限50%
    
    def _simulate_competitor_response(self, month: int, penetration: float) -> str:
        """模拟竞品反应"""
        if penetration > 0.1 and month == 3:
            return "竞品A启动降价促销"
        elif penetration > 0.2 and month == 6:
            return "竞品B发布新适应症数据"
        elif penetration > 0.3 and month == 9:
            return "竞品C申请医保谈判"
        return ""
    
    def _generate_summary(self) -> dict:
        """生成模拟汇总"""
        if not self.results:
            return {}
        
        peak = max(self.results, key=lambda s: s.prescription_volume)
        final = self.results[-1]
        year1_revenue = sum(s.revenue for s in self.results[:12])
        year2_revenue = sum(s.revenue for s in self.results[12:24]) if len(self.results) >= 24 else 0
        
        return {
            "peak_month": peak.month,
            "peak_prescription_volume": peak.prescription_volume,
            "peak_market_penetration": peak.market_penetration,
            "final_adoption_rate": final.doctor_adoption_rate,
            "final_market_penetration": final.market_penetration,
            "year1_revenue": year1_revenue,
            "year2_revenue": year2_revenue,
            "total_revenue": year1_revenue + year2_revenue,
            "insurace_impact": "显著" if any(s.insurance_coverage for s in self.results) else "无",
            "avg_patient_satisfaction": round(sum(s.patient_satisfaction for s in self.results) / len(self.results), 3),
        }
    
    @staticmethod
    def _snapshot_to_dict(s: MonthlySnapshot) -> dict:
        return {
            "month": s.month,
            "prescription_volume": s.prescription_volume,
            "market_penetration": s.market_penetration,
            "revenue": s.revenue,
            "doctor_adoption_rate": s.doctor_adoption_rate,
            "patient_satisfaction": s.patient_satisfaction,
            "insurance_coverage": s.insurance_coverage,
            "new_prescribers": s.new_prescribers,
            "cumulative_prescribers": s.cumulative_prescribers,
            "competitor_response": s.competitor_response,
        }
