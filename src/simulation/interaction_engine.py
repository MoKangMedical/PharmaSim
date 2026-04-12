"""
PharmaSim - 决策交互引擎
仿照Aaru实现Agent间的意见传播、权重匹配、多轮协商
"""

import random
import math
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from simulation.social_network import SocialNetwork


@dataclass
class AgentOpinion:
    """Agent对药品的初始意见"""
    agent_id: str
    willingness: float          # 用药意愿 0-1
    confidence: float           # 意见置信度 0-1
    dimensions: Dict[str, float] = field(default_factory=dict)  # 各维度评分
    reasons: List[str] = field(default_factory=list)
    influenced_by: List[str] = field(default_factory=list)  # 受谁影响
    round_history: List[float] = field(default_factory=list)  # 每轮意愿变化


@dataclass
class InteractionRound:
    """单轮交互记录"""
    round_num: int
    active_influences: int       # 有效影响次数
    opinion_shifts: int          # 意见改变次数
    avg_willingness: float       # 平均意愿
    willingness_std: float       # 意愿标准差
    convergence_rate: float      # 收敛率
    polarized_clusters: int      # 极化集群数


@dataclass
class DeliberationResult:
    """多轮协商结果"""
    num_rounds: int
    final_opinions: Dict[str, AgentOpinion]
    round_history: List[InteractionRound]
    convergence_achieved: bool
    final_avg_willingness: float
    willingness_distribution: Dict[str, float]  # "high"/"medium"/"low"占比
    influencer_ranking: List[Tuple[str, float]]  # 影响力排名
    opinion_clusters: Dict[str, List[str]]       # 意见集群


