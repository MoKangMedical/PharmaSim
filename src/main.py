"""
PharmaSim - 主入口
运行药品上市模拟的 CLI 和 API 服务
"""

import json
import sys
import os

# 添加 src 到路径
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
}


def run_simulation():
    """运行模拟"""
    print("=" * 60)
    print("  PharmaSim - 药品上市预测仿真平台")
    print("  基于多智能体AI模拟的药品上市表现预测")
    print("=" * 60)
    print()
    
    config = SimulationConfig(
        drug=SAMPLE_DRUG,
        num_doctors=500,
        num_patients=5000,
        simulation_months=24,
        random_seed=42,
    )
    
    engine = SimulationEngine(config)
    result = engine.run()
    
    # 输出结果
    print()
    print("=" * 60)
    print("  📊 模拟结果汇总")
    print("=" * 60)
    
    summary = result["summary"]
    print(f"  药品: {result['drug_name']}")
    print(f"  模拟时长: {result['simulation_months']} 个月")
    print()
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
    print(f"  🏥 医保影响: {summary['insurace_impact']}")
    
    if result.get("payer_decision"):
        pd = result["payer_decision"]
        print()
        print(f"  🏛️ 医保准入: {'✅ 通过' if pd['will_cover'] else '❌ 未通过'}")
        print(f"  🏛️ 谈判价格: ¥{pd['negotiation_price']:,.0f}")
        print(f"  🏛️ 报销比例: {pd['reimbursement_ratio']:.0%}")
    
    # 保存详细结果
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                "data", "simulation_result.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n  💾 详细结果已保存: {output_path}")
    
    return result


if __name__ == "__main__":
    run_simulation()
