"""
AI Service with LangChain integration
Supports Gemini, OpenAI, and mock fallback with proper memory management
"""
import asyncio
import time
from typing import Dict, Any, List
from ..core.config import get_settings
from ..models.schemas import AIResponse, AIUsage

# Try to import LangChain modules, fallback to mock if not available
try:
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("Warning: LangChain packages not installed, using mock mode")

class AIService:
    """AI service with LangChain integration and proper memory management"""
    
    def __init__(self):
        self.settings = get_settings()
        self._llm: BaseChatModel = None
        self._chain = None
        self._initialize_model()
    
    def _initialize_model(self) -> None:
        """Initialize the AI model and chain based on configuration"""
        if not LANGCHAIN_AVAILABLE:
            print("Warning: LangChain not available, using mock mode")
            self._llm = None
            return
            
        try:
            # Initialize LLM based on provider
            if self.settings.ai_provider.lower() == "gemini":
                if not self.settings.gemini_api_key:
                    print("Warning: GEMINI_API_KEY not found, using mock mode")
                    self._llm = None
                    return
                
                self._llm = ChatGoogleGenerativeAI(
                    model=self.settings.gemini_model,
                    google_api_key=self.settings.gemini_api_key,
                    temperature=0.7,
                    max_output_tokens=1000,
                )
                print(f"Success: Initialized Gemini model: {self.settings.gemini_model}")
                
            elif self.settings.ai_provider.lower() == "openai":
                if not self.settings.openai_api_key:
                    print("Warning: OPENAI_API_KEY not found, using mock mode")
                    self._llm = None
                    return
                
                self._llm = ChatOpenAI(
                    model=self.settings.openai_model,
                    api_key=self.settings.openai_api_key,
                    temperature=0.7,
                    max_tokens=1000,
                )
                print(f"Success: Initialized OpenAI model: {self.settings.openai_model}")
                
            else:
                print("Warning: Unknown AI provider, using mock mode")
                self._llm = None
                return
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.settings.system_prompt),
                ("placeholder", "{history}"),
                ("human", "{input}")
            ])
            
            # Create chain with memory
            from ..services.memory_adapter import get_session_history
            self._chain = RunnableWithMessageHistory(
                prompt | self._llm,
                get_session_history,
                input_messages_key="input",
                history_messages_key="history",
            )
                
        except Exception as e:
            print(f"Error: Failed to initialize AI model: {e}")
            self._llm = None
    
    async def process_message(
        self, 
        content: str, 
        thread_id: str,
        history: List[Dict[str, str]] = None
    ) -> AIResponse:
        """Process user message with proper LangChain memory"""
        start_time = time.time()
        
        try:
            if not self._llm or not self._chain:
                return await self._mock_response(content, start_time)
            
            # Use LangChain chain with memory
            response = await self._chain.ainvoke(
                {"input": content},
                config={"configurable": {"session_id": thread_id}}
            )
            
            # Extract content and usage information
            ai_content = response.content if hasattr(response, 'content') else str(response)
            usage = self._extract_usage(response)
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                content=ai_content,
                model=self._get_model_name(),
                usage=usage,
                latency_ms=latency_ms
            )
            
        except Exception as e:
            print(f"Error: AI processing error: {e}")
            return await self._mock_response(content, start_time, error=str(e))
    
    def _extract_usage(self, response) -> AIUsage:
        """Extract usage information from response"""
        try:
            # Try to get usage from response metadata
            if hasattr(response, 'response_metadata') and response.response_metadata:
                metadata = response.response_metadata
                return AIUsage(
                    prompt_tokens=metadata.get('prompt_tokens', 0),
                    completion_tokens=metadata.get('completion_tokens', 0),
                    total_tokens=metadata.get('total_tokens', 0)
                )
        except Exception:
            pass
        
        # Fallback: estimate tokens
        content = response.content if hasattr(response, 'content') else str(response)
        estimated_tokens = len(content.split())
        
        return AIUsage(
            prompt_tokens=estimated_tokens,
            completion_tokens=estimated_tokens,
            total_tokens=estimated_tokens * 2
        )
    
    def _get_model_name(self) -> str:
        """Get the current model name"""
        if self.settings.ai_provider.lower() == "gemini":
            return self.settings.gemini_model
        elif self.settings.ai_provider.lower() == "openai":
            return self.settings.openai_model
        return "mock"
    
    async def _mock_response(
        self, 
        content: str, 
        start_time: float, 
        error: str = None
    ) -> AIResponse:
        """Generate mock response when AI service is not available"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        if error:
            ai_content = f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn: {error}. (Mock mode - cần cấu hình API key)"
        else:
            ai_content = f"Tôi đã nhận được tin nhắn của bạn: '{content}'. Đây là phản hồi từ AI Assistant. (Mock mode - cần cấu hình API key)"
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        return AIResponse(
            content=ai_content,
            model="mock",
            usage=AIUsage(
                prompt_tokens=len(content.split()),
                completion_tokens=len(ai_content.split()),
                total_tokens=len(content.split()) + len(ai_content.split())
            ),
            latency_ms=latency_ms
        )
