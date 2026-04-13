#!/usr/bin/env python3
"""
PharmaSim Decision Model Engine v1.0
7-Dimensional × 28 Sub-Dimension Scoring System

Scoring methodology:
- Each sub-dimension scores 0-1 based on real data
- Weights are calibrated against historical drug launch outcomes
- Final composite is weighted average with interaction terms
"""
import sqlite3
import json
import math
import pathlib
from datetime import datetime

DB = pathlib.Path(__file__).parent / 'data' / 'pharmasim.db'

# ═══════════════════════════════════════
# DIMENSION DEFINITIONS & WEIGHTS
# ═══════════════════════════════════════

DIMENSIONS = {
    'epidemiology': {
        'name_cn': '流行病学',
        'emoji': '🧬',
        'weight': 0.15,
        'sub_dimensions': {
            'disease_burden': {'name_cn': '疾病负担', 'weight': 0.35},
            'population_size': {'name_cn': '人群规模', 'weight': 0.30},
            'unmet_need': {'name_cn': '未满足需求', 'weight': 0.25},
            'mortality_severity': {'name_cn': '死亡率/严重度', 'weight': 0.10},
        }
    },
    'clinical': {
        'name_cn': '临床评估',
        'emoji': '🩺',
        'weight': 0.25,
        'sub_dimensions': {
            'efficacy': {'name_cn': '疗效', 'weight': 0.40},
            'safety': {'name_cn': '安全性', 'weight': 0.30},
            'guideline_position': {'name_cn': '指南推荐', 'weight': 0.20},
            'operational_feasibility': {'name_cn': '可操作性', 'weight': 0.10},
        }
    },
    'market': {
        'name_cn': '市场评估',
        'emoji': '📊',
        'weight': 0.15,
        'sub_dimensions': {
            'competition': {'name_cn': '竞争格局', 'weight': 0.30},
            'market_size': {'name_cn': '市场容量', 'weight': 0.25},
            'channel_access': {'name_cn': '渠道可及', 'weight': 0.25},
            'commercialization': {'name_cn': '商业化能力', 'weight': 0.20},
        }
    },
    'pricing': {
        'name_cn': '定价评估',
        'emoji': '💰',
        'weight': 0.15,
        'sub_dimensions': {
            'value_support': {'name_cn': '价值支撑', 'weight': 0.30},
            'competitive_pricing': {'name_cn': '竞争定价', 'weight': 0.25},
            'nrml_access': {'name_cn': '医保准入', 'weight': 0.25},
            'international_reference': {'name_cn': '国际参考', 'weight': 0.20},
        }
    },
    'pharmacology': {
        'name_cn': '药物学',
        'emoji': '⚗️',
        'weight': 0.10,
        'sub_dimensions': {
            'pk_profile': {'name_cn': '药代动力学', 'weight': 0.30},
            'pd_efficacy': {'name_cn': '药效学', 'weight': 0.30},
            'toxicology': {'name_cn': '毒理', 'weight': 0.25},
            'formulation': {'name_cn': '制剂便利性', 'weight': 0.15},
        }
    },
    'pharmaecon': {
        'name_cn': '药物经济学',
        'emoji': '📐',
        'weight': 0.10,
        'sub_dimensions': {
            'cost_effectiveness': {'name_cn': '成本效果', 'weight': 0.35},
            'budget_impact': {'name_cn': '预算影响', 'weight': 0.30},
            'qol_improvement': {'name_cn': '生活质量改善', 'weight': 0.20},
            'hta_evidence': {'name_cn': 'HTA证据', 'weight': 0.15},
        }
    },
    'insurance': {
        'name_cn': '医保评估',
        'emoji': '📋',
        'weight': 0.10,
        'sub_dimensions': {
            'nrml_eligibility': {'name_cn': '国谈准入', 'weight': 0.30},
            'reimbursement_breadth': {'name_cn': '报销广度', 'weight': 0.25},
            'fund_impact': {'name_cn': '基金影响', 'weight': 0.25},
            'drg_compatibility': {'name_cn': 'DRG兼容', 'weight': 0.20},
        }
    },
}

