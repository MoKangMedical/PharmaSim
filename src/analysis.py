"""
PharmaSim — 结果分析模块
提供模拟结果的统计分析、可视化和报告生成功能
"""

import json
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class AnalysisResult:
    """分析结果"""
    metric_name: str
    value: float
    unit: str = ""
    confidence_interval: Optional[Tuple[float, float]] = None
    interpretation: str = ""


class SimulationAnalyzer:
    """
    模拟结果分析器
    
    对PharmaSim模拟输出进行多维度分析：
    - 市场渗透分析
    - 医生采纳行为分析
    - 患者满意度分析
    - 收入预测分析
    - 敏感性分析
    
    示例：
        >>> analyzer = SimulationAnalyzer(simulation_result)
        >>> report = analyzer.generate_report()
    """
    
    def __init__(self, simulation_result: Dict):
        self.result = simulation_result
        self.monthly_snapshots = simulation_result.get("monthly_snapshots", [])
        self.final_metrics = simulation_result.get("final_metrics", {})
        self.agent_results = simulation_result.get("agent_results", {})
        self.drug_info = simulation_result.get("drug_info", {})
    
    def market_penetration_analysis(self) -> Dict:
        """市场渗透分析"""
        if not self.monthly_snapshots:
            return {"error": "无月度数据"}
        
        penetrations = [s.get("market_penetration", 0) for s in self.monthly_snapshots]
        
        # 增长率计算
        growth_rates = []
        for i in range(1, len(penetrations)):
            if penetrations[i-1] > 0:
                rate = (penetrations[i] - penetrations[i-1]) / penetrations[i-1]
                growth_rates.append(rate)
        
        # 采用阶段判断
        final_penetration = penetrations[-1] if penetrations else 0
        if final_penetration < 0.05:
            stage = "引入期"
        elif final_penetration < 0.20:
            stage = "成长期"
        elif final_penetration < 0.50:
            stage = "成熟期"
        else:
            stage = "饱和期"
        
        return {
            "final_penetration": final_penetration,
            "max_penetration": max(penetrations) if penetrations else 0,
            "avg_monthly_growth": sum(growth_rates) / len(growth_rates) if growth_rates else 0,
            "adoption_stage": stage,
            "months_to_10pct": self._months_to_threshold(penetrations, 0.10),
            "months_to_20pct": self._months_to_threshold(penetrations, 0.20),
            "penetration_curve": penetrations
        }
    
    def doctor_adoption_analysis(self) -> Dict:
        """医生采纳分析"""
        if not self.monthly_snapshots:
            return {"error": "无月度数据"}
        
        adoption_rates = [s.get("doctor_adoption_rate", 0) for s in self.monthly_snapshots]
        new_prescribers = [s.get("new_prescribers", 0) for s in self.monthly_snapshots]
        cumulative = [s.get("cumulative_prescribers", 0) for s in self.monthly_snapshots]
        
        return {
            "final_adoption_rate": adoption_rates[-1] if adoption_rates else 0,
            "total_prescribers": cumulative[-1] if cumulative else 0,
            "avg_new_per_month": sum(new_prescribers) / len(new_prescribers) if new_prescribers else 0,
            "peak_new_prescribers_month": new_prescribers.index(max(new_prescribers)) + 1 if new_prescribers else 0,
            "adoption_curve": adoption_rates
        }
    
    def revenue_analysis(self) -> Dict:
        """收入分析"""
        if not self.monthly_snapshots:
            return {"error": "无月度数据"}
        
        revenues = [s.get("revenue", 0) for s in self.monthly_snapshots]
        
        # 年化收入
        total_revenue = sum(revenues)
        months = len(revenues)
        annualized = total_revenue / max(months, 1) * 12
        
        # 峰值月份
        peak_month = revenues.index(max(revenues)) + 1 if revenues else 0
        
        return {
            "total_revenue": total_revenue,
            "annualized_revenue": annualized,
            "avg_monthly_revenue": total_revenue / max(months, 1),
            "peak_revenue_month": peak_month,
            "peak_revenue": max(revenues) if revenues else 0,
            "revenue_curve": revenues
        }
    
    def patient_satisfaction_analysis(self) -> Dict:
        """患者满意度分析"""
        if not self.monthly_snapshots:
            return {"error": "无月度数据"}
        
        satisfactions = [s.get("patient_satisfaction", 0) for s in self.monthly_snapshots]
        
        return {
            "final_satisfaction": satisfactions[-1] if satisfactions else 0,
            "avg_satisfaction": sum(satisfactions) / len(satisfactions) if satisfactions else 0,
            "min_satisfaction": min(satisfactions) if satisfactions else 0,
            "max_satisfaction": max(satisfactions) if satisfactions else 0,
            "satisfaction_trend": "上升" if len(satisfactions) > 1 and satisfactions[-1] > satisfactions[0] else "稳定",
            "satisfaction_curve": satisfactions
        }
    
    def social_network_analysis(self) -> Dict:
        """社交网络影响分析"""
        if not self.monthly_snapshots:
            return {"error": "无月度数据"}
        
        social_willingness = [s.get("social_willingness", 0) for s in self.monthly_snapshots]
        
        return {
            "final_social_willingness": social_willingness[-1] if social_willingness else 0,
            "avg_social_willingness": sum(social_willingness) / len(social_willingness) if social_willingness else 0,
            "social_influence_factor": (
                social_willingness[-1] / max(social_willingness[0], 0.001)
                if social_willingness and social_willingness[0] > 0 else 1.0
            )
        }
    
    def competitive_positioning(self, competitor_data: Optional[Dict] = None) -> Dict:
        """竞争定位分析"""
        my_metrics = {
            "efficacy": self.drug_info.get("efficacy_rate", 0),
            "safety": self.drug_info.get("safety_score", 0),
            "price": self.drug_info.get("price", 0),
            "market_penetration": self.final_metrics.get("market_penetration", 0)
        }
        
        positioning = {"self": my_metrics}
        
        if competitor_data:
            for name, data in competitor_data.items():
                positioning[name] = {
                    "efficacy": data.get("efficacy_rate", 0),
                    "safety": data.get("safety_score", 0),
                    "price": data.get("price", 0),
                    "market_penetration": data.get("market_penetration", 0)
                }
        
        # 综合评分
        score = (
            my_metrics["efficacy"] * 0.35 +
            my_metrics["safety"] * 0.25 +
            (1 - my_metrics["price"] / 100000) * 0.20 +
            my_metrics["market_penetration"] * 0.20
        )
        
        return {
            "positioning": positioning,
            "composite_score": score,
            "grade": "A" if score > 0.8 else ("B" if score > 0.6 else ("C" if score > 0.4 else "D"))
        }
    
    def generate_report(self) -> Dict:
        """生成完整分析报告"""
        return {
            "drug_info": self.drug_info,
            "market_penetration": self.market_penetration_analysis(),
            "doctor_adoption": self.doctor_adoption_analysis(),
            "revenue": self.revenue_analysis(),
            "patient_satisfaction": self.patient_satisfaction_analysis(),
            "social_network": self.social_network_analysis(),
            "competitive_positioning": self.competitive_positioning(),
            "executive_summary": self._executive_summary()
        }
    
    def _executive_summary(self) -> str:
        """生成执行摘要"""
        mp = self.market_penetration_analysis()
        rev = self.revenue_analysis()
        doc = self.doctor_adoption_analysis()
        
        drug_name = self.drug_info.get("name", "该药物")
        
        summary = f"""
【{drug_name}模拟执行摘要】

1. 市场表现：最终市场渗透率 {mp['final_penetration']:.1%}，处于{mp['adoption_stage']}
2. 医生采纳：{doc['total_prescribers']}位处方医生，采纳率 {doc['final_adoption_rate']:.1%}
3. 收入表现：累计收入 ¥{rev['total_revenue']:,.0f}，月均 ¥{rev['avg_monthly_revenue']:,.0f}
4. 综合评级：{self.competitive_positioning()['grade']}级
        """.strip()
        
        return summary
    
    def _months_to_threshold(self, penetrations: List[float], threshold: float) -> Optional[int]:
        """计算达到阈值所需的月数"""
        for i, p in enumerate(penetrations):
            if p >= threshold:
                return i + 1
        return None
    
    def summary(self) -> str:
        """文本摘要"""
        report = self.generate_report()
        mp = report["market_penetration"]
        rev = report["revenue"]
        doc = report["doctor_adoption"]
        
        lines = [
            "=" * 60,
            "📊 PharmaSim 模拟结果分析报告",
            "=" * 60,
            f"药物: {self.drug_info.get('name', 'N/A')}",
            f"适应症: {self.drug_info.get('indication', 'N/A')}",
            "-" * 60,
            f"📈 市场渗透率: {mp['final_penetration']:.1%} ({mp['adoption_stage']})",
            f"👨‍⚕️ 医生采纳率: {doc['final_adoption_rate']:.1%} ({doc['total_prescribers']}人)",
            f"💰 累计收入: ¥{rev['total_revenue']:,.0f}",
            f"👥 患者满意度: {report['patient_satisfaction']['final_satisfaction']:.2f}",
            f"🌐 社交网络影响: {report['social_network']['social_influence_factor']:.2f}x",
            f"🏆 综合评级: {report['competitive_positioning']['grade']}",
            "=" * 60
        ]
        
        return "\n".join(lines)


