"""
PharmaSim API Server
完整的后端API服务 - FastAPI
"""

import sys, os, json, uuid, time, random, sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents.doctor_agent import DoctorAgent, PrescriptionStyle, InnovationAttitude
from agents.patient_agent import PatientAgent, InsuranceType, EconomicLevel, InformationSource
from agents.payer_agent import PayerAgent, FundStatus, NegotiationStyle
from simulation.simulation_engine import SimulationEngine, SimulationConfig

# ──────────────────────────────────────────────
# 数据库
# ──────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "pharmsim.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS drugs (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        generic_name TEXT,
        company TEXT,
        indication TEXT,
        indication_category TEXT,
        mechanism TEXT,
        phase TEXT,
        price REAL DEFAULT 0,
        is_listed INTEGER DEFAULT 0,
        is_novel_mechanism INTEGER DEFAULT 0,
        is_domestic INTEGER DEFAULT 1,
        is_expensive INTEGER DEFAULT 0,
        orphan_drug INTEGER DEFAULT 0,
        data_json TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    
    CREATE TABLE IF NOT EXISTS simulations (
        id TEXT PRIMARY KEY,
        drug_id TEXT,
        drug_name TEXT,
        status TEXT DEFAULT 'pending',
        config_json TEXT,
        result_json TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        completed_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simulation_id TEXT,
        agent_name TEXT,
        agent_role TEXT,
        message TEXT,
        reasoning TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)
    conn.commit()
    conn.close()

# ──────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────
class DrugCreate(BaseModel):
    name: str
    generic_name: str = ""
    company: str = ""
    indication: str = ""
    indication_category: str = "肿瘤"
    mechanism: str = ""
    phase: str = "已上市"
    price: float = 0
    is_listed: bool = True
    is_novel_mechanism: bool = False
    is_domestic: bool = True
    is_expensive: bool = False
    orphan_drug: bool = False
    target_specialties: List[str] = []
    competitor_prices: List[float] = []
    efficacy: dict = {}
    safety: dict = {}
    dosing_convenience: float = 0.7

class SimulationRequest(BaseModel):
    drug_id: Optional[str] = None
    drug: Optional[DrugCreate] = None
    num_doctors: int = 500
    num_patients: int = 5000
    simulation_months: int = 24
    regions: List[str] = ["北京", "上海", "广州", "深圳", "成都", "武汉"]
    include_competitors: bool = True
    enable_insurance_simulation: bool = True
    agent_reasoning: bool = True

class AgentMessage(BaseModel):
    role: str
    content: str
    reasoning: str = ""
    timestamp: str = ""

class SimulationStatus(BaseModel):
    id: str
    status: str
    progress: float = 0
    current_step: str = ""
    agent_messages: List[AgentMessage] = []

