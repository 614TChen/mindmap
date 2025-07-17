from typing import List, Dict
from llama_index.core.llms import ChatMessage
import time

class MessageManager:
    def __init__(
        self, 
        system_prompt: str = "你是Eure，善于启发用户的灵感。",
        max_rounds: int = 10
    ):
        """
        初始化消息管理器
        
        Args:
            max_rounds: 最大对话轮数，默认10轮
        """
        self.system_prompt = system_prompt
        self.max_rounds = max_rounds
        self.conversations: Dict[str, List[ChatMessage]] = {}
        self.conversation_timestamps: Dict[str, float] = {}
    
    def get_or_create_conversation(self, session_id: str) -> List[ChatMessage]:
        """
        获取或创建会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话消息列表
        """
        if session_id not in self.conversations:
            self.conversations[session_id] = []
            self.conversation_timestamps[session_id] = time.time()
        return self.conversations[session_id]
    
    def add_message(self, session_id: str, role: str, content: str) -> None:
        """
        添加消息到会话
        
        Args:
            session_id: 会话ID
            role: 消息角色 ('user' 或 'assistant')
            content: 消息内容
        """
        conversation = self.get_or_create_conversation(session_id)
        message = ChatMessage(role=role, content=content)
        conversation.append(message)
        
        # 检查并限制对话轮数
        self._limit_conversation_rounds(session_id)
    
    def get_context_messages(self, session_id: str) -> List[ChatMessage]:
        """
        获取会话的上下文消息（包含系统消息）
        
        Args:
            session_id: 会话ID
            
        Returns:
            包含系统消息的完整上下文
        """
        conversation = self.get_or_create_conversation(session_id)
        
        # 系统消息
        system_message = ChatMessage(
            role="system",
            content=self.system_prompt
        )
        
        # 返回系统消息 + 对话历史
        return [system_message] + conversation
    
    def _limit_conversation_rounds(self, session_id: str) -> None:
        """
        限制对话轮数，保持最新的对话
        
        Args:
            session_id: 会话ID
        """
        conversation = self.conversations[session_id]
        
        # 计算当前轮数（每轮包含用户和助手各一条消息）
        current_rounds = len(conversation) // 2
        
        if current_rounds > self.max_rounds:
            # 保留最新的 max_rounds 轮对话
            keep_messages = self.max_rounds * 2
            self.conversations[session_id] = conversation[-keep_messages:]
    
    def clear_conversation(self, session_id: str) -> None:
        """
        清空指定会话
        
        Args:
            session_id: 会话ID
        """
        if session_id in self.conversations:
            self.conversations[session_id] = []
            self.conversation_timestamps[session_id] = time.time()
    
    def get_conversation_info(self, session_id: str) -> Dict:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话信息字典
        """
        conversation = self.get_or_create_conversation(session_id)
        current_rounds = len(conversation) // 2
        
        return {
            "session_id": session_id,
            "current_rounds": current_rounds,
            "max_rounds": self.max_rounds,
            "total_messages": len(conversation),
            "created_at": self.conversation_timestamps.get(session_id, 0)
        }
    
    def cleanup_old_conversations(self, max_age_hours: int = 24) -> None:
        """
        清理过期的会话
        
        Args:
            max_age_hours: 最大保留时间（小时）
        """
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        expired_sessions = []
        for session_id, timestamp in self.conversation_timestamps.items():
            if current_time - timestamp > max_age_seconds:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.conversations[session_id]
            del self.conversation_timestamps[session_id] 