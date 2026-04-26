"""
PharmaSim — 顶层模拟引擎便捷接口
封装 src/simulation/simulation_engine.py，提供简化的对外API
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, field

# 导入核心模拟引擎
from simulation.simulation_engine import SimulationConfig, SimulationEngine


@dataclass
class QuickSimulationRequest:
    """快速模拟请求"""
    drug_name: str
    indication: str
    mechanism: str = ""
    price: float = 0.0
    efficacy_rate: float = 0.7
    safety_score: float = 0.8
    num_agents: int = 1800
    simulation_months: int = 24
    random_seed: int = 42
    regions: List[str] = field(default_factory=lambda: ["北京", "上海", "广州", "深圳"])


class PharmaSimEngine:
    """
    PharmaSim 顶层模拟引擎
    
    提供简化的药物市场准入模拟接口，支持：
    - 快速模拟（单药物场景）
    - 对比模拟（多药物对比）
    - 批量场景分析
    
    示例：
        >>> engine = PharmaSimEngine()
        >>> result = engine.quick_simulate(
        ...     drug_name="新药A",
        ...     indication="非小细胞肺癌",
        ...     efficacy_rate=0.75,
        ...     price=15000
        ... )
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self._load_templates()
    
    def _load_templates(self):
        """加载模拟模板"""
        self.templates = {}
        template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data", "simulation-templates.json"
        )
        if os.path.exists(template_path):
            with open(template_path) as f:
                data = json.load(f)
                for tpl in data.get("templates", []):
                    self.templates[tpl["id"]] = tpl
    
    def quick_simulate(
        self,
        drug_name: str,
        indication: str,
        mechanism: str = "",
        price: float = 0.0,
        efficacy_rate: float = 0.7,
        safety_score: float = 0.8,
        num_agents: int = 1800,
        simulation_months: int = 24,
        random_seed: int = 42,
        regions: Optional[List[str]] = None
    ) -> Dict:
        """快速模拟"""
        if regions is None:
            regions = ["北京", "上海", "广州", "深圳", "成都", "武汉"]
        
        drug = {
            "name": drug_name,
            "indication": indication,
            "mechanism": mechanism,
            "price": price,
            "efficacy_rate": efficacy_rate,
            "safety_score": safety_score
        }
        
        config = SimulationConfig(
            drug=drug,
            num_agents=num_agents,
            simulation_months=simulation_months,
            random_seed=random_seed,
            region_focus=regions
        )
        
        engine = SimulationEngine(config)
        return engine.run()
    
    def compare_drugs(
        self,
        drugs: List[Dict],
        num_agents: int = 1800,
        simulation_months: int = 24
    ) -> Dict:
        """对比模拟多个药物"""
        results = {}
        for drug in drugs:
            name = drug.get("name", "未知")
            result = self.quick_simulate(
                drug_name=name,
                indication=drug.get("indication", ""),
                mechanism=drug.get("mechanism", ""),
                price=drug.get("price", 0),
                efficacy_rate=drug.get("efficacy_rate", 0.7),
                safety_score=drug.get("safety_score", 0.8),
                num_agents=num_agents,
                simulation_months=simulation_months
            )
            results[name] = result
        
        return {
            "individual_results": results,
            "comparison": self._generate_comparison(results)
        }
    
    def scenario_analysis(
        self,
        drug_name: str,
        indication: str,
        price_range: List[float],
        efficacy_range: List[float],
        num_agents: int = 1000,
        simulation_months: int = 12
    ) -> Dict:
        """场景分析 — 价格和疗效的二维扫描"""
        scenario_results = []
        
        for price in price_range:
            for efficacy in efficacy_range:
                result = self.quick_simulate(
                    drug_name=drug_name,
                    indication=indication,
                    price=price,
                    efficacy_rate=efficacy,
                    num_agents=num_agents,
                    simulation_months=simulation_months
                )
                scenario_results.append({
                    "price": price,
                    "efficacy": efficacy,
                    "market_penetration": result.get("final_metrics", {}).get("market_penetration", 0),
                    "revenue": result.get("final_metrics", {}).get("total_revenue", 0),
                    "adoption_rate": result.get("final_metrics", {}).get("doctor_adoption_rate", 0)
                })
        
        return {
            "drug_name": drug_name,
            "indication": indication,
            "scenarios": scenario_results,
            "best_scenario": max(scenario_results, key=lambda x: x["revenue"]) if scenario_results else None
        }
    
    def _generate_comparison(self, results: Dict) -> Dict:
        """生成对比摘要"""
        comparison = []
        for name, result in results.items():
            metrics = result.get("final_metrics", {})
            comparison.append({
                "drug": name,
                "market_penetration": metrics.get("market_penetration", 0),
                "total_revenue": metrics.get("total_revenue", 0),
                "doctor_adoption": metrics.get("doctor_adoption_rate", 0),
                "patient_satisfaction": metrics.get("patient_satisfaction", 0)
            })
        
        comparison.sort(key=lambda x: x["market_penetration"], reverse=True)
        return comparison
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """获取模拟模板"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        return [
            {"id": k, "name": v.get("name", k), "description": v.get("description", "")}
            for k, v in self.templates.items()
        ]


if __name__ == "__main__":
    engine = PharmaSimEngine()
    
    # 快速模拟
    result = engine.quick_simulate(
        drug_name="免疫检查点抑制剂X",
        indication="非小细胞肺癌",
        mechanism="PD-1/PD-L1抑制",
        price=28000,
        efficacy_rate=0.72,
        safety_score=0.85,
        num_agents=500,
        simulation_months=12
    )
    
    print("模拟完成！")
    print(json.dumps(result.get("final_metrics", {}), indent=2, ensure_ascii=False, default=str))