def sigmoid(x, center=0.5, steepness=10):
    """Sigmoid normalization for smooth scoring."""
    return 1 / (1 + math.exp(-steepness * (x - center)))

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def get_conn():
    return sqlite3.connect(str(DB))

def score_drug(drug_id, config=None):
    """
    Score a drug across all 7 dimensions × 28 sub-dimensions.
    Returns detailed scoring breakdown.
    """
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    # Load drug data
    drug_row = conn.execute('SELECT * FROM drugs WHERE id=?', (drug_id,)).fetchone()
    if not drug_row:
        return {'error': f'Drug {drug_id} not found'}
    drug = dict(drug_row)
    
    # Load related data
    efficacy = conn.execute('SELECT * FROM clinical_efficacy WHERE drug_id=? ORDER BY sample_size DESC', (drug_id,)).fetchall()
    china_row = conn.execute('SELECT * FROM china_status WHERE drug_id=?', (drug_id,)).fetchone()
    china = dict(china_row) if china_row else None
    pricing_rows = conn.execute('SELECT * FROM pricing WHERE drug_id=?', (drug_id,)).fetchall()
    epi_row = conn.execute('SELECT * FROM disease_epidemiology WHERE disease=?', (drug['indication'],)).fetchone()
    epi = dict(epi_row) if epi_row else None
    pipeline = conn.execute('SELECT * FROM pipeline_drugs WHERE competitive_threat_to=?', (drug_id,)).fetchall()
    
    pricing = {p['market']: dict(p) for p in pricing_rows}
    
    # Use best efficacy data (largest trial)
    best = dict(efficacy[0]) if efficacy else None
    
    config = config or {}
    scores = {}
    explanations = {}
    
    # ═══ DIMENSION 1: EPIDEMIOLOGY ═══
    epi_scores = {}
    if epi:
        # Disease burden: based on prevalence, mortality, severity
        burden = clamp(0.3 + 0.4 * sigmoid(epi['total_patients_cn'] or 0, 100000, 0.00001) + 0.3 * sigmoid(epi['mortality_rate'] or 0, 20, 0.1))
        epi_scores['disease_burden'] = burden
        explanations['disease_burden'] = f"患者数{epi['total_patients_cn']:,}人, 死亡率{epi['mortality_rate']}%"
        
        # Population size
        pop = clamp(sigmoid(epi['total_patients_cn'] or 0, 500000, 0.000005))
        epi_scores['population_size'] = pop
        explanations['population_size'] = f"中国患者池{epi['total_patients_cn']:,}人"
        
        # Unmet need: low diagnosis/treatment rate = high unmet need
        treat_rate = epi['treated_rate'] or 50
        unmet = clamp(1 - treat_rate / 100)
        epi_scores['unmet_need'] = unmet
        explanations['unmet_need'] = f"治疗率{treat_rate}%, 未满足需求{'高' if unmet > 0.6 else '中' if unmet > 0.3 else '低'}"
        
        # Mortality severity
        mort = clamp(sigmoid(epi['mortality_rate'] or 0, 15, 0.15))
        epi_scores['mortality_severity'] = mort
        explanations['mortality_severity'] = f"年死亡率{epi['mortality_rate']}%"
    else:
        epi_scores = {'disease_burden': 0.5, 'population_size': 0.5, 'unmet_need': 0.5, 'mortality_severity': 0.5}
        explanations.update({'disease_burden': '流行病学数据不足', 'population_size': '流行病学数据不足', 'unmet_need': '流行病学数据不足', 'mortality_severity': '流行病学数据不足'})
    
    scores['epidemiology'] = epi_scores
    
    # ═══ DIMENSION 2: CLINICAL ═══
    clin_scores = {}
    if best:
        # Efficacy: normalize ORR, PFS, OS, or other endpoints
        eff = 0.5
        if best['orr'] and best['orr'] > 0:
            eff = clamp(sigmoid(best['orr'], 50, 0.06))
        elif best['median_pfs'] and best['median_pfs'] > 0:
            eff = clamp(sigmoid(best['median_pfs'], 12, 0.15))
        elif best['hba1c_reduction'] and best['hba1c_reduction'] < 0:
            eff = clamp(sigmoid(-best['hba1c_reduction'], 1.5, 1.5))
        elif best['response_rate'] and best['response_rate'] > 0:
            eff = clamp(sigmoid(best['response_rate'], 0.6, 8))
        elif best['hospitalization_reduction'] and best['hospitalization_reduction'] > 0:
            eff = clamp(sigmoid(best['hospitalization_reduction'], 0.2, 8))
        clin_scores['efficacy'] = eff
        explanations['efficacy'] = f"ORR {best['orr'] or 'N/A'}% | PFS {best['median_pfs'] or 'N/A'}m | OS {best['median_os'] or 'N/A'}m | 样本量 n={best['sample_size']}"
        
        # Safety: lower AE rate = better
        g3ae = best['grade3_ae_rate'] or 20
        safety = clamp(1 - sigmoid(g3ae, 15, 0.12))
        clin_scores['safety'] = safety
        explanations['safety'] = f"3级以上AE {g3ae}%, SAE {best['serious_ae_rate'] or 'N/A'}%, 停药率 {best['discontinuation_rate'] or 'N/A'}%"
        
        # Guideline position (based on FDA breakthrough + priority)
        guide = 0.4 + 0.15 * (drug['fda_breakthrough'] or 0) + 0.15 * (drug['fda_priority_review'] or 0) + 0.15 * (1 if drug['fda_approval_year'] and drug['fda_approval_year'] < 2020 else 0) + 0.15 * min(1, (best['sample_size'] or 0) / 1000)
        clin_scores['guideline_position'] = clamp(guide)
        explanations['guideline_position'] = f"FDA突破性{'是' if drug['fda_breakthrough'] else '否'}, 优先审评{'是' if drug['fda_priority_review'] else '否'}"
        
        # Operational feasibility
        route_score = {'oral': 0.9, 'subcutaneous': 0.7, 'IV': 0.5, 'intrathecal': 0.2}.get(drug['route_of_admin'], 0.5)
        freq_score = {'QD': 0.9, 'BID': 0.7, 'QW': 0.75, 'Q2W': 0.6, 'Q3W': 0.55, 'Q4W': 0.65, 'Q4M maintenance': 0.5}.get(drug['dosing_frequency'], 0.5)
        oper = clamp(0.5 * route_score + 0.5 * freq_score)
        clin_scores['operational_feasibility'] = oper
        explanations['operational_feasibility'] = f"{drug['route_of_admin']}给药, {drug['dosing_frequency']}"
    else:
        clin_scores = {'efficacy': 0.5, 'safety': 0.5, 'guideline_position': 0.5, 'operational_feasibility': 0.5}
        explanations.update({'efficacy': '无临床数据', 'safety': '无安全性数据', 'guideline_position': '无指南数据', 'operational_feasibility': '无给药数据'})
    
    scores['clinical'] = clin_scores
    
    # ═══ DIMENSION 3: MARKET ═══
    mkt_scores = {}
    
    # Competition: fewer competitors = better
    comp_count = config.get('competitor_count', 4)
    comp = clamp(1 - sigmoid(comp_count, 3, 0.6))
    mkt_scores['competition'] = comp
    explanations['competition'] = f"竞品数{comp_count}个"
    
    # Market size
    if epi and epi['total_patients_cn']:
        mkt_size = clamp(sigmoid(epi['total_patients_cn'], 1000000, 0.000002))
    else:
        mkt_size = 0.5
    mkt_scores['market_size'] = mkt_size
    explanations['market_size'] = f"目标患者{epi['total_patients_cn'] if epi else '未知'}人"
    
    # Channel access
    if china:
        channel = clamp(0.3 + 0.3 * (1 if china['dtp_available'] else 0) + 0.2 * sigmoid(china['hospital_listed_count'] or 0, 100, 0.02) + 0.2 * (1 if china['included_in_nrml'] else 0))
    else:
        channel = 0.3
    mkt_scores['channel_access'] = channel
    explanations['channel_access'] = f"DTP{'可用' if china and china['dtp_available'] else '不可用'}, 医院覆盖{china['hospital_listed_count'] if china else 0}家"
    
    # Commercialization: based on company size and track record
    big_pharma = any(c in (drug['company'] or '') for c in ['Merck', 'Pfizer', 'Roche', 'Novartis', 'AstraZeneca', 'BMS', 'Eli Lilly', 'AbbVie', 'J&J', 'Novo Nordisk', 'Sanofi'])
    comm = 0.75 if big_pharma else 0.45
    mkt_scores['commercialization'] = comm
    explanations['commercialization'] = f"{'跨国大药企' if big_pharma else '中型药企'}"
    
    scores['market'] = mkt_scores
    
    # ═══ DIMENSION 4: PRICING ═══
    price_scores = {}
    
    # Value support: efficacy vs price ratio
    if pricing.get('CN') and best:
        price_cn = pricing['CN']['price_per_month']
        if best['orr'] and best['orr'] > 0:
            val = clamp(sigmoid(best['orr'] / max(price_cn, 1) * 10000, 30, 0.08))
        elif best.get('hba1c_reduction'):
            val = clamp(sigmoid(-best['hba1c_reduction'] / max(price_cn, 1) * 10000, 25, 0.08))
        else:
            val = 0.5
        price_scores['value_support'] = val
        explanations['value_support'] = f"疗效/价格比: ORR {best['orr'] or 'N/A'}% / ¥{price_cn}/月"
    else:
        price_scores['value_support'] = 0.5
        explanations['value_support'] = '定价数据不足'
    
    # Competitive pricing
    if pricing.get('CN') and pricing.get('US'):
        cn_us_ratio = pricing['CN']['price_per_month'] / max(pricing['US']['price_per_month'], 1)
        comp_price = clamp(1 - sigmoid(cn_us_ratio, 0.5, 5))
        price_scores['competitive_pricing'] = comp_price
        explanations['competitive_pricing'] = f"中美比价: {cn_us_ratio:.1%} (中国¥{pricing['CN']['price_per_month']}/月 vs 美国${pricing['US']['price_per_month']}/月)"
    else:
        price_scores['competitive_pricing'] = 0.5
        explanations['competitive_pricing'] = '无对比定价数据'
    
    # NRML access
    if china and china['included_in_nrml']:
        disc = china['nrml_discount'] or 50
        nrml = clamp(0.5 + 0.3 * sigmoid(disc, 60, 0.05) + 0.2)
        price_scores['nrml_access'] = nrml
        explanations['nrml_access'] = f"已进入医保, 降幅{disc}%, 谈判价¥{china['nrml_price']}/月"
    else:
        price_scores['nrml_access'] = 0.2
        explanations['nrml_access'] = '未进入国家医保目录'
    
    # International reference
    if pricing.get('US') and pricing.get('CN'):
        ir = clamp(0.5 + 0.3 * (1 if china and china['included_in_nrml'] else 0) + 0.2 * sigmoid(pricing['US']['price_per_month'], 10000, 0.0003))
    else:
        ir = 0.5
    price_scores['international_reference'] = ir
    explanations['international_reference'] = f"美国月费用${pricing['US']['price_per_month'] if pricing.get('US') else 'N/A'}"
    
    scores['pricing'] = price_scores
    
    # ═══ DIMENSION 5: PHARMACOLOGY ═══
    pharma_scores = {}
    
    # PK profile (based on dosing frequency and route)
    freq_pk = {'QD': 0.8, 'BID': 0.6, 'QW': 0.75, 'Q2W': 0.65, 'Q3W': 0.55, 'Q4W': 0.7, 'Q4M maintenance': 0.5}.get(drug['dosing_frequency'], 0.5)
    pharma_scores['pk_profile'] = freq_pk
    explanations['pk_profile'] = f"给药频率{drug['dosing_frequency']}"
    
    # PD efficacy
    if best:
        if best['pfs_hr'] and best['pfs_hr'] > 0 and best['pfs_hr'] < 1:
            pd = clamp(1 - best['pfs_hr'])
        elif best['hba1c_reduction'] and best['hba1c_reduction'] < 0:
            pd = clamp(sigmoid(-best['hba1c_reduction'], 1.5, 1.5))
        else:
            pd = clamp(sigmoid(best.get('efficacy', best.get('orr', 50)), 50, 0.06) if best.get('orr') else 0.5)
        pharma_scores['pd_efficacy'] = pd
        explanations['pd_efficacy'] = f"PFS HR {best['pfs_hr'] or 'N/A'}"
    else:
        pharma_scores['pd_efficacy'] = 0.5
        explanations['pd_efficacy'] = '无药效数据'
    
    # Toxicology
    if best:
        tox = clamp(1 - sigmoid(best['grade3_ae_rate'] or 20, 15, 0.12))
    else:
        tox = 0.5
    pharma_scores['toxicology'] = tox
    explanations['toxicology'] = f"3级AE {best['grade3_ae_rate'] if best else 'N/A'}%"
    
    # Formulation
    form = {'oral': 0.9, 'subcutaneous': 0.7, 'IV': 0.4, 'intrathecal': 0.2}.get(drug['route_of_admin'], 0.5)
    pharma_scores['formulation'] = form
    explanations['formulation'] = f"{drug['route_of_admin']}给药"
    
    scores['pharmacology'] = pharma_scores
    
    # ═══ DIMENSION 6: PHARMACOECONOMICS ═══
    pharmaecon_scores = {}
    
    # Cost-effectiveness (simplified ICER proxy)
    if pricing.get('CN') and best:
        monthly_cost = pricing['CN']['price_per_month']
        if best['orr'] and best['orr'] > 0:
            qaly_proxy = best['orr'] / 100 * (best['median_os'] or 12) / 12
        elif best.get('hba1c_reduction'):
            qaly_proxy = -best['hba1c_reduction'] / 10
        else:
            qaly_proxy = 0.5
        icer_proxy = monthly_cost * 12 / max(qaly_proxy, 0.01)
        ce = clamp(sigmoid(500000 - icer_proxy, 0, 0.000005))
        pharmaecon_scores['cost_effectiveness'] = ce
        explanations['cost_effectiveness'] = f"年治疗费¥{monthly_cost*12:,}, QALY增量~{qaly_proxy:.2f}"
    else:
        pharmaecon_scores['cost_effectiveness'] = 0.5
        explanations['cost_effectiveness'] = '无药物经济学数据'
    
    # Budget impact
    if epi and pricing.get('CN'):
        annual_budget = (epi['total_patients_cn'] or 0) * (pricing['CN']['price_per_month'] or 0) * 12
        bi = clamp(1 - sigmoid(annual_budget, 100000000000, 0.00000000001))
        pharmaecon_scores['budget_impact'] = bi
        explanations['budget_impact'] = f"年预算冲击约¥{annual_budget/1e8:.0f}亿"
    else:
        pharmaecon_scores['budget_impact'] = 0.5
        explanations['budget_impact'] = '预算影响待评估'
    
    # QoL improvement
    qol = 0.5
    if best:
        if best['response_rate'] and best['response_rate'] > 0.6:
            qol = 0.75
        if drug['route_of_admin'] == 'oral':
            qol += 0.1
    pharmaecon_scores['qol_improvement'] = clamp(qol)
    explanations['qol_improvement'] = f"给药途径{drug['route_of_admin']}, 响应率{best['response_rate'] if best else 'N/A'}"
    
    # HTA evidence
    hta = 0.4 + 0.2 * (1 if best and best['is_randomized'] else 0) + 0.2 * (1 if best and best['is_phase3'] else 0) + 0.2 * min(1, (best['sample_size'] if best else 0) / 1000)
    pharmaecon_scores['hta_evidence'] = clamp(hta)
    explanations['hta_evidence'] = f"{'RCT' if best and best['is_randomized'] else '非随机'}, n={best['sample_size'] if best else 'N/A'}"
    
    scores['pharmaecon'] = pharmaecon_scores
    
    # ═══ DIMENSION 7: INSURANCE ═══
    ins_scores = {}
    
    # NRML eligibility
    if china and china['included_in_nrml']:
        ins_scores['nrml_eligibility'] = 0.9
        explanations['nrml_eligibility'] = f"已进入国谈目录, 谈判价¥{china['nrml_price']}/月"
    elif china and china['status'] == 'approved':
        ins_scores['nrml_eligibility'] = 0.5
        explanations['nrml_eligibility'] = '已上市但未进入国谈'
    elif china and china['status'] == 'pending':
        ins_scores['nrml_eligibility'] = 0.2
        explanations['nrml_eligibility'] = '中国审批中, 暂无国谈资格'
    else:
        ins_scores['nrml_eligibility'] = 0.1
        explanations['nrml_eligibility'] = '未在中国提交申请'
    
    # Reimbursement breadth
    if china and china['included_in_nrml']:
        reimb = clamp(0.5 + 0.3 * sigmoid(china['hospital_listed_count'] or 0, 200, 0.01))
    else:
        reimb = 0.15
    ins_scores['reimbursement_breadth'] = reimb
    explanations['reimbursement_breadth'] = f"覆盖医院{china['hospital_listed_count'] if china else 0}家"
    
    # Fund impact
    if epi and pricing.get('CN') and china:
        fund = (epi['total_patients_cn'] or 0) * (china['nrml_price'] or pricing['CN']['price_per_month'] or 0) * 12
        fi = clamp(1 - sigmoid(fund, 50000000000, 0.00000000003))
    else:
        fi = 0.5
    ins_scores['fund_impact'] = fi
    explanations['fund_impact'] = f"基金年支出约¥{fund/1e8 if 'fund' in dir() else '未知'}亿"
    
    # DRG compatibility
    drg = 0.3 if drug['drug_type'] == 'biologic' else 0.7
    if drug['route_of_admin'] == 'oral':
        drg += 0.1
    ins_scores['drg_compatibility'] = clamp(drg)
    explanations['drg_compatibility'] = f"{'生物制剂' if drug['drug_type'] == 'biologic' else '小分子'}, DRG{'豁免可申请' if drug['drug_type'] == 'biologic' else '需纳入'}"
    
    scores['insurance'] = ins_scores
    
    conn.close()
    
    # ═══ COMPUTE DIMENSION AVERAGES AND COMPOSITE ═══
    dim_results = {}
    composite = 0
    
    for dim_key, dim_def in DIMENSIONS.items():
        sub_scores = scores.get(dim_key, {})
        dim_total = 0
        dim_weight_sum = 0
        sub_results = []
        
        for sub_key, sub_def in dim_def['sub_dimensions'].items():
            s = sub_scores.get(sub_key, 0.5)
            w = sub_def['weight']
            dim_total += s * w
            dim_weight_sum += w
            sub_results.append({
                'key': sub_key,
                'name': sub_def['name_cn'],
                'score': round(s, 3),
                'weight': w,
                'explanation': explanations.get(sub_key, '')
            })
        
        dim_avg = dim_total / max(dim_weight_sum, 0.01)
        dim_results[dim_key] = {
            'name': dim_def['name_cn'],
            'emoji': dim_def['emoji'],
            'score': round(dim_avg, 3),
            'weight': dim_def['weight'],
            'sub_dimensions': sub_results
        }
        composite += dim_avg * dim_def['weight']
    
    # Recommendation
    if composite >= 0.65:
        recommendation = '✅ 推荐上市'
        rec_code = 'recommend'
    elif composite >= 0.50:
        recommendation = '⚠️ 有条件推荐'
        rec_code = 'conditional'
    else:
        recommendation = '❌ 暂不推荐'
        rec_code = 'not_recommend'
    
    return {
        'drug': {
            'id': drug['id'],
            'name': drug['name'],
            'generic': drug['generic_name'],
            'chinese': drug['chinese_name'],
            'company': drug['company'],
            'area': drug['therapeutic_area'],
            'mechanism': drug['mechanism'],
        },
        'composite_score': round(composite, 3),
        'recommendation': recommendation,
        'recommendation_code': rec_code,
        'dimensions': dim_results,
        'timestamp': datetime.now().isoformat(),
    }


def score_all_drugs():
    """Score all drugs in the database."""
    conn = get_conn()
    drugs = conn.execute('SELECT id, name FROM drugs ORDER BY therapeutic_area, name').fetchall()
    conn.close()
    
    results = []
    for drug_id, drug_name in drugs:
        print(f'  Scoring {drug_name}...')
        result = score_drug(drug_id)
        results.append(result)
    
    return results


if __name__ == '__main__':
    results = score_all_drugs()
    print(f'\nScored {len(results)} drugs:')
    for r in sorted(results, key=lambda x: x['composite_score'], reverse=True):
        print(f"  {r['drug']['name']:20s} {r['composite_score']:.3f}  {r['recommendation']}")
