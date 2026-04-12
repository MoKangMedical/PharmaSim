"""
PharmaSim - 社交网络拓扑模块
仿照Aaru构建Agent间的社交关系网络
基于Watts-Strogatz小世界网络 + 层级影响力模型
"""

import random
import math
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class SocialEdge:
    """社交连接"""
    source: str
    target: str
    trust: float           # 信任度 0-1
    interaction_freq: float # 交互频率 0-1
    edge_type: str         # "peer" / "kol_follower" / "colleague" / "family" / "community"

    def influence_weight(self) -> float:
        """该连接的影响权重"""
        type_multipliers = {
            "kol_follower": 1.5,   # KOL对粉丝影响大
            "colleague": 1.2,      # 同事影响较大
            "family": 1.3,         # 家人影响大
            "peer": 1.0,           # 同龄人
            "community": 0.7,      # 社区
        }
        return self.trust * self.interaction_freq * type_multipliers.get(self.edge_type, 1.0)


@dataclass
class NetworkNode:
    """网络节点"""
    agent_id: str
    agent_type: str        # "patient" / "doctor" / "expert"
    influence_score: float # 社交影响力(中心度) 0-1
    expertise_areas: Dict[str, float] = field(default_factory=dict)  # 各领域的专业度
    neighbors: List[str] = field(default_factory=list)
    is_hub: bool = False   # 是否为枢纽节点(KOL)


