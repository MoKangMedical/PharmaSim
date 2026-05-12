"""
PharmaSim - Agent工厂模块
批量生成1000个专业Agent，覆盖10个维度
"""

import random
import uuid
from typing import List, Dict

from agents.doctor_agent import DoctorAgent, PrescriptionStyle, InnovationAttitude
from agents.patient_agent import PatientAgent, InsuranceType, EconomicLevel, InformationSource
from agents.payer_agent import PayerAgent, FundStatus, NegotiationStyle
from agents.pharmacology_agent import PharmacologyExpertAgent, PharmacologyFocus, ExpertiseLevel as PharmLevel
from agents.epidemiology_agent import EpidemiologyExpertAgent, EpiFocus, ExpertiseLevel as EpiLevel
from agents.pharmacoeconomics_agent import PharmacoeconomicsExpertAgent, HEORFocus, ExpertiseLevel as HEORLevel
from agents.insurance_expert_agent import InsuranceExpertAgent, InsuranceFocus, ExpertiseLevel as InsLevel
from agents.clinical_expert_agent import ClinicalExpertAgent, ClinicalFocus, ExpertiseLevel as ClinLevel
from agents.pricing_expert_agent import PricingExpertAgent, PricingFocus, ExpertiseLevel as PriceLevel
from agents.market_expert_agent import MarketExpertAgent, MarketFocus, ExpertiseLevel as MarketLevel


# 中国地区分布（加权）
REGIONS = [
    "北京", "上海", "广州", "深圳",       # 一线城市
    "成都", "武汉", "杭州", "南京",        # 新一线
    "重庆", "天津", "西安", "长沙",        # 新一线
    "郑州", "沈阳", "青岛", "济南",        # 二线
    "哈尔滨", "大连", "厦门", "合肥",      # 二线
    "福州", "昆明", "南宁", "贵阳",        # 二线
    "兰州", "太原", "石家庄", "南昌",      # 三线
    "呼和浩特", "乌鲁木齐", "银川", "海口", # 三线
]

REGION_WEIGHTS = [8, 8, 6, 6] + [4] * 8 + [2] * 12 + [1] * 8

SPECIALTIES = {
    "肿瘤": ["肿瘤科", "呼吸科", "胸外科", "消化科", "乳腺外科", "血液科", "泌尿外科", "妇科肿瘤"],
    "慢性病": ["心内科", "内分泌科", "肾内科", "神经内科", "消化科"],
    "精神疾病": ["精神科", "心理科", "神经内科"],
    "自身免疫": ["风湿免疫科", "皮肤科", "消化科"],
    "感染性疾病": ["感染科", "呼吸科", "肝病科"],
    "罕见病": ["儿科", "神经内科", "血液科", "遗传科"],
}

HOSPITAL_TIERS = ["三甲", "三甲", "三甲", "二甲", "二甲", "社区"]

INSTITUTIONS_PHARM = ["学术", "学术", "药企", "CRO", "监管"]
INSTITUTIONS_EPI = ["学术", "学术", "疾控", "药企", "WHO"]
INSTITUTIONS_HEOR = ["学术", "学术", "药企", "HTA机构", "咨询"]
INSTITUTIONS_INS = ["医保局", "医保局", "学术", "药企", "咨询"]
INSTITUTIONS_CLIN = ["三甲", "三甲", "二甲", "学术", "药企"]
INSTITUTIONS_PRICE = ["药企", "药企", "咨询", "学术"]
INSTITUTIONS_MKT = ["药企", "药企", "咨询", "投资", "学术"]


