#!/usr/bin/env python3
"""
PharmaSim Database Schema v1.0
Real pharmaceutical data with multi-dimensional scoring
"""
import sqlite3
import pathlib

DB_PATH = pathlib.Path(__file__).parent / 'data' / 'pharmasim.db'

SCHEMA = """
-- ═══════════════════════════════════════
-- CORE DRUG DATA
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,                    -- Brand name (Keytruda)
    generic_name TEXT NOT NULL,            -- Generic (pembrolizumab)
    chinese_name TEXT,                     -- Chinese name (帕博利珠单抗)
    company TEXT NOT NULL,                 -- Manufacturer
    company_cn TEXT,                       -- Chinese company name
    therapeutic_area TEXT NOT NULL,         -- Category (肿瘤/免疫)
    indication TEXT NOT NULL,              -- Primary indication
    indications_json TEXT,                 -- All indications as JSON array
    mechanism TEXT NOT NULL,               -- MOA (PD-1 inhibitor)
    mechanism_detail TEXT,                 -- Detailed MOA description
    drug_type TEXT DEFAULT 'small_molecule', -- small_molecule, biologic, gene_therapy
    route_of_admin TEXT DEFAULT 'IV',      -- IV, oral, subcutaneous
    dosing_frequency TEXT DEFAULT 'Q3W',   -- QD, BID, QW, Q2W, Q3W, Q4W
    
    -- FDA data
    fda_approval_date TEXT,               -- YYYY-MM-DD
    fda_approval_year INTEGER,
    fda_indication TEXT,
    fda_breakthrough TINYINT DEFAULT 0,   -- Breakthrough therapy designation
    fda_priority_review TINYINT DEFAULT 0,
    fda_accelerated TINYINT DEFAULT 0,
    nda_number TEXT,                       -- NDA/BLA number
    
    -- Real-world data
    annual_us_revenue REAL,               -- Peak US revenue (USD)
    global_revenue REAL,                  -- Peak global revenue (USD)
    patient_population_us INTEGER,        -- Estimated US patients
    patient_population_cn INTEGER,        -- Estimated China patients
    
    -- Metadata
    data_source TEXT DEFAULT 'FDA',
    last_updated TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS clinical_efficacy (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL REFERENCES drugs(id),
    trial_name TEXT,                       -- Trial name (KEYNOTE-189)
    indication TEXT NOT NULL,
    line_of_therapy TEXT,                  -- 1L, 2L, 3L+
    
    -- Oncology endpoints
    orr REAL,                              -- Objective Response Rate (%)
    dcr REAL,                              -- Disease Control Rate (%)
    median_pfs REAL,                       -- Median PFS (months)
    pfs_hr REAL,                           -- PFS Hazard Ratio
    median_os REAL,                        -- Median OS (months)
    os_hr REAL,                            -- OS Hazard Ratio
    median_dor REAL,                       -- Duration of Response (months)
    
    -- Non-oncology endpoints
    hba1c_reduction REAL,                  -- Diabetes (absolute reduction)
    weight_change REAL,                    -- Weight change (kg)
    response_rate REAL,                    -- General response rate
    remission_rate REAL,                   -- Remission rate
    ldl_reduction REAL,                    -- LDL reduction (%)
    
    -- Safety
    grade3_ae_rate REAL,                   -- Grade 3+ AE rate (%)
    serious_ae_rate REAL,                  -- Serious AE rate (%)
    discontinuation_rate REAL,             -- Discontinuation due to AEs (%)
    treatment_related_death REAL,          -- Treatment-related death rate (%)
    
    -- Trial quality
    sample_size INTEGER,
    is_randomized TINYINT DEFAULT 1,
    is_controlled TINYINT DEFAULT 1,
    is_phase3 TINYINT DEFAULT 1,
    publication_url TEXT,
    
    data_source TEXT DEFAULT 'ClinicalTrials.gov',
    last_updated TEXT DEFAULT (datetime('now'))
);

-- ═══════════════════════════════════════
-- CHINA MARKET DATA
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS china_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL REFERENCES drugs(id),
    status TEXT NOT NULL,                  -- approved, pending, not_submitted, rejected
    approval_date TEXT,                    -- NMPA approval date
    nrda_number TEXT,                       -- NMPA approval number
    import_license TEXT,
    included_in_nrml TINYINT DEFAULT 0,   -- National Reimbursement Medicine List
    nrml_included_date TEXT,
    nrml_price REAL,                       -- NRML negotiated price (RMB/month)
    nrml_discount REAL,                    -- Discount from original price (%)
    vbp_tender TINYINT DEFAULT 0,         -- Volume-based procurement
    dtp_available TINYINT DEFAULT 0,       -- DTP pharmacy available
    hospital_listed_count INTEGER DEFAULT 0, -- Number of hospitals listing
    
    last_updated TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pricing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL REFERENCES drugs(id),
    market TEXT NOT NULL,                  -- 'US', 'CN', 'EU', 'JP'
    price_per_unit REAL,                   -- Price per unit (USD or RMB)
    price_per_month REAL,                  -- Monthly treatment cost
    price_per_year REAL,                   -- Annual treatment cost
    currency TEXT DEFAULT 'USD',
    wac_price REAL,                        -- Wholesale acquisition cost
    net_price REAL,                        -- After rebates
    patient_copay REAL,                    -- Typical patient copay
    pap_available TINYINT DEFAULT 0,       -- Patient assistance program
    pap_details TEXT,
    data_date TEXT,
    
    last_updated TEXT DEFAULT (datetime('now'))
);

-- ═══════════════════════════════════════
-- COMPETITIVE LANDSCAPE
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS competitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL REFERENCES drugs(id),
    competitor_id INTEGER NOT NULL REFERENCES drugs(id),
    competition_type TEXT,                 -- direct, indirect, biosimilar
    market_share_cn REAL,                  -- China market share (%)
    market_share_us REAL,                  -- US market share (%)
    price_advantage REAL,                  -- Price difference (%)
    efficacy_comparison TEXT,              -- better, similar, worse
    first_mover TINYINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pipeline_drugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    generic_name TEXT,
    company TEXT NOT NULL,
    therapeutic_area TEXT,
    indication TEXT,
    mechanism TEXT,
    phase TEXT NOT NULL,                   -- Phase 1, 2, 3, NDA
    trial_id TEXT,                         -- NCT number
    primary_endpoint TEXT,
    expected_approval TEXT,                -- Expected year
    data_readout TEXT,                     -- Expected data readout
    peak_sales_estimate REAL,             -- Analyst consensus (USD)
    competitive_threat_to INTEGER REFERENCES drugs(id),
    
    last_updated TEXT DEFAULT (datetime('now'))
);

-- ═══════════════════════════════════════
-- EPIDEMIOLOGY & MARKET
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS disease_epidemiology (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease TEXT NOT NULL,
    disease_cn TEXT,
    icd10_code TEXT,
    prevalence_cn REAL,                    -- China prevalence per 100k
    incidence_cn REAL,                     -- China incidence per 100k
    total_patients_cn INTEGER,             -- Total China patients
    diagnosed_rate REAL,                   -- Diagnosis rate (%)
    treated_rate REAL,                     -- Treatment rate (%)
    annual_new_cases INTEGER,
    mortality_rate REAL,
    data_source TEXT,
    
    last_updated TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS market_size (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    therapeutic_area TEXT NOT NULL,
    indication TEXT NOT NULL,
    year INTEGER NOT NULL,
    market_size_usd REAL,                  -- Global market size
    market_size_rmb REAL,                  -- China market size
    growth_rate REAL,                      -- YoY growth (%)
    volume_doses INTEGER,                  -- Total doses/units
    data_source TEXT,
    
    UNIQUE(therapeutic_area, indication, year)
);

-- ═══════════════════════════════════════
-- AGENT SIMULATION
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_type TEXT NOT NULL,              -- doctor, patient, expert
    name TEXT NOT NULL,
    
    -- Doctor fields
    hospital TEXT,
    hospital_tier TEXT,                    -- 三甲, 二甲, etc.
    specialty TEXT,
    years_experience INTEGER,
    patient_volume INTEGER,
    innovation_type TEXT,                  -- innovator, early_adopter, majority, laggard
    publications INTEGER,
    clinical_trials INTEGER,
    
    -- Patient fields
    age INTEGER,
    gender TEXT,
    city TEXT,
    city_tier INTEGER,                     -- 1, 2, 3, 4
    insurance_type TEXT,                   -- 城镇职工, 城镇居民, 新农合, 自费
    income_level TEXT,                     -- high, middle, low
    monthly_income INTEGER,
    primary_disease TEXT,
    comorbidities TEXT,
    
    -- Expert fields
    expert_dimension TEXT,                 -- epidemiology, clinical, market, pricing, pharmacology, pharmaecon, insurance
    university TEXT,
    h_index INTEGER,
    total_publications INTEGER,
    industry_influence TEXT,               -- high, medium, low
    grant_count INTEGER,
    
    -- Shared
    base_willingness REAL,                 -- 0-1 adoption willingness
    attitude TEXT,
    stance TEXT,
    
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS agent_connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_a INTEGER NOT NULL REFERENCES agents(id),
    agent_b INTEGER NOT NULL REFERENCES agents(id),
    connection_type TEXT,                  -- peer, kol, referral, influence
    strength REAL DEFAULT 0.5,             -- 0-1 connection strength
    
    UNIQUE(agent_a, agent_b)
);

-- ═══════════════════════════════════════
-- SIMULATION RESULTS
-- ═══════════════════════════════════════

CREATE TABLE IF NOT EXISTS simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    drug_id INTEGER NOT NULL REFERENCES drugs(id),
    simulation_date TEXT DEFAULT (datetime('now')),
    
    -- Config
    china_price_monthly REAL,
    pricing_strategy TEXT,
    patient_assistance TEXT,
    insurance_target TEXT,
    expected_discount REAL,
    drg_exemption TINYINT,
    competitor_count INTEGER,
    target_specialties TEXT,
    launch_quarter TEXT,
    promotion_level TEXT,
    kol_strategy TEXT,
    channel_coverage TEXT,
    
    -- Results
    composite_score REAL,
    recommendation TEXT,                   -- recommend, conditional, not_recommend
    peak_prescriptions INTEGER,
    peak_penetration REAL,
    revenue_24m REAL,
    patient_willingness REAL,
    
    -- Dimension scores (JSON)
    dimension_scores TEXT,                 -- JSON blob
    cluster_distribution TEXT,             -- JSON blob
    monthly_forecast TEXT,                 -- JSON blob
    expert_comments TEXT                   -- JSON blob
);

CREATE TABLE IF NOT EXISTS dimension_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id INTEGER NOT NULL REFERENCES simulations(id),
    dimension TEXT NOT NULL,               -- epidemiology, clinical, market, pricing, pharmacology, pharmaecon, insurance
    sub_dimension TEXT NOT NULL,
    score REAL NOT NULL,
    weight REAL DEFAULT 1.0,
    explanation TEXT,
    evidence TEXT                          -- JSON array of supporting evidence
);

-- ═══════════════════════════════════════
-- INDEXES
-- ═══════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_drugs_area ON drugs(therapeutic_area);
CREATE INDEX IF NOT EXISTS idx_drugs_fda ON drugs(fda_approval_year);
CREATE INDEX IF NOT EXISTS idx_efficacy_drug ON clinical_efficacy(drug_id);
CREATE INDEX IF NOT EXISTS idx_china_drug ON china_status(drug_id);
CREATE INDEX IF NOT EXISTS idx_pricing_drug ON pricing(drug_id);
CREATE INDEX IF NOT EXISTS idx_competitors_drug ON competitors(drug_id);
CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_simulations_drug ON simulations(drug_id);
CREATE INDEX IF NOT EXISTS idx_scores_sim ON dimension_scores(simulation_id);
"""

def create_database():
    """Create the database and all tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript(SCHEMA)
    conn.commit()
    
    # Verify
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Database created at: {DB_PATH}")
    print(f"Tables ({len(tables)}): {', '.join(tables)}")
    
    conn.close()
    return str(DB_PATH)

if __name__ == '__main__':
    create_database()