# ──────────────────────────────────────────────
# 预置药品库
# ──────────────────────────────────────────────
PRESET_DRUGS = [
    {
        "id": "preset-001",
        "name": "帕博利珠单抗(Keytruda)",
        "generic_name": "Pembrolizumab",
        "company": "默沙东(MSD)",
        "indication": "非小细胞肺癌",
        "indication_category": "肿瘤",
        "mechanism": "PD-1抑制剂",
        "phase": "已上市",
        "price": 17918,
        "is_listed": True,
        "is_novel_mechanism": False,
        "is_domestic": False,
        "is_expensive": True,
        "orphan_drug": False,
        "target_specialties": ["肿瘤科", "呼吸科", "胸外科"],
        "competitor_prices": [15000, 19800, 12000, 9800],
        "efficacy": {"orr": 44.8, "pfs_months": 10.3, "os_months": 26.3},
        "safety": {"serious_ae_rate": 13.5, "discontinuation_rate": 7.0},
    },
    {
        "id": "preset-002",
        "name": "司美格鲁肽(Ozempic)",
        "generic_name": "Semaglutide",
        "company": "诺和诺德(Novo Nordisk)",
        "indication": "2型糖尿病",
        "indication_category": "代谢",
        "mechanism": "GLP-1受体激动剂",
        "phase": "已上市",
        "price": 1180,
        "is_listed": True,
        "is_novel_mechanism": False,
        "is_domestic": False,
        "is_expensive": False,
        "orphan_drug": False,
        "target_specialties": ["内分泌科", "心内科"],
        "competitor_prices": [890, 650, 1200],
        "efficacy": {"hba1c_reduction": 1.8, "weight_loss_kg": 6.2},
        "safety": {"serious_ae_rate": 3.2, "discontinuation_rate": 4.5},
    },
    {
        "id": "preset-003",
        "name": "阿兹夫定(Azvudine)",
        "generic_name": "阿兹夫定片",
        "company": "真实生物",
        "indication": "COVID-19",
        "indication_category": "感染",
        "mechanism": "RdRp抑制剂",
        "phase": "已上市",
        "price": 270,
        "is_listed": True,
        "is_novel_mechanism": True,
        "is_domestic": True,
        "is_expensive": False,
        "orphan_drug": False,
        "target_specialties": ["感染科", "呼吸科"],
        "competitor_prices": [600, 298, 2300],
        "efficacy": {"viral_clearance_days": 5.2, "symptom_resolution": 7.1},
        "safety": {"serious_ae_rate": 2.1, "discontinuation_rate": 1.8},
    },
    {
        "id": "preset-004",
        "name": "泽布替尼(Zanubrutinib)",
        "generic_name": "泽布替尼胶囊",
        "company": "百济神州",
        "indication": "套细胞淋巴瘤",
        "indication_category": "血液肿瘤",
        "mechanism": "BTK抑制剂",
        "phase": "已上市",
        "price": 8600,
        "is_listed": True,
        "is_novel_mechanism": True,
        "is_domestic": True,
        "is_expensive": True,
        "orphan_drug": False,
        "target_specialties": ["血液科", "肿瘤科"],
        "competitor_prices": [12000, 9800, 7500],
        "efficacy": {"orr": 83.0, "pfs_months": 35.6},
        "safety": {"serious_ae_rate": 11.5, "discontinuation_rate": 6.2},
    },
    {
        "id": "preset-005",
        "name": "仑伐替尼(Lenvatinib)",
        "generic_name": "甲磺酸仑伐替尼胶囊",
        "company": "卫材(Eisai)",
        "indication": "肝细胞癌",
        "indication_category": "肿瘤",
        "mechanism": "多靶点TKI",
        "phase": "已上市",
        "price": 16800,
        "is_listed": True,
        "is_novel_mechanism": False,
        "is_domestic": False,
        "is_expensive": True,
        "orphan_drug": False,
        "target_specialties": ["肝胆外科", "肿瘤科", "消化科"],
        "competitor_prices": [12000, 5800, 22000],
        "efficacy": {"orr": 24.1, "os_months": 13.6},
        "safety": {"serious_ae_rate": 17.4, "discontinuation_rate": 10.5},
    },
    {
        "id": "preset-006",
        "name": "诺西那生钠(Spinraza)",
        "generic_name": "Nusinersen",
        "company": "渤健(Biogen)",
        "indication": "脊髓性肌萎缩症",
        "indication_category": "罕见病",
        "mechanism": "反义寡核苷酸",
        "phase": "已上市",
        "price": 699700,
        "is_listed": True,
        "is_novel_mechanism": True,
        "is_domestic": False,
        "is_expensive": True,
        "orphan_drug": True,
        "target_specialties": ["神经内科", "儿科"],
        "competitor_prices": [2120000, 580000],
        "efficacy": {"motor_improvement": 65.0, "survival_benefit": True},
        "safety": {"serious_ae_rate": 5.8, "discontinuation_rate": 2.1},
    },
    {
        "id": "preset-007",
        "name": "【待上市】XY-001(示例新药)",
        "generic_name": "示例新分子实体",
        "company": "示例生物科技",
        "indication": "非小细胞肺癌(2线)",
        "indication_category": "肿瘤",
        "mechanism": "EGFR/c-MET双抗",
        "phase": "III期临床",
        "price": 25000,
        "is_listed": False,
        "is_novel_mechanism": True,
        "is_domestic": True,
        "is_expensive": True,
        "orphan_drug": False,
        "target_specialties": ["肿瘤科", "呼吸科"],
        "competitor_prices": [15000, 18000, 22000],
        "efficacy": {"orr": 52.0, "pfs_months": 12.5, "os_months": 28.0},
        "safety": {"serious_ae_rate": 15.0, "discontinuation_rate": 8.0},
    },
]