class AgentFactory:
    """1000 Agent 工厂 - 生成多维度专家体系"""

    def __init__(self, drug: dict, num_agents: int = 1000, random_seed: int = 42):
        self.drug = drug
        self.num_agents = num_agents
        random.seed(random_seed)

        # 按比例分配Agent (总数=num_agents)
        # 基础比例: 医生22%, 患者56%, 各类专家共22%
        if num_agents < 100:
            num_agents = 100  # 最低保障

        n_patients = max(10, int(num_agents * 0.56))
        n_doctors = max(5, int(num_agents * 0.22))
        n_pharma = max(2, int(num_agents * 0.044))
        n_epi = max(2, int(num_agents * 0.044))
        n_heor = max(2, int(num_agents * 0.044))
        n_ins = max(1, int(num_agents * 0.022))
        n_clin = max(1, int(num_agents * 0.022))
        n_price = max(1, int(num_agents * 0.022))
        n_mkt = max(1, int(num_agents * 0.022))

        self.allocation = {
            "doctors": n_doctors,
            "patients": n_patients,
            "pharmacology": n_pharma,
            "epidemiology": n_epi,
            "pharmacoeconomics": n_heor,
            "insurance": n_ins,
            "clinical": n_clin,
            "pricing": n_price,
            "market": n_mkt,
        }
        self.allocation["payer"] = 1

    def create_all_agents(self) -> dict:
        """生成全部Agent"""
        print(f"🏭 Agent工厂启动 - 目标: {self.num_agents}个Agent")

        agents = {
            "doctors": self._create_doctors(),
            "patients": self._create_patients(),
            "pharmacology_experts": self._create_pharmacology_experts(),
            "epidemiology_experts": self._create_epidemiology_experts(),
            "pharmacoeconomics_experts": self._create_pharmacoeconomics_experts(),
            "insurance_experts": self._create_insurance_experts(),
            "clinical_experts": self._create_clinical_experts(),
            "pricing_experts": self._create_pricing_experts(),
            "market_experts": self._create_market_experts(),
            "payer": self._create_payer(),
        }

        total = sum(len(v) if isinstance(v, list) else 1 for v in agents.values())
        print(f"✅ Agent生成完成: 共{total}个")
        for category, items in agents.items():
            count = len(items) if isinstance(items, list) else 1
            print(f"   {category}: {count}")

        return agents

    def _get_regions(self, n: int) -> List[str]:
        return random.choices(REGIONS, weights=REGION_WEIGHTS, k=n)

    def _get_specialties(self) -> List[str]:
        indication = self.drug.get("indication_category", "肿瘤")
        return SPECIALTIES.get(indication, SPECIALTIES["肿瘤"])

    def _create_doctors(self) -> List[DoctorAgent]:
        n = self.allocation["doctors"]
        specialties = self._get_specialties()
        styles = list(PrescriptionStyle)
        attitudes = list(InnovationAttitude)
        regions = self._get_regions(n)

        doctors = []
        for i in range(n):
            doc = DoctorAgent(
                agent_id=f"doc-{uuid.uuid4().hex[:8]}",
                name=f"医生_{i+1}",
                specialty=random.choice(specialties),
                hospital_tier=random.choice(HOSPITAL_TIERS),
                years_experience=random.randint(3, 35),
                prescription_style=random.choice(styles),
                innovation_attitude=random.choice(attitudes),
                academic_influence=random.betavariate(2, 5),
                monthly_patient_volume=random.randint(50, 300),
                region=regions[i],
            )
            doctors.append(doc)
        return doctors

    def _create_patients(self) -> List[PatientAgent]:
        n = self.allocation["patients"]
        regions = self._get_regions(n)
        indication = self.drug.get("indication", "肿瘤")

        patients = []
        for i in range(n):
            pt = PatientAgent(
                agent_id=f"pt-{uuid.uuid4().hex[:8]}",
                age=random.randint(18, 80),
                gender=random.choice(["男", "女"]),
                disease_type=indication,
                disease_stage=random.choice(["早期", "中期", "晚期"]),
                insurance_type=random.choice(list(InsuranceType)),
                economic_level=random.choice(list(EconomicLevel)),
                information_source=random.choice(list(InformationSource)),
                adherence_score=random.betavariate(3, 2),
                brand_preference=random.choice(["original", "generic", "indifferent"]),
                region=regions[i],
            )
            patients.append(pt)
        return patients

    def _create_pharmacology_experts(self) -> List[PharmacologyExpertAgent]:
        n = self.allocation["pharmacology"]
        focuses = list(PharmacologyFocus)
        levels = list(PharmLevel)
        regions = self._get_regions(n)

        experts = []
        for i in range(n):
            exp = PharmacologyExpertAgent(
                agent_id=f"pharm-{uuid.uuid4().hex[:8]}",
                name=f"药物学专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                therapeutic_area=self.drug.get("indication_category", "肿瘤"),
                years_experience=random.randint(3, 30),
                publication_count=random.randint(0, 100),
                has_ind_experience=random.random() < 0.4,
                institution_type=random.choice(INSTITUTIONS_PHARM),
            )
            experts.append(exp)
        return experts

    def _create_epidemiology_experts(self) -> List[EpidemiologyExpertAgent]:
        n = self.allocation["epidemiology"]
        focuses = list(EpiFocus)
        levels = list(EpiLevel)
        regions = self._get_regions(n)

        experts = []
        for i in range(n):
            exp = EpidemiologyExpertAgent(
                agent_id=f"epi-{uuid.uuid4().hex[:8]}",
                name=f"流行病学专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                disease_expertise=self.drug.get("indication_category", "肿瘤"),
                years_experience=random.randint(3, 30),
                region_expertise=regions[i],
                has_surveillance_experience=random.random() < 0.5,
                institution_type=random.choice(INSTITUTIONS_EPI),
            )
            experts.append(exp)
        return experts

    def _create_pharmacoeconomics_experts(self) -> List[PharmacoeconomicsExpertAgent]:
        n = self.allocation["pharmacoeconomics"]
        focuses = list(HEORFocus)
        levels = list(HEORLevel)

        experts = []
        for i in range(n):
            exp = PharmacoeconomicsExpertAgent(
                agent_id=f"heor-{uuid.uuid4().hex[:8]}",
                name=f"药物经济学专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                years_experience=random.randint(3, 25),
                wtp_threshold=random.choice([1.0, 1.5, 2.0, 3.0, 5.0]),
                modeling_expertise=random.choice(["markov", "decision_tree", "microsimulation"]),
                institution_type=random.choice(INSTITUTIONS_HEOR),
                has_hta_submission=random.random() < 0.4,
            )
            experts.append(exp)
        return experts

    def _create_insurance_experts(self) -> List[InsuranceExpertAgent]:
        n = self.allocation["insurance"]
        focuses = list(InsuranceFocus)
        levels = list(InsLevel)
        regions = self._get_regions(n)

        experts = []
        for i in range(n):
            exp = InsuranceExpertAgent(
                agent_id=f"ins-{uuid.uuid4().hex[:8]}",
                name=f"医保专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                years_experience=random.randint(3, 25),
                region_expertise=regions[i],
                has_negotiation_experience=random.random() < 0.3,
                institution_type=random.choice(INSTITUTIONS_INS),
                fund_region=regions[i],
            )
            experts.append(exp)
        return experts

    def _create_clinical_experts(self) -> List[ClinicalExpertAgent]:
        n = self.allocation["clinical"]
        focuses = list(ClinicalFocus)
        levels = list(ClinLevel)
        specialties = self._get_specialties()

        experts = []
        for i in range(n):
            exp = ClinicalExpertAgent(
                agent_id=f"clin-{uuid.uuid4().hex[:8]}",
                name=f"临床专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                specialty=random.choice(specialties),
                years_experience=random.randint(5, 35),
                publication_count=random.randint(0, 200),
                has_kol_status=random.random() < 0.15,
                institution_type=random.choice(INSTITUTIONS_CLIN),
            )
            experts.append(exp)
        return experts

    def _create_pricing_experts(self) -> List[PricingExpertAgent]:
        n = self.allocation["pricing"]
        focuses = list(PricingFocus)
        levels = list(PriceLevel)

        experts = []
        for i in range(n):
            exp = PricingExpertAgent(
                agent_id=f"price-{uuid.uuid4().hex[:8]}",
                name=f"定价专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                years_experience=random.randint(3, 25),
                therapeutic_expertise=self.drug.get("indication_category", "肿瘤"),
                has_launch_experience=random.random() < 0.4,
                institution_type=random.choice(INSTITUTIONS_PRICE),
            )
            experts.append(exp)
        return experts

    def _create_market_experts(self) -> List[MarketExpertAgent]:
        n = self.allocation["market"]
        focuses = list(MarketFocus)
        levels = list(MarketLevel)

        experts = []
        for i in range(n):
            exp = MarketExpertAgent(
                agent_id=f"mkt-{uuid.uuid4().hex[:8]}",
                name=f"市场专家_{i+1}",
                focus=random.choice(focuses),
                expertise_level=random.choice(levels),
                years_experience=random.randint(3, 25),
                therapeutic_expertise=self.drug.get("indication_category", "肿瘤"),
                has_launch_experience=random.random() < 0.4,
                institution_type=random.choice(INSTITUTIONS_MKT),
                company_type=random.choice(["MNC", "本土大型", "Biotech", "独立"]),
            )
            experts.append(exp)
        return experts

    def _create_payer(self) -> PayerAgent:
        return PayerAgent(
            fund_status=random.choice(list(FundStatus)),
            negotiation_style=random.choice(list(NegotiationStyle)),
        )

    def get_summary(self) -> dict:
        """获取Agent分配摘要"""
        return {
            "total_agents": self.num_agents,
            "allocation": self.allocation,
            "dimensions": [
                "医生处方决策", "患者用药决策",
                "药物学评估", "流行病学评估", "药物经济学评估",
                "医保准入评估", "临床价值评估", "定价策略评估", "市场潜力评估",
            ],
            "regions_covered": len(set(self._get_regions(100))),
        }
