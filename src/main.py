"""
PharmaSim - 主入口 (v2.0)
运行1000 Agent多维度药品上市模拟
"""

import json
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation.simulation_engine import SimulationEngine, SimulationConfig


# 示例药品: PD-1 单抗
SAMPLE_DRUG = {
    "name": "PharmaSim-Test-001",
    "generic_name": "示例PD-1单抗",
    "indication": "非小细胞肺癌",
    "indication_category": "肿瘤",
    "mechanism": "PD-1抑制剂",
    "target_specialties": ["肿瘤科", "呼吸科", "胸外科"],
    "price": 15000,  # 元/月
    "competitor_prices": [12000, 18000, 9800, 22000],
    "efficacy": {
        "orr": 45.2,
        "pfs_improvement": 4.8,
        "os_improvement": 3.2,
    },
    "safety": {
        "serious_ae_rate": 12.5,
        "treatment_discontinuation_rate": 8.3,
    },
    "evidence_level": "RCT",
    "is_novel_mechanism": False,
    "is_domestic": True,
    "is_expensive": True,
    "orphan_drug": False,
    "unmet_need": False,
    "superior_to_standard": True,
    "icer": 2.8,  # 万元/QALY
    "estimated_annual_sales": 5_000_000_000,  # 50亿
    "dosing_convenience": 0.8,
    "is_original": False,
    # 药物学参数
    "bioavailability": 85,
    "half_life_hours": 18,
    "drug_interactions": ["CYP3A4抑制剂", "华法林"],
    "target_validation": "validated",
    "selectivity_score": 0.85,
    "dose_response_slope": 0.75,
    "administration_route": "静脉",
    "storage_requirement": "cold_chain",
    "black_box_warning": False,
    "qt_prolongation_risk": False,
    # 流行病学参数
    "prevalence_per_100k": 560,
    "diagnosis_rate": 0.65,
    "rwe_available": True,
    "rwe_sample_size": 5000,
    "rwe_consistent_with_rct": True,
    "qol_improvement": 0.12,
    "tam_billion": 280,
    "market_cagr": 0.18,
    "eligible_patient_count": 820000,
    # 药物经济学参数
    "heor_study_type": "markov_model",
    "utility_source": "rct_measured",
    "sensitivity_analysis_done": True,
    "hta_dossier_ready": True,
    "incremental_qaly": 0.85,
    "reduces_hospitalization": True,
    "international_hta_results": [
        {"country": "UK", "approved": True},
        {"country": "Germany", "approved": True},
        {"country": "Australia", "approved": False},
    ],
    "patent_remaining_years": 12,
    # 医保参数
    "competitors_in_insurance": 2,
    "restricted_use": False,
    "outpatient_eligible": True,
    "reduces_total_cost": False,
    "drg_exempt": False,
    "innovation_exemption": False,
    # 临床参数
    "primary_endpoint_met": True,
    "guideline_recommendation": "category_2a",
    "countries_approved": 15,
    # 市场参数
    "num_competitors": 4,
    "first_in_class": False,
    "best_in_class": True,
    "me_too": False,
    "breakthrough_therapy": False,
    "kol_endorsed": True,
    "company_type": "MNC",
    "hospital_access_ease": 0.5,
    "otc_eligible": False,
    "retail_available": False,
    "dtp_available": True,
    "ecommerce_eligible": False,
    "oral_administration": False,
    "requires_special_equipment": False,
    "biomarker_required": True,
    "diagnostic_availability": 0.6,
    # 定价参数
    "international_prices": {
        "us": 150000,
        "japan": 80000,
        "eu": 95000,
    },
}