# ──────────────────────────────────────────────
# LLM Agent 推理引擎
# ──────────────────────────────────────────────
MIMO_ENDPOINT = "https://api.xiaomimimo.com/v1"
MIMO_MODEL = "mimo-v2-pro"

async def agent_reason(role: str, task: str, context: dict) -> dict:
    """调用MiMo API进行Agent推理"""
    import httpx
    
    system_prompts = {
        "market_analyst": "你是PharmaSim的市场分析专家。基于给定数据，进行深入的医药市场分析。输出结构化分析结论。",
        "clinical_expert": "你是PharmaSim的临床医学专家。从临床角度分析药品的处方行为和医生采纳模式。",
        "health_economist": "你是PharmaSim的药物经济学专家。分析医保准入、定价策略和成本效果。",
        "patient_analyst": "你是PharmaSim的患者行为分析师。分析患者就医决策、用药偏好和依从性。",
        "channel_strategist": "你是PharmaSim的渠道策略师。分析药品在医院、药房、电商等渠道的流通策略。",
        "regulatory_analyst": "你是PharmaSim的政策法规分析师。分析监管政策对药品市场的影响。",
        "calibrator": "你是PharmaSim的数据校准专家。基于真实世界数据校准模拟参数。",
        "orchestrator": "你是PharmaSim的模拟编排师。协调各Agent工作，生成最终预测报告。",
    }
    
    prompt = system_prompts.get(role, "你是PharmaSim的AI专家。请分析以下任务。")
    
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"任务: {task}\n\n上下文数据:\n{json.dumps(context, ensure_ascii=False, indent=2)[:3000]}"}
    ]
    
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{MIMO_ENDPOINT}/chat/completions",
                json={"model": MIMO_MODEL, "messages": messages, "temperature": 0.7, "max_tokens": 1000},
                headers={"Content-Type": "application/json"}
            )
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return {"success": True, "reasoning": content, "role": role}
    except Exception as e:
        return {"success": False, "error": str(e), "role": role}

