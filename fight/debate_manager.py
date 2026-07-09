"""辩论管理器模块 - 核心辩论逻辑"""

import os
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from anthropic import Anthropic
except ImportError:
    raise ImportError("请安装anthropic: pip install anthropic")

from fight.memory_store import MemoryStore


class DebateManager:
    """辩论管理器 - 管理辩论状态和流程"""

    def __init__(self, memory_store: MemoryStore):
        """初始化辩论管理器"""
        self.memory_store = memory_store
        self.client = None

        # 辩论状态
        self.topic: Optional[str] = None
        self.user_position: Optional[str] = None
        self.ai_position: Optional[str] = None
        self.round = 0
        self.arguments: List[Dict[str, Any]] = []
        self.is_debate_active = False
        self.debate_id: Optional[str] = None

        # 初始化AI客户端
        self._init_ai_client()

    def _init_ai_client(self):
        """初始化Anthropic AI客户端"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("请设置ANTHROPIC_API_KEY环境变量")

        self.client = Anthropic(api_key=api_key)

    def start_debate(self, topic: str, user_position: str) -> bool:
        """开始新的辩论"""
        try:
            self.topic = topic
            self.user_position = user_position
            self.round = 1
            self.arguments = []
            self.is_debate_active = True
            self.debate_id = str(uuid.uuid4())

            # 生成AI的初始立场
            self.ai_position = self._generate_ai_position(topic, user_position)

            # 开始记忆存储会话
            self.memory_store.start_debate_session(self.debate_id)

            # 保存初始立场
            self._save_initial_arguments()

            return True

        except Exception as e:
            print(f"开始辩论失败: {e}")
            return False

    def _generate_ai_position(self, topic: str, user_position: str) -> str:
        """生成AI的初始对立立场"""
        try:
            prompt = f"""用户正在考虑以下决策主题：
主题: {topic}
用户的初步立场: {user_position}

作为辩论对手，请提供一个简洁的对立立场（1-2句话）。
这个立场应该：
1. 与用户立场相反或提出重要质疑
2. 基于合理的考虑和担忧
3. 有助于深入讨论这个决策

直接陈述对立立场，不要额外解释："""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text.strip()

        except Exception as e:
            print(f"生成AI立场失败: {e}")
            return "我对此有不同的担忧，让我们深入讨论。"

    def _save_initial_arguments(self):
        """保存初始论点到记忆存储"""
        try:
            # 保存用户立场
            user_arg = {
                "id": str(uuid.uuid4()),
                "speaker": "user",
                "content": self.user_position,
                "round": 0,
                "stance": "pro",
                "timestamp": datetime.now().isoformat()
            }
            self.memory_store.save_argument(user_arg)
            self.arguments.append(user_arg)

            # 保存AI立场
            ai_arg = {
                "id": str(uuid.uuid4()),
                "speaker": "ai",
                "content": self.ai_position,
                "round": 0,
                "stance": "con",
                "timestamp": datetime.now().isoformat()
            }
            self.memory_store.save_argument(ai_arg)
            self.arguments.append(ai_arg)

        except Exception as e:
            print(f"保存初始论点失败: {e}")

    def process_user_argument(self, user_argument: str) -> str:
        """处理用户论点并生成AI回应"""
        try:
            # 保存用户论点
            user_arg = {
                "id": str(uuid.uuid4()),
                "speaker": "user",
                "content": user_argument,
                "round": self.round,
                "stance": "pro",
                "timestamp": datetime.now().isoformat()
            }
            self.memory_store.save_argument(user_arg)
            self.arguments.append(user_arg)

            # 获取相关上下文
            context = self._get_debate_context()

            # 生成AI回应
            ai_response = self._generate_ai_response(user_argument, context)

            # 保存AI论点
            ai_arg = {
                "id": str(uuid.uuid4()),
                "speaker": "ai",
                "content": ai_response,
                "round": self.round,
                "stance": "con",
                "timestamp": datetime.now().isoformat()
            }
            self.memory_store.save_argument(ai_arg)
            self.arguments.append(ai_arg)

            return ai_response

        except Exception as e:
            print(f"处理用户论点失败: {e}")
            return "抱歉，我在处理你的论点时遇到了问题。"

    def _get_debate_context(self) -> str:
        """获取辩论上下文用于AI生成回应"""
        try:
            recent_args = self.arguments[-4:] if len(self.arguments) > 4 else self.arguments

            context_parts = []
            for arg in recent_args:
                speaker = "你" if arg["speaker"] == "user" else "我"
                context_parts.append(f"{speaker}（第{arg['round']}轮）: {arg['content']}")

            return "\n".join(context_parts)

        except Exception as e:
            print(f"获取上下文失败: {e}")
            return ""

    def _generate_ai_response(self, user_argument: str, context: str) -> str:
        """生成AI的回应"""
        try:
            prompt = f"""你正在参与一场关于决策的辩论。