class InteractionEngine:
    """
    决策交互引擎 - Aaru风格的多Agent协商

    核心机制:
    1. 意见初始化: 基于Agent属性和专家评估
    2. 影响力传播: 通过社交网络传播意见
    3. 权重匹配: 影响力=专业度×置信度×社交权重
    4. 多轮协商: 迭代直到收敛或达到最大轮次
    5. 涌现行为: 最终决策从个体交互中涌现
    """

    def __init__(self, network: SocialNetwork, random_seed: int = 42):
        self.network = network
        self._rng = random.Random(random_seed)
        self.opinions: Dict[str, AgentOpinion] = {}
        self.round_history: List[InteractionRound] = []

    def run_deliberation(self, patients: list, drug: dict,
                          multidim_scores: Dict[str, float],
                          payer_decision: dict,
                          max_rounds: int = 8,
                          convergence_threshold: float = 0.01) -> DeliberationResult:
        """
        运行完整协商过程

        Args:
            patients: 患者Agent列表
            drug: 药品信息
            multidim_scores: 多维度专家评估得分
            payer_decision: 医保决策
            max_rounds: 最大协商轮次
            convergence_threshold: 收敛阈值

        Returns:
            DeliberationResult
        """
        print(f"   🔄 启动决策交互引擎: {len(patients)}个患者Agent")

        # Phase 1: 初始化意见
        self._initialize_opinions(patients, drug, multidim_scores, payer_decision)
        initial_avg = self._calc_avg_willingness()
        print(f"   📝 意见初始化完成: 平均意愿={initial_avg:.3f}")

        # Phase 2: 多轮协商
        converged = False
        for round_num in range(1, max_rounds + 1):
            # 外部事件冲击 (模拟信息传播)
            self._apply_external_shock(round_num, drug, payer_decision)

            round_result = self._run_interaction_round(
                round_num, drug, multidim_scores, payer_decision
            )
            self.round_history.append(round_result)

            print(f"   🔄 第{round_num}轮: 平均意愿={round_result.avg_willingness:.3f}, "
                  f"意见改变={round_result.opinion_shifts}, "
                  f"收敛率={round_result.convergence_rate:.3f}")

            # 检查收敛
            if round_result.convergence_rate < convergence_threshold:
                converged = True
                print(f"   ✅ 第{round_num}轮达成收敛!")
                break

        # Phase 3: 汇总结果
        final_avg = self._calc_avg_willingness()
        distribution = self._calc_willingness_distribution()
        influencer_ranking = self._calc_influencer_ranking()
        clusters = self._identify_opinion_clusters()

        return DeliberationResult(
            num_rounds=len(self.round_history),
            final_opinions=self.opinions,
            round_history=self.round_history,
            convergence_achieved=converged,
            final_avg_willingness=final_avg,
            willingness_distribution=distribution,
            influencer_ranking=influencer_ranking[:20],
            opinion_clusters=clusters,
        )

    def _initialize_opinions(self, patients: list, drug: dict,
                              multidim_scores: Dict[str, float],
                              payer_decision: dict):
        """初始化每个患者的意见 - 基于个体差异产生真实分布"""
        insurance_covered = payer_decision.get("will_cover", False)
        price = drug.get("price", 0)

        # 多维度综合得分
        clin_score = multidim_scores.get("临床评估", 0.5)
        price_score = multidim_scores.get("定价评估", 0.5)
        ins_score = multidim_scores.get("医保评估", 0.5)
        pharm_score = multidim_scores.get("药物学评估", 0.5)

        for pt in patients:
            # 个体化基础意愿 - 基于患者属性差异
            base = 0.4  # 起始基准

            # 1. 经济水平对价格的敏感度
            econ_sensitivity = 0.3
            if hasattr(pt, 'economic_level'):
                econ = pt.economic_level.value if hasattr(pt.economic_level, 'value') else str(pt.economic_level)
                if "高" in econ:
                    base += 0.15
                    econ_sensitivity = 0.1
                elif "低" in econ:
                    base -= 0.1
                    econ_sensitivity = 0.5

            # 2. 价格因素
            if insurance_covered:
                base += 0.15 * (ins_score + 0.3)
            else:
                base -= econ_sensitivity * 0.3
                if price > 20000:
                    base -= econ_sensitivity * 0.2

            # 3. 疗效感知 (受信息来源影响)
            info_weight = 0.6
            if hasattr(pt, 'information_source'):
                src = pt.information_source.value if hasattr(pt.information_source, 'value') else str(pt.information_source)
                if "医生" in src:
                    info_weight = 0.8
                elif "病友" in src:
                    info_weight = 0.6
                elif "网络" in src:
                    info_weight = 0.5
                elif "家人" in src:
                    info_weight = 0.4
            base += clin_score * info_weight * 0.3

            # 4. 疾病阶段 - 晚期患者更积极
            if hasattr(pt, 'disease_stage'):
                stage = str(pt.disease_stage)
                if "晚期" in stage:
                    base += 0.15
                elif "中期" in stage:
                    base += 0.05

            # 5. 依从性影响
            if hasattr(pt, 'adherence_score'):
                base += (pt.adherence_score - 0.5) * 0.15

            # 6. 品牌偏好
            if hasattr(pt, 'brand_preference'):
                pref = str(pt.brand_preference)
                if pref == "original" and drug.get("is_original", False):
                    base += 0.1
                elif pref == "generic" and not drug.get("is_original", True):
                    base += 0.08

            # 7. 药物学因素 (患者感知)
            base += pharm_score * 0.05

            # 8. 个体随机噪声 (模拟不可观察因素)
            noise = self._rng.gauss(0, 0.12)
            base += noise

            willingness = max(0.05, min(0.95, base))

            # 置信度 - 基于信息充分度
            confidence = 0.3 + self._rng.random() * 0.4
            if info_weight > 0.7:
                confidence += 0.15

            # 多维度感知
            dimensions = {}
            for dim_name, score in multidim_scores.items():
                if dim_name == "综合评估":
                    continue
                dim_weight = self._get_patient_dimension_weight(pt, dim_name)
                dimensions[dim_name] = score * dim_weight + 0.5 * (1 - dim_weight)

            # 决策理由
            reasons = []
            if willingness > 0.6:
                if clin_score > 0.6:
                    reasons.append("疗效数据良好")
                if insurance_covered:
                    reasons.append("医保可报销")
            elif willingness < 0.4:
                if not insurance_covered:
                    reasons.append("自费负担重")
                if price > 15000:
                    reasons.append("价格较高")

            self.opinions[pt.agent_id] = AgentOpinion(
                agent_id=pt.agent_id,
                willingness=willingness,
                confidence=confidence,
                dimensions=dimensions,
                reasons=reasons if reasons else ["综合考虑"],
                round_history=[willingness],
            )

    def _get_patient_dimension_weight(self, patient, dim_name: str) -> float:
        """患者对不同维度的关注度"""
        weights = {
            "临床评估": 0.7,       # 患者普遍关注疗效
            "药物学评估": 0.2,     # 患者不太懂药理
            "定价评估": 0.8,       # 价格敏感
            "医保评估": 0.9,       # 医保非常重要
            "市场评估": 0.3,       # 患者不关注市场
            "流行病学评估": 0.1,   # 患者不关注流行病学
            "药物经济学评估": 0.2,  # 患者不关注经济学
        }

        # 经济水平调整
        if hasattr(patient, 'economic_level'):
            econ = patient.economic_level.value if hasattr(patient.economic_level, 'value') else str(patient.economic_level)
            if "高" in econ and dim_name == "定价评估":
                weights["定价评估"] = 0.4  # 高收入不太在意价格
            elif "低" in econ:
                weights["定价评估"] = 0.95
                weights["医保评估"] = 0.95

        return weights.get(dim_name, 0.5)

    def _apply_external_shock(self, round_num: int, drug: dict, payer_decision: dict):
        """
        模拟外部事件冲击 - 信息在社交网络传播后影响群体意见

        类似Aaru的叙事追踪(narrative tracking)机制
        """
        shocks = {
            2: {
                "event": "媒体报道药品不良反应事件",
                "impact": -0.08,
                "affected_ratio": 0.3,
                "reason": "媒体负面报道",
            },
            3: {
                "event": "KOL专家公开推荐",
                "impact": 0.06,
                "affected_ratio": 0.2,
                "reason": "KOL推荐",
            },
            5: {
                "event": "病友社区分享正面使用体验",
                "impact": 0.05,
                "affected_ratio": 0.4,
                "reason": "病友正面反馈",
            },
            7: {
                "event": "医保谈判结果公布",
                "impact": 0.07 if payer_decision.get("will_cover") else -0.12,
                "affected_ratio": 0.6,
                "reason": "医保谈判结果",
            },
        }

        shock = shocks.get(round_num)
        if not shock:
            return

        impact = shock["impact"]
        affected_count = int(len(self.opinions) * shock["affected_ratio"])

        # 枢纽节点(KOL)先受影响，再传播
        hub_ids = [nid for nid, node in self.network.nodes.items() if node.is_hub and nid in self.opinions]

        # 随机选一批Agent受影响
        all_ids = list(self.opinions.keys())
        affected = self._rng.sample(all_ids, min(affected_count, len(all_ids)))

        for agent_id in affected:
            op = self.opinions[agent_id]
            # 影响幅度受信心度调制
            actual_impact = impact * (1 - op.confidence * 0.3)
            op.willingness = max(0.05, min(0.95, op.willingness + actual_impact))
            op.reasons.append(shock["reason"])
            op.round_history.append(op.willingness)

    def _run_interaction_round(self, round_num: int, drug: dict,
                                multidim_scores: Dict[str, float],
                                payer_decision: dict) -> InteractionRound:
        """运行一轮交互"""
        active_influences = 0
        opinion_shifts = 0

        # 随机打乱交互顺序
        agent_ids = list(self.opinions.keys())
        self._rng.shuffle(agent_ids)

        # 每个Agent受邻居影响
        new_willingness = {}

        for agent_id in agent_ids:
            current_opinion = self.opinions[agent_id]
            neighbors = self.network.get_neighbors(agent_id)

            if not neighbors:
                continue

            # 收集邻居意见
            neighbor_influences = []
            for neighbor_id, edge_weight in neighbors:
                if neighbor_id in self.opinions:
                    neighbor_opinion = self.opinions[neighbor_id]
                    # 计算影响强度
                    influence = self._calc_influence(
                        current_opinion, neighbor_opinion, edge_weight, round_num
                    )
                    if influence > 0.01:
                        neighbor_influences.append((neighbor_id, neighbor_opinion.willingness, influence))
                        active_influences += 1

            if not neighbor_influences:
                continue

            # 加权平均更新意愿
            total_weight = 0
            weighted_sum = 0
            for _, willingness, influence in neighbor_influences:
                weighted_sum += willingness * influence
                total_weight += influence

            if total_weight > 0:
                neighbor_avg = weighted_sum / total_weight

                # 信心度调节 + 基础学习率
                base_lr = 0.35
                stubbornness = current_opinion.confidence * 0.4  # 高信心者更固执
                learning_rate = base_lr - stubbornness
                learning_rate = max(0.08, min(0.45, learning_rate))

                # 异质意见冲击更大
                opinion_diff = abs(current_opinion.willingness - neighbor_avg)
                if opinion_diff > 0.3:
                    learning_rate *= 1.3

                updated = current_opinion.willingness * (1 - learning_rate) + neighbor_avg * learning_rate
                updated = max(0, min(1, updated))
                new_willingness[agent_id] = updated

                # 记录影响来源
                if abs(updated - current_opinion.willingness) > 0.05:
                    opinion_shifts += 1
                    influencers = [n_id for n_id, _, inf in neighbor_influences if inf > 0.1]
                    current_opinion.influenced_by.extend(influencers[:3])

        # 批量更新
        for agent_id, new_w in new_willingness.items():
            old_w = self.opinions[agent_id].willingness
            self.opinions[agent_id].willingness = new_w
            self.opinions[agent_id].round_history.append(new_w)
            # 每轮稍微增加置信度
            self.opinions[agent_id].confidence = min(1.0, self.opinions[agent_id].confidence + 0.02)

        # 统计
        willingness_values = [op.willingness for op in self.opinions.values()]
        avg_w = sum(willingness_values) / len(willingness_values) if willingness_values else 0
        std_w = (sum((w - avg_w) ** 2 for w in willingness_values) / len(willingness_values)) ** 0.5

        # 收敛率 = 本轮与上轮平均意愿的差
        convergence = 1.0  # 默认不收敛
        if len(self.round_history) >= 1:
            prev_avg = self.round_history[-1].avg_willingness
            convergence = abs(avg_w - prev_avg)

        return InteractionRound(
            round_num=round_num,
            active_influences=active_influences,
            opinion_shifts=opinion_shifts,
            avg_willingness=round(avg_w, 4),
            willingness_std=round(std_w, 4),
            convergence_rate=round(convergence, 4),
            polarized_clusters=self._count_polarized_clusters(),
        )

    def _calc_influence(self, current: AgentOpinion, neighbor: AgentOpinion,
                         edge_weight: float, round_num: int) -> float:
        """
        计算邻居对当前Agent的影响强度

        Aaru式权重匹配:
        influence = edge_weight × confidence_gap × expertise_match × time_decay
        """
        # 1. 基础社交权重
        base = edge_weight

        # 2. 置信度差距: 高信心的人影响低信心的人
        confidence_gap = max(0, neighbor.confidence - current.confidence + 0.2)
        base *= (0.5 + confidence_gap)

        # 3. 意见相似度: 同质性偏好(同意见的人更容易被影响)
        opinion_similarity = 1 - abs(neighbor.willingness - current.willingness)
        base *= (0.3 + opinion_similarity * 0.7)  # 轻度同质偏好

        # 4. 时间衰减: 后面的轮次影响减弱
        time_decay = math.exp(-0.1 * (round_num - 1))
        base *= time_decay

        # 5. 枢纽节点加成
        node = self.network.nodes.get(neighbor.agent_id)
        if node and node.is_hub:
            base *= 1.5

        return min(base, 1.0)

    def _calc_avg_willingness(self) -> float:
        if not self.opinions:
            return 0
        return sum(op.willingness for op in self.opinions.values()) / len(self.opinions)

    def _calc_willingness_distribution(self) -> Dict[str, float]:
        """意愿分布"""
        if not self.opinions:
            return {"high": 0, "medium": 0, "low": 0}
        n = len(self.opinions)
        high = sum(1 for op in self.opinions.values() if op.willingness > 0.65) / n
        low = sum(1 for op in self.opinions.values() if op.willingness < 0.35) / n
        medium = 1 - high - low
        return {"high": round(high, 3), "medium": round(medium, 3), "low": round(low, 3)}

    def _calc_influencer_ranking(self) -> List[Tuple[str, float]]:
        """影响力排名"""
        influence_count = defaultdict(float)
        for op in self.opinions.values():
            for influencer in op.influenced_by:
                influence_count[influencer] += 1
        ranking = sorted(influence_count.items(), key=lambda x: x[1], reverse=True)
        return ranking

    def _count_polarized_clusters(self) -> int:
        """计算极化集群数"""
        high = sum(1 for op in self.opinions.values() if op.willingness > 0.7)
        low = sum(1 for op in self.opinions.values() if op.willingness < 0.3)
        if high > 10 and low > 10:
            return 2
        return 1

    def _identify_opinion_clusters(self) -> Dict[str, List[str]]:
        """识别意见集群"""
        clusters = {"enthusiast": [], "cautious": [], "skeptic": [], "neutral": []}
        for agent_id, op in self.opinions.items():
            if op.willingness > 0.7:
                clusters["enthusiast"].append(agent_id)
            elif op.willingness > 0.5:
                clusters["cautious"].append(agent_id)
            elif op.willingness > 0.3:
                clusters["neutral"].append(agent_id)
            else:
                clusters["skeptic"].append(agent_id)
        return clusters
