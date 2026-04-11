"""
PharmaSim - Second Me 集成模块
实现 A2A (Agent-to-Agent) 协作协议
允许用户的 Second Me 数字分身参与药品模拟决策
"""

import json
import httpx
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


# Second Me API 基础配置
SECONDME_API_BASE = "https://api.mindverse.com/gate/lab"
SECONDME_OAUTH_AUTHORIZE = "https://go.second.me/oauth/authorize"
SECONDME_DEVELOPER_PORTAL = "https://develop.second.me/skill"


class A2AMessageType(Enum):
    DISCOVERY = "discovery"         # Agent发现
    TASK = "task"                   # 任务分配
    MESSAGE = "message"             # 消息传递
    STATUS = "status"               # 状态查询
    COLLABORATION = "collaboration" # 协作请求


@dataclass
class A2AMessage:
    """A2A协议消息"""
    message_type: A2AMessageType
    sender_id: str
    receiver_id: str
    content: dict
    timestamp: str = ""
    correlation_id: str = ""
    
    def to_dict(self) -> dict:
        return {
            "type": self.message_type.value,
            "sender": self.sender_id,
            "receiver": self.receiver_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
        }


@dataclass
class SecondMeIdentity:
    """Second Me 用户身份"""
    sm_id: str = ""
    sm_name: str = ""
    sm_email: str = ""
    sm_avatar: str = ""
    
    @classmethod
    def from_url_params(cls, params: dict) -> "SecondMeIdentity":
        return cls(
            sm_id=params.get("sm_id", ""),
            sm_name=params.get("sm_name", ""),
            sm_email=params.get("sm_email", ""),
            sm_avatar=params.get("sm_avatar", ""),
        )


@dataclass
class ShadeProfile:
    """Second Me 数字分身 (Shade)"""
    shade_id: str
    name: str
    description: str
    personality: dict = field(default_factory=dict)
    memory_context: str = ""
    skills: List[str] = field(default_factory=list)


class A2AProtocol:
    """A2A 协议实现"""
    
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.known_agents: Dict[str, dict] = {}
        self.message_queue: List[A2AMessage] = []
    
    def register_discovery_endpoint(self) -> dict:
        """
        返回 Agent 发现信息
        供其他 A2A Agent 查询本 Agent 的能力
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": "1.0.0",
            "capabilities": [
                {
                    "name": "drug_launch_simulation",
                    "description": "药品上市表现模拟预测",
                    "input_schema": {
                        "drug": "药品属性对象",
                        "config": "模拟配置对象"
                    },
                    "output_schema": {
                        "monthly_snapshots": "月度预测数据",
                        "summary": "模拟汇总报告"
                    }
                },
                {
                    "name": "pricing_strategy_analysis",
                    "description": "定价策略分析",
                    "input_schema": {
                        "drug": "药品属性",
                        "pricing_options": "定价方案列表"
                    }
                },
                {
                    "name": "competitor_impact_simulation",
                    "description": "竞品冲击模拟",
                    "input_schema": {
                        "current_drug": "当前药品",
                        "competitor_action": "竞品行为"
                    }
                }
            ],
            "endpoints": {
                "message": "/api/a2a/message",
                "task": "/api/a2a/task",
                "status": "/api/a2a/status",
            }
        }
    
    def send_message(self, receiver_id: str, content: dict, 
                      msg_type: A2AMessageType = A2AMessageType.MESSAGE) -> A2AMessage:
        """发送 A2A 消息"""
        import uuid
        from datetime import datetime
        
        msg = A2AMessage(
            message_type=msg_type,
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            content=content,
            timestamp=datetime.now().isoformat(),
            correlation_id=uuid.uuid4().hex[:12],
        )
        self.message_queue.append(msg)
        return msg
    
    def handle_message(self, message: dict) -> dict:
        """处理收到的 A2A 消息"""
        msg_type = message.get("type", "message")
        
        if msg_type == "discovery":
            return self.register_discovery_endpoint()
        elif msg_type == "task":
            return self._handle_task(message.get("content", {}))
        elif msg_type == "collaboration":
            return self._handle_collaboration(message.get("content", {}))
        elif msg_type == "status":
            return {"status": "active", "agent_id": self.agent_id}
        else:
            return {"error": f"Unknown message type: {msg_type}"}
    
    def _handle_task(self, task_content: dict) -> dict:
        """处理任务请求"""
        task_type = task_content.get("task_type", "")
        
        if task_type == "simulate_drug_launch":
            return {
                "accepted": True,
                "task_id": task_content.get("task_id", ""),
                "message": "已接受药品上市模拟任务",
                "estimated_time": "5-30分钟"
            }
        elif task_type == "evaluate_pricing":
            return {
                "accepted": True,
                "message": "已接受定价策略评估任务"
            }
        else:
            return {"accepted": False, "reason": f"不支持的任务类型: {task_type}"}
    
    def _handle_collaboration(self, collab_content: dict) -> dict:
        """处理协作请求"""
        return {
            "accepted": True,
            "collaboration_id": collab_content.get("session_id", ""),
            "available_agents": list(self.known_agents.keys()),
            "message": "协作模式已就绪"
        }


class SecondMeIntegration:
    """Second Me 集成层"""
    
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret
        self.a2a = A2AProtocol("pharmsim-main", "PharmaSim")
    
    def get_oauth_url(self, redirect_uri: str, state: str = "") -> str:
        """生成 Second Me OAuth 授权 URL"""
        import urllib.parse
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": "profile email shades:read",
            "state": state,
        }
        return f"{SECONDME_OAUTH_AUTHORIZE}?{urllib.parse.urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> dict:
        """用授权码换取访问令牌"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{SECONDME_API_BASE}/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                }
            )
            return response.json()
    
    async def get_user_shades(self, access_token: str) -> List[dict]:
        """获取用户的数字分身列表"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SECONDME_API_BASE}/v1/shades",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            return response.json().get("shades", [])
    
    def create_pharma_shade(self, shade_data: dict) -> ShadeProfile:
        """
        创建药品行业专用的数字分身
        
        从用户的 Second Me 分身中提取相关特征，
        映射为 PharmaSim 模拟所需的 Agent 属性
        """
        return ShadeProfile(
            shade_id=shade_data.get("id", ""),
            name=shade_data.get("name", "药品顾问分身"),
            description=shade_data.get("description", ""),
            personality=shade_data.get("personality", {}),
            memory_context=shade_data.get("context", ""),
            skills=["drug_evaluation", "market_analysis", "clinical_insight"],
        )
    
    def integrate_shade_into_simulation(self, shade: ShadeProfile, 
                                          simulation_context: dict) -> dict:
        """
        将用户分身集成到模拟中
        
        分身可以扮演以下角色：
        - 药企决策者: 参与定价和上市策略决策
        - 临床专家: 提供疾病领域见解
        - 投资人: 评估药品商业价值
        """
        return {
            "shade_id": shade.shade_id,
            "role": "consultant",
            "integration_point": "strategy_session",
            "context": {
                "shade_name": shade.name,
                "shade_skills": shade.skills,
                "simulation_drug": simulation_context.get("drug_name"),
                "collaboration_mode": "human_agent_plus_shade",
            }
        }
    
    def generate_a2a_manifest(self) -> dict:
        """生成 A2A 协议清单 (供外部 Agent 发现)"""
        return self.a2a.register_discovery_endpoint()
