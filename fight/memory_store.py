"""记忆存储模块 - 与agents_memory集成"""

import os
from typing import Any, Dict, List, Optional
from datetime import datetime

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    # 如果没有安装sqlalchemy，提供错误提示
    raise ImportError("请安装sqlalchemy: pip install sqlalchemy")


class MemoryStore:
    """记忆存储类 - 用于存储和检索辩论相关信息"""

    def __init__(self):
        """初始化记忆存储"""
        self.dsn = os.getenv('AGENTS_MEMORY_DSN')
        self.api_key = os.getenv('AGENTS_MEMORY_API_KEY')
        self.tenant = "fight_app"
        self.user_id = "default_user"

        if not self.dsn:
            raise ValueError("请设置AGENTS_MEMORY_DSN环境变量")

        if not self.api_key:
            raise ValueError("请设置AGENTS_MEMORY_API_KEY环境变量")

        try:
            # 创建数据库连接
            self.engine = create_engine(
                self.dsn,
                pool_pre_ping=True,
                pool_recycle=3600
            )

            # 测试连接
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            print("记忆存储连接成功")

        except SQLAlchemyError as e:
            raise ConnectionError(f"无法连接到数据库: {e}")

        # 当前辩论的命名空间和线程ID
        self.current_namespace = "debate"
        self.current_thread_id = None

    def start_debate_session(self, debate_id: str) -> bool:
        """开始新的辩论会话"""
        try:
            self.current_thread_id = debate_id

            # 记录辩论开始事件
            event_data = {
                "event_type": "debate_started",
                "timestamp": datetime.now().isoformat(),
                "debate_id": debate_id
            }

            return self._record_event(event_data)

        except Exception as e:
            print(f"开始辩论会话失败: {e}")
            return False

    def save_argument(self, argument_data: Dict[str, Any]) -> bool:
        """保存论点到记忆存储"""
        try:
            if not self.current_thread_id:
                print("没有活动的辩论会话")
                return False

            # 添加论点记录事件
            event_data = {
                "event_type": "argument_recorded",
                "timestamp": datetime.now().isoformat(),
                "argument": argument_data
            }

            return self._record_event(event_data)

        except Exception as e:
            print(f"保存论点失败: {e}")
            return False

    def save_evidence(self, evidence_data: Dict[str, Any]) -> bool:
        """保存证据到记忆存储"""
        try:
            if not self.current_thread_id:
                print("没有活动的辩论会话")
                return False

            # 添加证据记录事件
            event_data = {
                "event_type": "evidence_recorded",
                "timestamp": datetime.now().isoformat(),
                "evidence": evidence_data
            }

            return self._record_event(event_data)

        except Exception as e:
            print(f"保存证据失败: {e}")
            return False

    def get_debate_history(self, debate_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取辩论历史记录"""
        try:
            thread_id = debate_id or self.current_thread_id
            if not thread_id:
                return []

            query = """
                SELECT event_type, payload, created_at
                FROM agents_memory.investigation_events
                WHERE event_group_id = :thread_id
                ORDER BY created_at ASC
            """

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(query),
                    {"thread_id": thread_id}
                )

                history = []
                for row in result:
                    history.append({
                        "event_type": row[0],
                        "payload": row[1],
                        "created_at": row[2].isoformat() if row[2] else None
                    })

                return history

        except Exception as e:
            print(f"获取辩论历史失败: {e}")
            return []

    def get_key_arguments(self, debate_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取关键论点"""
        try:
            thread_id = debate_id or self.current_thread_id
            if not thread_id:
                return []

            query = """
                SELECT f.id, f.content, f.stance, f.importance
                FROM agents_memory.findings f
                WHERE f.investigation_id = :thread_id
                AND f.deleted_at IS NULL
                ORDER BY f.importance DESC, f.created_at DESC
                LIMIT 10
            """

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(query),
                    {"thread_id": thread_id}
                )

                arguments = []
                for row in result:
                    arguments.append({
                        "id": str(row[0]),
                        "content": row[1],
                        "stance": row[2],
                        "importance": row[3]
                    })

                return arguments

        except Exception as e:
            print(f"获取关键论点失败: {e}")
            return []

    def search_relevant_context(self, query: str, debate_id: Optional[str] = None) -> List[str]:
        """搜索相关上下文（用于AI回应时参考）"""
        try:
            thread_id = debate_id or self.current_thread_id
            if not thread_id:
                return []

            # 简单的文本搜索（可以升级为向量搜索）
            search_query = """
                SELECT content
                FROM agents_memory.findings
                WHERE investigation_id = :thread_id
                AND deleted_at IS NULL
                AND content ILIKE :query_pattern
                ORDER BY importance DESC
                LIMIT 5
            """

            with self.engine.connect() as conn:
                result = conn.execute(
                    text(search_query),
                    {
                        "thread_id": thread_id,
                        "query_pattern": f"%{query}%"
                    }
                )

                contexts = [row[0] for row in result if row[0]]
                return contexts

        except Exception as e:
            print(f"搜索相关上下文失败: {e}")
            return []

    def _record_event(self, event_data: Dict[str, Any]) -> bool:
        """记录事件到数据库"""
        try:
            insert_query = """
                INSERT INTO agents_memory.investigation_events
                (event_group_id, verb, payload, created_at)
                VALUES (:event_group_id, :verb, :payload, :created_at)
            """

            with self.engine.connect() as conn:
                conn.execute(
                    text(insert_query),
                    {
                        "event_group_id": self.current_thread_id,
                        "verb": event_data["event_type"],
                        "payload": event_data,
                        "created_at": datetime.now()
                    }
                )
                conn.commit()

            return True

        except Exception as e:
            print(f"记录事件失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if hasattr(self, 'engine'):
            self.engine.dispose()
            print("记忆存储连接已关闭")