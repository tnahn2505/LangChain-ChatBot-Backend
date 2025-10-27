"""
MongoDB adapter for LangChain memory
Implements BaseChatMessageHistory for RunnableWithMessageHistory
"""
from typing import List, Optional
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from ..db.mongo import get_db
from ..core.config import get_settings

class MongoChatMessageHistory(BaseChatMessageHistory):
    """MongoDB implementation of LangChain chat message history"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.settings = get_settings()
        self._messages: Optional[List[BaseMessage]] = None
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Get messages from MongoDB"""
        if self._messages is None:
            self._load_messages()
        return self._messages or []
    
    def _load_messages(self) -> None:
        """Load messages from MongoDB synchronously"""
        try:
            # Get database
            db = get_db()
            
            # Query messages for this session (thread_id) - synchronous for now
            cursor = db.messages.find(
                {"threadId": self.session_id}
            ).sort("createdAt", 1)  # Chronological order
            
            messages = []
            for doc in cursor:
                role = doc.get("role", "user")
                content = doc.get("content", "")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
                elif role == "system":
                    messages.append(SystemMessage(content=content))
            
            self._messages = messages
            
        except Exception as e:
            print(f"Error loading messages: {e}")
            self._messages = []
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to history"""
        if self._messages is None:
            self._messages = []
        self._messages.append(message)
    
    def clear(self) -> None:
        """Clear all messages"""
        self._messages = []
    
    def __str__(self) -> str:
        """String representation"""
        return f"MongoChatMessageHistory(session_id={self.session_id}, messages={len(self.messages)})"

def get_session_history(session_id: str) -> MongoChatMessageHistory:
    """Get session history for LangChain memory"""
    return MongoChatMessageHistory(session_id)