def run_simulation():
    """运行模拟"""
    start_time = time.time()

    config = SimulationConfig(
        drug=SAMPLE_DRUG,
        num_agents=1800,        # 400医生 + 1000患者 + 400专家 + 1医保
        simulation_months=24,
        random_seed=42,
        parallel_evaluation=True,
        max_workers=8,
        deliberation_rounds=8,
        convergence_threshold=0.01,
    )

    engine = SimulationEngine(config)
    result = engine.run()

    elapsed = time.time() - start_time

    # ═══ 输出结果 ═══
    print()
    print("=" * 60)
    print("  📊 PharmaSim 多维度仿真结果")
    print("=" * 60)

    summary = result["summary"]
    ms = result["multidim_summary"]

    print(f"\n  💊 药品: {result['drug_name']}")
    print(f"  🤖 Agent总数: {result['num_agents']}")
    print(f"  ⏱️ 仿真耗时: {elapsed:.1f}秒")
    print()

    # 多维度评估
    print("  ┌─────────────────────────────────────────┐")
    print("  │         多维度专家评估结果              │")
    print("  ├─────────────────────────────────────────┤")
    for dim, data in ms.items():
        if dim == "综合评估":
            continue
        score = data["avg_score"]
        bar = "█" * int(score * 20) + "░" * (20 - int(score * 20))
        emoji = "🟢" if score > 0.7 else ("🟡" if score > 0.5 else "🔴")
        print(f"  │ {emoji} {dim:<12} {bar} {score:.3f}  ({data['agent_count']}人) │")
    print("  └─────────────────────────────────────────┘")

    if "综合评估" in ms:
        comp = ms["综合评估"]
        print(f"\n  🎯 综合得分: {comp['overall_score']:.3f}")
        print(f"  📋 综合建议: {comp['recommendation']}")
        print(f"  👥 参与专家: {comp['total_experts']}人 / {comp['num_dimensions']}维度")

    # 社交协商结果
    ds = result.get("deliberation_summary", {})
    if ds:
        print(f"\n  ── 1000用户Agent社交协商结果 ──")
        print(f"  🔄 协商轮次: {ds.get('num_rounds', 0)}")
        print(f"  ✅ 收敛: {'是' if ds.get('convergence_achieved') else '否'}")
        print(f"  💡 最终平均用药意愿: {ds.get('final_avg_willingness', 0):.3f}")
        wd = ds.get("willingness_distribution", {})
        print(f"  📊 意愿分布: 积极={wd.get('high', 0):.1%} | "
              f"中立={wd.get('medium', 0):.1%} | 怀疑={wd.get('low', 0):.1%}")
        clusters = ds.get("opinion_clusters", {})
        if clusters:
            print(f"  👥 意见集群: ", end="")
            print(" | ".join(f"{k}={v}人" for k, v in clusters.items()))

        # 协商轮次演化
        rounds = ds.get("round_history", [])
        if rounds:
            print(f"\n  ── 协商轮次演化 ──")
            for r in rounds[-4:]:  # 显示最后4轮
                w = r["avg_willingness"]
                bar = "█" * int(w * 30) + "░" * (30 - int(w * 30))
                print(f"  第{r['round']:>2}轮: {bar} {w:.3f} (改变{r['opinion_shifts']}人)")

    # 网络统计
    ns = result.get("network_stats", {})
    if ns:
        print(f"\n  ── 社交网络统计 ──")
        print(f"  🔗 网络节点: {ns.get('num_nodes', 0)}")
        print(f"  🔗 网络边数: {ns.get('num_edges', 0)}")
        print(f"  📊 平均度数: {ns.get('avg_degree', 0):.1f}")
        print(f"  🏘️ 社区数: {ns.get('num_communities', 0)}")
        print(f"  ⭐ 枢纽节点: {ns.get('hub_count', 0)}")

    # 市场表现
    print(f"\n  ── 市场表现预测 ──")
    print(f"  📈 峰值月份: 第{summary['peak_month']}月")
    print(f"  📈 峰值处方量: {summary['peak_prescription_volume']:,} 张/月")
    print(f"  📈 峰值渗透率: {summary['peak_market_penetration']:.1%}")
    print()
    print(f"  💰 第一年收入: {summary['year1_revenue']/1e8:.1f} 亿元")
    print(f"  💰 第二年收入: {summary['year2_revenue']/1e8:.1f} 亿元")
    print(f"  💰 总收入: {summary['total_revenue']/1e8:.1f} 亿元")
    print()
    print(f"  👨‍⚕️ 最终医生采纳率: {summary['final_adoption_rate']:.1%}")
    print(f"  😊 平均患者满意度: {summary['avg_patient_satisfaction']:.1%}")
    print(f"  💡 社交协商意愿: {summary.get('final_social_willingness', 0):.3f}")
    print(f"  🏥 医保影响: {summary['insurance_impact']}")

    if result.get("payer_decision"):
        pd = result["payer_decision"]
        print()
        print(f"  🏛️ 医保准入: {'✅ 通过' if pd['will_cover'] else '❌ 未通过'}")
        print(f"  🏛️ 谈判价格: ¥{pd['negotiation_price']:,.0f}")
        print(f"  🏛️ 报销比例: {pd['reimbursement_ratio']:.0%}")

    # 各维度关键发现
    print(f"\n  ── 各维度关键发现 ──")
    for dim, data in ms.items():
        if dim == "综合评估":
            continue
        print(f"\n  【{dim}】 (置信度: {data['confidence']:.2f})")
        if data["top_findings"]:
            print(f"    ✅ {'; '.join(data['top_findings'][:2])}")
        if data["top_risks"]:
            print(f"    ⚠️ {'; '.join(data['top_risks'][:2])}")

    # 保存结果
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "simulation_result.json"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 详细结果已保存: {output_path}")

    return result


if __name__ == "__main__":
    run_simulation()