辩论主题: {self.topic}
你的立场: {self.ai_position}

之前的辩论内容：
{context}

用户的新论点（第{self.round}轮）:
{user_argument}

请生成你的回应。回应应该：
1. 直接回应用户的论点
2. 提出有理有据的反驳或质疑
3. 保持辩论的建设性
4. 长度控制在2-3句话
5. 不要重复已经说过的内容

你的回应："""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text.strip()

        except Exception as e:
            print(f"生成AI回应失败: {e}")
            return "这个观点很有趣，值得我们进一步探讨。"

    def next_round(self):
        """进入下一轮辩论"""
        self.round += 1

    def end_debate(self):
        """结束辩论"""
        self.is_debate_active = False

    def is_active(self) -> bool:
        """检查辩论是否活跃"""
        return self.is_debate_active

    def get_summary(self) -> Dict[str, Any]:
        """获取辩论摘要"""
        return {
            "topic": self.topic or "无主题",
            "round": self.round,
            "argument_count": len(self.arguments),
            "user_position": self.user_position or "无",
            "ai_position": self.ai_position or "无",
            "key_arguments": self._extract_key_arguments()
        }

    def _extract_key_arguments(self) -> List[str]:
        """提取关键论点"""
        try:
            # 获取记忆存储中的关键论点
            key_args = self.memory_store.get_key_arguments(self.debate_id)

            if key_args:
                return [arg["content"] for arg in key_args[:5]]

            # 如果没有，返回最近的论点
            return [arg["content"] for arg in self.arguments[-3:]]

        except Exception as e:
            print(f"提取关键论点失败: {e}")
            return []

    def generate_decision(self) -> Dict[str, Any]:
        """生成最终决策建议"""
        try:
            # 获取完整的辩论历史
            debate_history = self.memory_store.get_debate_history(self.debate_id)

            context = f"""
辩论主题: {self.topic}
用户初始立场: {self.user_position}
AI初始立场: {self.ai_position}
辩论轮次: {self.round}
总论点数: {len(self.arguments)}

辩论摘要:
{self._get_debate_context()}

请基于以上辩论内容，生成一个平衡的决策建议。包括：
1. 明确的建议（支持/反对/修改方案）
2. 置信度评估（0-100%）
3. 推理过程（2-3句话）
4. 主要风险（2-3点）

请以JSON格式回复，包含字段: recommendation, confidence, reasoning, risks
"""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=600,
                temperature=0.3,
                messages=[{"role": "user", "content": context}]
            )

            response_text = message.content[0].text.strip()

            # 尝试解析JSON响应
            try:
                import json
                decision_data = json.loads(response_text)

                return {
                    "recommendation": decision_data.get("recommendation", "基于辩论，建议谨慎推进此决策。"),
                    "confidence": decision_data.get("confidence", 75),
                    "reasoning": decision_data.get("reasoning", "辩论显示此议题需要更多考虑。"),
                    "risks": decision_data.get("risks", ["需要进一步调研潜在风险"])
                }

            except json.JSONDecodeError:
                # 如果JSON解析失败，返回默认结构
                return {
                    "recommendation": "基于辩论内容，建议在充分准备后推进此决策。",
                    "confidence": 70,
                    "reasoning": "辩论中提出了多个重要观点，建议综合考虑。",
                    "risks": ["需要评估实施难度", "考虑潜在负面影响"]
                }

        except Exception as e:
            print(f"生成决策失败: {e}")
            return {
                "recommendation": "由于技术问题无法生成具体建议，建议基于辩论内容自行决策。",
                "confidence": 50,
                "reasoning": "辩论过程已记录，建议回顾关键论点后做出决定。",
                "risks": ["建议重新评估", "考虑寻求专业意见"]
            }