class SocialNetwork:
    """
    社交网络 - 构建Agent间的关系拓扑

    支持:
    - 小世界网络 (Watts-Strogatz)
    - 无标度网络 (Barabasi-Albert)
    - 层级影响力网络
    - 病友社区网络
    """

    def __init__(self, random_seed: int = 42):
        self.nodes: Dict[str, NetworkNode] = {}
        self.edges: Dict[str, List[SocialEdge]] = defaultdict(list)  # agent_id -> [edges]
        self.communities: Dict[str, Set[str]] = {}  # 社区/群体
        self._rng = random.Random(random_seed)

    def build_patient_network(self, patients: list, doctors: list = None,
                               expert_agents: dict = None) -> dict:
        """
        构建患者社交网络

        网络结构:
        1. 患者-患者: 小世界网络 (同地区/同疾病社区)
        2. 患者-医生: 层级关系 (医生为KOL)
        3. 患者-病友社区: 社区归属
        4. 患者-专家: 弱连接 (信息源)
        """
        print(f"   🔗 构建社交网络: {len(patients)}患者节点")

        # 1. 注册所有患者节点
        for pt in patients:
            node = NetworkNode(
                agent_id=pt.agent_id,
                agent_type="patient",
                influence_score=self._calc_patient_influence(pt),
                expertise_areas={"patient_experience": 0.8},
            )
            self.nodes[pt.agent_id] = node

        # 2. 构建小世界网络 (Watts-Strogatz)
        patient_ids = [pt.agent_id for pt in patients]
        self._build_watts_strogatz(patient_ids, k=6, beta=0.3)

        # 3. 同地区加强连接
        self._add_regional_links(patients)

        # 4. 同疾病社区
        self._build_disease_communities(patients)

        # 5. 医生作为KOL连接
        if doctors:
            self._connect_doctors_as_kols(patients, doctors)

        # 6. 专家弱连接
        if expert_agents:
            self._connect_expert_weak_links(patients, expert_agents)

        # 7. 识别枢纽节点
        self._identify_hubs()

        total_edges = sum(len(v) for v in self.edges.values())
        print(f"   ✅ 网络构建完成: {len(self.nodes)}节点, {total_edges}条边, "
              f"{len(self.communities)}个社区")

        return {
            "num_nodes": len(self.nodes),
            "num_edges": total_edges,
            "num_communities": len(self.communities),
            "avg_degree": total_edges / len(self.nodes) if self.nodes else 0,
            "hub_count": sum(1 for n in self.nodes.values() if n.is_hub),
        }

    def _calc_patient_influence(self, patient) -> float:
        """计算患者影响力(社交中心度代理)"""
        score = 0.3

        # 经济水平影响社交影响力
        if hasattr(patient, 'economic_level'):
            econ = patient.economic_level.value if hasattr(patient.economic_level, 'value') else str(patient.economic_level)
            if "高" in econ:
                score += 0.25
            elif "中" in econ:
                score += 0.1

        # 信息来源决定社交活跃度
        if hasattr(patient, 'information_source'):
            src = patient.information_source.value if hasattr(patient.information_source, 'value') else str(patient.information_source)
            if "病友" in src:
                score += 0.2  # 病友社区用户影响力更大
            elif "网络" in src:
                score += 0.15

        # 依从性高的患者在社区中更有影响力
        if hasattr(patient, 'adherence_score'):
            score += patient.adherence_score * 0.15

        return min(score, 1.0)

    def _build_watts_strogatz(self, node_ids: List[str], k: int = 6, beta: float = 0.3):
        """Watts-Strogatz小世界网络"""
        n = len(node_ids)
        if n < k + 1:
            k = max(2, n - 1)

        # 创建规则环形网格
        for i in range(n):
            for j in range(1, k // 2 + 1):
                neighbor = node_ids[(i + j) % n]
                if neighbor != node_ids[i]:
                    self._add_edge(node_ids[i], neighbor, "peer", 0.5)

        # 以概率beta重连
        edges_to_check = list(self._get_all_edges())
        for src, dst in edges_to_check:
            if self._rng.random() < beta:
                # 移除旧连接
                self._remove_edge(src, dst)
                # 添加新随机连接
                new_target = self._rng.choice(node_ids)
                if new_target != src and not self._has_edge(src, new_target):
                    self._add_edge(src, new_target, "peer", 0.3 + self._rng.random() * 0.4)

    def _add_regional_links(self, patients: list):
        """同地区加强连接"""
        region_groups = defaultdict(list)
        for pt in patients:
            if hasattr(pt, 'region'):
                region_groups[pt.region].append(pt.agent_id)

        for region, pids in region_groups.items():
            # 同地区随机增加1-3条强连接
            for _ in range(min(len(pids) - 1, self._rng.randint(1, 3))):
                if len(pids) >= 2:
                    a, b = self._rng.sample(pids, 2)
                    trust = 0.6 + self._rng.random() * 0.3
                    self._add_edge(a, b, "community", trust)

    def _build_disease_communities(self, patients: list):
        """构建病友社区"""
        disease_groups = defaultdict(list)
        for pt in patients:
            disease = getattr(pt, 'disease_type', 'unknown')
            stage = getattr(pt, 'disease_stage', 'unknown')
            key = f"{disease}_{stage}"
            disease_groups[key].append(pt.agent_id)

        for community_name, members in disease_groups.items():
            self.communities[community_name] = set(members)
            # 社区内随机增加连接
            density = min(0.15, 5 / max(len(members), 1))
            for i in range(len(members)):
                for j in range(i + 1, len(members)):
                    if self._rng.random() < density:
                        trust = 0.5 + self._rng.random() * 0.4
                        self._add_edge(members[i], members[j], "peer", trust)

    def _connect_doctors_as_kols(self, patients: list, doctors: list):
        """医生作为KOL连接到患者"""
        # 每个医生连接其科室相关的患者
        for doc in doctors[:min(50, len(doctors))]:  # 限制50个医生节点
            doc_id = doc.agent_id
            self.nodes[doc_id] = NetworkNode(
                agent_id=doc_id,
                agent_type="doctor",
                influence_score=0.5 + (doc.academic_influence if hasattr(doc, 'academic_influence') else 0.3),
                expertise_areas={"clinical": 0.9},
                is_hub=True,
            )
            # 每个医生连接5-15个患者
            num_followers = self._rng.randint(5, 15)
            connected_patients = self._rng.sample(
                [pt.agent_id for pt in patients],
                min(num_followers, len(patients))
            )
            for pt_id in connected_patients:
                trust = 0.6 + self._rng.random() * 0.3
                self._add_edge(doc_id, pt_id, "kol_follower", trust)

    def _connect_expert_weak_links(self, patients: list, expert_agents: dict):
        """专家弱连接 - 信息源"""
        expert_ids = []
        for key, experts in expert_agents.items():
            if key in ["doctors", "patients", "payer"]:
                continue
            for exp in experts[:5]:  # 每类取5个
                expert_ids.append(exp.agent_id)
                self.nodes[exp.agent_id] = NetworkNode(
                    agent_id=exp.agent_id,
                    agent_type="expert",
                    influence_score=0.4,
                    expertise_areas={key: 0.9},
                )

        # 每个患者以10%概率连接一个专家
        for pt in patients:
            if expert_ids and self._rng.random() < 0.1:
                expert_id = self._rng.choice(expert_ids)
                self._add_edge(pt.agent_id, expert_id, "community", 0.3)

    def _identify_hubs(self):
        """识别枢纽节点(KOL)"""
        # 计算度数
        degree = defaultdict(int)
        for node_id, edges in self.edges.items():
            degree[node_id] = len(edges)

        if not degree:
            return

        # 度数前5%为枢纽
        sorted_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)
        hub_count = max(1, len(sorted_nodes) // 20)

        for node_id, _ in sorted_nodes[:hub_count]:
            if node_id in self.nodes:
                self.nodes[node_id].is_hub = True
                self.nodes[node_id].influence_score = min(
                    1.0, self.nodes[node_id].influence_score + 0.2
                )

    def get_neighbors(self, agent_id: str) -> List[Tuple[str, float]]:
        """获取邻居及其影响权重"""
        result = []
        for edge in self.edges.get(agent_id, []):
            neighbor_id = edge.target if edge.source == agent_id else edge.source
            weight = edge.influence_weight()
            result.append((neighbor_id, weight))
        return result

    def get_community_peers(self, agent_id: str) -> List[str]:
        """获取同社区的成员"""
        for comm_name, members in self.communities.items():
            if agent_id in members:
                return [m for m in members if m != agent_id]
        return []

    def get_influence_cascade(self, source_id: str, max_depth: int = 3) -> Dict[str, float]:
        """获取影响力级联(传播路径)"""
        visited = {source_id: 1.0}
        queue = [(source_id, 1.0, 0)]

        while queue:
            current, influence, depth = queue.pop(0)
            if depth >= max_depth:
                continue

            for neighbor_id, edge_weight in self.get_neighbors(current):
                if neighbor_id not in visited:
                    decayed = influence * edge_weight * 0.7  # 传播衰减
                    if decayed > 0.05:
                        visited[neighbor_id] = decayed
                        queue.append((neighbor_id, decayed, depth + 1))

        return visited

    def _add_edge(self, source: str, target: str, edge_type: str, trust: float):
        """添加双向边"""
        freq = 0.3 + self._rng.random() * 0.5
        edge1 = SocialEdge(source, target, trust, freq, edge_type)
        edge2 = SocialEdge(target, source, trust, freq, edge_type)
        self.edges[source].append(edge1)
        self.edges[target].append(edge2)
        if source in self.nodes:
            self.nodes[source].neighbors.append(target)
        if target in self.nodes:
            self.nodes[target].neighbors.append(source)

    def _remove_edge(self, source: str, target: str):
        """移除边"""
        self.edges[source] = [e for e in self.edges[source] if e.target != target]
        self.edges[target] = [e for e in self.edges[target] if e.target != source]

    def _has_edge(self, source: str, target: str) -> bool:
        return any(e.target == target for e in self.edges.get(source, []))

    def _get_all_edges(self) -> Set[Tuple[str, str]]:
        seen = set()
        for src, edges in self.edges.items():
            for e in edges:
                pair = tuple(sorted([src, e.target]))
                seen.add(pair)
        return seen

    def get_stats(self) -> dict:
        """网络统计"""
        degrees = [len(v) for v in self.edges.values()]
        return {
            "nodes": len(self.nodes),
            "edges": sum(degrees) // 2,
            "avg_degree": sum(degrees) / max(len(degrees), 1),
            "max_degree": max(degrees) if degrees else 0,
            "communities": len(self.communities),
            "hubs": sum(1 for n in self.nodes.values() if n.is_hub),
        }