def batch_analyze(results: List[Dict]) -> Dict:
    """批量分析多个模拟结果"""
    analyses = []
    for result in results:
        analyzer = SimulationAnalyzer(result)
        report = analyzer.generate_report()
        analyses.append({
            "drug": result.get("drug_info", {}).get("name", "未知"),
            "penetration": report["market_penetration"]["final_penetration"],
            "revenue": report["revenue"]["total_revenue"],
            "grade": report["competitive_positioning"]["grade"]
        })
    
    analyses.sort(key=lambda x: x["penetration"], reverse=True)
    
    return {
        "rankings": analyses,
        "best_performer": analyses[0] if analyses else None,
        "total_drugs_analyzed": len(analyses)
    }


if __name__ == "__main__":
    # 模拟示例数据
    mock_result = {
        "drug_info": {"name": "免疫检查点抑制剂X", "indication": "NSCLC", "efficacy_rate": 0.72, "safety_score": 0.85, "price": 28000},
        "monthly_snapshots": [
            {"month": i+1, "market_penetration": min(0.35, 0.02 * (i+1) + 0.01 * (i+1)**0.5),
             "revenue": 50000 * (i+1) * (1 + 0.05 * i),
             "doctor_adoption_rate": min(0.45, 0.03 * (i+1)),
             "patient_satisfaction": min(0.92, 0.70 + 0.01 * (i+1)),
             "new_prescribers": max(5, 20 - i),
             "cumulative_prescribers": min(200, 10 * (i+1)),
             "social_willingness": min(0.8, 0.5 + 0.02 * i)}
            for i in range(24)
        ],
        "final_metrics": {"market_penetration": 0.35, "total_revenue": 30000000, "doctor_adoption_rate": 0.45}
    }
    
    analyzer = SimulationAnalyzer(mock_result)
    print(analyzer.summary())
