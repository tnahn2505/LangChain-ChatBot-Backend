"""
AI Service - Business logic for AI interactions using Google Gemini API
"""
from typing import Dict, Any
import asyncio
import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

class AIService:
    """Service for AI interactions using Google Gemini API"""
    
    @staticmethod
    async def process_message(content: str) -> Dict[str, Any]:
        """
        Process user message and generate AI response using Google Gemini API
        """
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                # Fallback to mock response if no API key
                await asyncio.sleep(0.5)
                ai_response = f"Tôi đã nhận được tin nhắn của bạn: '{content}'. Đây là phản hồi từ AI Assistant. (Mock mode - cần cấu hình GEMINI_API_KEY)"
                return {
                    "content": ai_response,
                    "model": "mock",
                    "usage": {
                        "prompt_tokens": len(content.split()),
                        "completion_tokens": len(ai_response.split()),
                        "total_tokens": len(content.split()) + len(ai_response.split())
                    },
                    "latency_ms": 500
                }
            
            # Call Google Gemini API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}:generateContent?key={api_key}",
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": f"Bạn là một AI Assistant thông minh và hữu ích. Hãy trả lời câu hỏi của người dùng một cách chính xác và thân thiện bằng tiếng Việt.\n\nNgười dùng: {content}"
                                    }
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 1000,
                            "topP": 0.8,
                            "topK": 10
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "candidates" in data and len(data["candidates"]) > 0:
                        ai_response = data["candidates"][0]["content"]["parts"][0]["text"]
                        usage_info = data.get("usageMetadata", {})
                        
                        return {
                            "content": ai_response,
                            "model": os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                            "usage": {
                                "prompt_tokens": usage_info.get("promptTokenCount", 0),
                                "completion_tokens": usage_info.get("candidatesTokenCount", 0),
                                "total_tokens": usage_info.get("totalTokenCount", 0)
                            },
                            "latency_ms": int(response.elapsed.total_seconds() * 1000)
                        }
                    else:
                        ai_response = "Xin lỗi, tôi không thể tạo phản hồi cho câu hỏi này."
                        return {
                            "content": ai_response,
                            "model": "error",
                            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                            "latency_ms": int(response.elapsed.total_seconds() * 1000)
                        }
                else:
                    # Fallback to mock response on API error
                    ai_response = f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn. Lỗi: {response.status_code}"
                    return {
                        "content": ai_response,
                        "model": "error",
                        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                        "latency_ms": int(response.elapsed.total_seconds() * 1000)
                    }
                    
        except Exception as e:
            # Fallback to mock response on any error
            ai_response = f"Xin lỗi, tôi gặp lỗi khi xử lý yêu cầu của bạn: {str(e)}"
            return {
                "content": ai_response,
                "model": "error",
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
                "latency_ms": 0
            }
    
    @staticmethod
    async def health_check() -> bool:
        """Check if AI service is available"""
        try:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key or api_key == "your_gemini_api_key_here":
                return False
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                    timeout=10.0
                )
                return response.status_code == 200
        except:
            return False