# ──────────────────────────────────────────────
# 完整模拟引擎（增强版）
# ──────────────────────────────────────────────
class EnhancedSimulationEngine(SimulationEngine):
    """增强版模拟引擎 - 带Agent推理和完整输出"""
    
    def __init__(self, config, enable_reasoning=True):
        super().__init__(config)
        self.enable_reasoning = enable_reasoning
        self.agent_messages = []
        self.competitor_actions = []
        self.regional_results = {}
    
    async def run_with_agents(self) -> dict:
        """带Agent推理的完整模拟"""
        sim_id = str(uuid.uuid4())[:12]
        
        # 1. 市场分析Agent - 分析竞争格局
        if self.enable_reasoning:
            market_analysis = await agent_reason("market_analyst", 
                "分析目标药品的竞争格局和市场机会", {
                    "drug": self.drug,
                    "competitors": self.drug.get("competitor_prices", []),
                })
            self.agent_messages.append({
                "role": "market_analyst",
                "content": market_analysis.get("reasoning", "市场分析完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 2. 临床专家Agent - 评估处方行为
        if self.enable_reasoning:
            clinical_analysis = await agent_reason("clinical_expert",
                "评估目标药品在医生群体中的处方意愿和采纳模式", {
                    "drug": self.drug,
                    "efficacy": self.drug.get("efficacy", {}),
                    "safety": self.drug.get("safety", {}),
                })
            self.agent_messages.append({
                "role": "clinical_expert",
                "content": clinical_analysis.get("reasoning", "临床评估完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 3. 药物经济学Agent - 医保评估
        if self.enable_reasoning:
            heor_analysis = await agent_reason("health_economist",
                "评估医保准入概率和药物经济学价值", {
                    "drug": self.drug,
                    "price": self.drug.get("price", 0),
                    "indication": self.drug.get("indication", ""),
                })
            self.agent_messages.append({
                "role": "health_economist",
                "content": heor_analysis.get("reasoning", "药物经济学评估完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 4. 运行基础模拟
        self.initialize_agents()
        
        # 医保评估
        payer_decision = self.payer.evaluate_reimbursement(self.drug)
        insurance_coverage_month = 6
        
        # 医生初始评估
        initial_adopters = set()
        adopted_doctors = set()
        
        for month in range(1, self.config.simulation_months + 1):
            # 逐月模拟
            snapshot = self._simulate_month(
                month=month,
                adopted_doctors=adopted_doctors,
                insurance_active=(month >= insurance_coverage_month and payer_decision["will_cover"]),
                payer_decision=payer_decision,
            )
            self.results.append(snapshot)
            
            # 模拟竞品行为
            competitor_action = self._simulate_competitor_response(month, snapshot.market_penetration)
            if competitor_action:
                self.competitor_actions.append({
                    "month": month,
                    "action": competitor_action,
                    "market_penetration": snapshot.market_penetration,
                })
        
        # 5. 患者行为Agent - 分析患者采纳
        if self.enable_reasoning:
            patient_analysis = await agent_reason("patient_analyst",
                "分析患者群体的用药决策模式和依从性", {
                    "drug": self.drug,
                    "patient_population": len(self.patients),
                    "reimbursement": payer_decision,
                })
            self.agent_messages.append({
                "role": "patient_analyst",
                "content": patient_analysis.get("reasoning", "患者行为分析完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 6. 渠道策略Agent
        if self.enable_reasoning:
            channel_analysis = await agent_reason("channel_strategist",
                "分析药品渠道策略和分销模式", {
                    "drug": self.drug,
                    "adoption_rate": self.results[-1].doctor_adoption_rate if self.results else 0,
                    "regions": self.config.region_focus,
                })
            self.agent_messages.append({
                "role": "channel_strategist",
                "content": channel_analysis.get("reasoning", "渠道策略分析完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 7. 政策分析Agent
        if self.enable_reasoning:
            regulatory_analysis = await agent_reason("regulatory_analyst",
                "分析当前医药政策对该药品市场的影响", {
                    "drug": self.drug,
                    "indication": self.drug.get("indication_category", ""),
                    "is_novel": self.drug.get("is_novel_mechanism", False),
                })
            self.agent_messages.append({
                "role": "regulatory_analyst",
                "content": regulatory_analysis.get("reasoning", "政策分析完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 8. 模拟编排Agent - 生成最终报告
        summary = self._generate_summary()
        if self.enable_reasoning:
            final_report = await agent_reason("orchestrator",
                "综合所有Agent分析，生成最终的药品上市预测报告", {
                    "drug_name": self.drug.get("name", ""),
                    "summary": summary,
                    "payer_decision": payer_decision,
                    "competitor_actions": self.competitor_actions,
                    "total_agent_analyses": len(self.agent_messages),
                })
            self.agent_messages.append({
                "role": "orchestrator",
                "content": final_report.get("reasoning", "报告生成完成"),
                "timestamp": datetime.now().isoformat(),
            })
        
        # 区域分析
        self.regional_results = self._simulate_regional()
        
        return {
            "id": sim_id,
            "drug_name": self.drug.get("name", "未知"),
            "simulation_months": self.config.simulation_months,
            "monthly_snapshots": [self._snapshot_to_dict(s) for s in self.results],
            "summary": summary,
            "payer_decision": payer_decision,
            "agent_messages": self.agent_messages,
            "competitor_actions": self.competitor_actions,
            "regional_results": self.regional_results,
            "doctor_adoption_curve": self._get_adoption_curve(),
            "revenue_projection": self._get_revenue_projection(),
            "config": {
                "num_doctors": self.config.num_doctors,
                "num_patients": self.config.num_patients,
                "random_seed": self.config.random_seed,
            }
        }
    
    def _simulate_regional(self) -> dict:
        """区域差异化模拟"""
        regions = {}
        region_multipliers = {
            "北京": {"adoption": 1.2, "price_sensitivity": 0.8, "insurance": 1.1},
            "上海": {"adoption": 1.15, "price_sensitivity": 0.85, "insurance": 1.05},
            "广州": {"adoption": 1.1, "price_sensitivity": 0.9, "insurance": 1.0},
            "深圳": {"adoption": 1.1, "price_sensitivity": 0.9, "insurance": 1.0},
            "成都": {"adoption": 0.95, "price_sensitivity": 1.1, "insurance": 0.95},
            "武汉": {"adoption": 0.9, "price_sensitivity": 1.15, "insurance": 0.9},
        }
        
        for region, multipliers in region_multipliers.items():
            if self.results:
                final = self.results[-1]
                regions[region] = {
                    "adoption_rate": round(final.doctor_adoption_rate * multipliers["adoption"], 4),
                    "market_penetration": round(final.market_penetration * multipliers["adoption"], 4),
                    "effective_price": round(self.drug.get("price", 0) * multipliers["price_sensitivity"], 2),
                    "revenue_share": round(multipliers["adoption"] * multipliers["insurance"] / 6, 4),
                }
        return regions
    
    def _get_adoption_curve(self) -> list:
        """医生采纳曲线"""
        return [{"month": s.month, "rate": s.doctor_adoption_rate, "cumulative": s.cumulative_prescribers} 
                for s in self.results]
    
    def _get_revenue_projection(self) -> dict:
        """收入预测"""
        if not self.results:
            return {}
        y1 = sum(s.revenue for s in self.results[:12])
        y2 = sum(s.revenue for s in self.results[12:24]) if len(self.results) >= 24 else 0
        y3 = int(y2 * 1.15) if y2 > 0 else 0  # 第三年增长15%
        y4 = int(y2 * 1.25) if y2 > 0 else 0
        y5 = int(y2 * 1.30) if y2 > 0 else 0
        return {
            "year1": y1, "year2": y2, "year3": y3, "year4": y4, "year5": y5,
            "total_5yr": y1 + y2 + y3 + y4 + y5,
        }

# ──────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # 预置药品入库
    conn = get_db()
    for drug in PRESET_DRUGS:
        conn.execute(
            "INSERT OR IGNORE INTO drugs (id, name, generic_name, company, indication, indication_category, mechanism, phase, price, is_listed, is_novel_mechanism, is_domestic, is_expensive, orphan_drug, data_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (drug["id"], drug["name"], drug.get("generic_name",""), drug.get("company",""),
             drug.get("indication",""), drug.get("indication_category",""), drug.get("mechanism",""),
             drug.get("phase",""), drug.get("price",0), int(drug.get("is_listed",True)),
             int(drug.get("is_novel_mechanism",False)), int(drug.get("is_domestic",True)),
             int(drug.get("is_expensive",False)), int(drug.get("orphan_drug",False)),
             json.dumps(drug, ensure_ascii=False))
        )
    conn.commit()
    conn.close()
    yield

app = FastAPI(title="PharmaSim API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# API 路由
# ──────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.now().isoformat()}

@app.get("/api/drugs")
async def list_drugs(category: Optional[str] = None):
    """获取药品列表"""
    conn = get_db()
    if category:
        rows = conn.execute("SELECT * FROM drugs WHERE indication_category = ? ORDER BY name", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM drugs ORDER BY name").fetchall()
    conn.close()
    drugs = []
    for r in rows:
        d = dict(r)
        d["data"] = json.loads(d.pop("data_json", "{}")) if d.get("data_json") else {}
        drugs.append(d)
    return {"drugs": drugs, "total": len(drugs)}

@app.get("/api/drugs/{drug_id}")
async def get_drug(drug_id: str):
    """获取药品详情"""
    conn = get_db()
    row = conn.execute("SELECT * FROM drugs WHERE id = ?", (drug_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "药品未找到")
    d = dict(row)
    d["data"] = json.loads(d.pop("data_json", "{}")) if d.get("data_json") else {}
    return d

@app.post("/api/drugs")
async def create_drug(drug: DrugCreate):
    """创建自定义药品"""
    drug_id = f"custom-{uuid.uuid4().hex[:8]}"
    conn = get_db()
    drug_dict = drug.model_dump()
    drug_dict["target_specialties"] = drug.target_specialties
    drug_dict["competitor_prices"] = drug.competitor_prices
    drug_dict["efficacy"] = drug.efficacy
    drug_dict["safety"] = drug.safety
    conn.execute(
        "INSERT INTO drugs (id, name, generic_name, company, indication, indication_category, mechanism, phase, price, is_listed, is_novel_mechanism, is_domestic, is_expensive, orphan_drug, data_json) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (drug_id, drug.name, drug.generic_name, drug.company, drug.indication,
         drug.indication_category, drug.mechanism, drug.phase, drug.price,
         int(drug.is_listed), int(drug.is_novel_mechanism), int(drug.is_domestic),
         int(drug.is_expensive), int(drug.orphan_drug),
         json.dumps(drug_dict, ensure_ascii=False))
    )
    conn.commit()
    conn.close()
    return {"id": drug_id, "message": "药品创建成功"}

@app.post("/api/simulations")
async def create_simulation(req: SimulationRequest):
    """创建并运行模拟"""
    sim_id = str(uuid.uuid4())[:12]
    
    # 获取药品数据
    if req.drug_id:
        conn = get_db()
        row = conn.execute("SELECT * FROM drugs WHERE id = ?", (req.drug_id,)).fetchone()
        conn.close()
        if not row:
            raise HTTPException(404, "药品未找到")
        drug_data = json.loads(row["data_json"]) if row["data_json"] else dict(row)
    elif req.drug:
        drug_data = req.drug.model_dump()
    else:
        raise HTTPException(400, "需要提供drug_id或drug数据")
    
    # 构建模拟配置
    config = SimulationConfig(
        drug=drug_data,
        num_doctors=req.num_doctors,
        num_patients=req.num_patients,
        simulation_months=req.simulation_months,
        random_seed=42,
        region_focus=req.regions,
    )
    
    # 运行增强模拟
    engine = EnhancedSimulationEngine(config, enable_reasoning=req.agent_reasoning)
    result = await engine.run_with_agents()
    
    # 保存结果
    conn = get_db()
    conn.execute(
        "INSERT INTO simulations (id, drug_id, drug_name, status, config_json, result_json, completed_at) VALUES (?,?,?,?,?,?,?)",
        (sim_id, req.drug_id or "", drug_data.get("name", ""), "completed",
         json.dumps(req.model_dump(), ensure_ascii=False),
         json.dumps(result, ensure_ascii=False),
         datetime.now().isoformat())
    )
    # 保存Agent日志
    for msg in result.get("agent_messages", []):
        conn.execute(
            "INSERT INTO agent_logs (simulation_id, agent_name, agent_role, message, reasoning) VALUES (?,?,?,?,?)",
            (sim_id, msg.get("role", ""), msg.get("role", ""), msg.get("content", ""), msg.get("content", ""))
        )
    conn.commit()
    conn.close()
    
    return result

@app.get("/api/simulations")
async def list_simulations(limit: int = 20):
    """获取模拟历史"""
    conn = get_db()
    rows = conn.execute("SELECT id, drug_name, status, created_at, completed_at FROM simulations ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return {"simulations": [dict(r) for r in rows]}

@app.get("/api/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    """获取模拟详情"""
    conn = get_db()
    row = conn.execute("SELECT * FROM simulations WHERE id = ?", (sim_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "模拟未找到")
    d = dict(row)
    d["config"] = json.loads(d.pop("config_json", "{}")) if d.get("config_json") else {}
    d["result"] = json.loads(d.pop("result_json", "{}")) if d.get("result_json") else {}
    return d

@app.get("/api/simulations/{sim_id}/agents")
async def get_agent_logs(sim_id: str):
    """获取模拟的Agent对话日志"""
    conn = get_db()
    rows = conn.execute("SELECT * FROM agent_logs WHERE simulation_id = ? ORDER BY created_at", (sim_id,)).fetchall()
    conn.close()
    return {"logs": [dict(r) for r in rows]}

@app.get("/api/agents")
async def list_agents():
    """获取Agent列表"""
    return {
        "agents": [
            {"id": "market_analyst", "name": "市场分析专家", "icon": "📊", "description": "分析竞争格局、市场规模和定价策略"},
            {"id": "clinical_expert", "name": "临床医学专家", "icon": "👨‍⚕️", "description": "评估疗效安全性、处方意愿和临床价值"},
            {"id": "health_economist", "name": "药物经济学专家", "icon": "💰", "description": "分析医保准入、ICER和成本效果"},
            {"id": "patient_analyst", "name": "患者行为分析师", "icon": "🏥", "description": "模拟患者就医、用药和依从行为"},
            {"id": "channel_strategist", "name": "渠道策略师", "icon": "🏭", "description": "分析医院、药房和电商渠道策略"},
            {"id": "regulatory_analyst", "name": "政策法规分析师", "icon": "📋", "description": "分析DRG/DIP、集采和监管影响"},
            {"id": "calibrator", "name": "数据校准专家", "icon": "🔧", "description": "基于真实世界数据校准模拟参数"},
            {"id": "orchestrator", "name": "模拟编排师", "icon": "🎯", "description": "协调Agent协作并生成最终报告"},
        ]
    }

# 挂载前端静态文件
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIR, "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
