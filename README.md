# ChatBot Backend API

Backend API cho ứng dụng ChatBot sử dụng FastAPI, MongoDB và Google Gemini AI.

## ✨ Tính năng

- 🤖 **Google Gemini AI Integration** - Sử dụng Gemini 2.0 Flash model
- 🗄️ **MongoDB Database** - Lưu trữ threads và messages
- 🚀 **FastAPI** - API framework hiện đại và nhanh
- 🔄 **Real-time Chat** - Xử lý tin nhắn real-time
- 🌐 **CORS Support** - Hỗ trợ frontend cross-origin

## 🏗️ Cấu trúc dự án

```
BE/
├── routes/
│   ├── health.py       # GET /health
│   ├── threads.py      # POST /threads, GET /threads
│   └── messages.py     # POST /threads/{id}/messages
├── models/             # Database models
│   ├── thread.py       # Thread model
│   └── message.py      # Message model
├── services/           # Business logic
│   ├── ai_service.py   # AI processing
│   ├── thread_service.py # Thread operations
│   └── message_service.py # Message operations
├── main.py            # FastAPI app
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
└── README.md          # Documentation
```

## Frontend-Backend Architecture

### Frontend sử dụng:
- **localStorage** cho thread và message management
- **Backend API** chỉ cho AI responses
- **Hybrid approach** - local storage + AI backend

### Backend cung cấp:
- **Health check** - `/health`
- **AI message processing** - `/threads/{id}/messages`
- **Thread creation** - `/threads` (optional)

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình environment
```bash
# Tạo file .env từ template
cp .env.example .env

# Hoặc tạo file .env mới với nội dung:
# MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=AppName
# MONGODB_DB_NAME=chatbotdb
# GEMINI_API_KEY=your_gemini_api_key_here
# GEMINI_MODEL=gemini-2.0-flash
```

### 3. Chạy ứng dụng
```bash
# Development mode
python main.py

# Hoặc với uvicorn trực tiếp
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 4. Kiểm tra hoạt động
```bash
# Health check
curl http://127.0.0.1:8000/health

# API Documentation
# Mở trình duyệt: http://127.0.0.1:8000/docs
```

## 📡 API Endpoints

### 🔥 Core Endpoints (Frontend sử dụng)
- `GET /health` - Health check (frontend api.health())
- `POST /threads` - Create thread (frontend api.createThread())
- `POST /threads/{id}/messages` - Send message to Gemini AI (frontend api.sendMessage())

### 📋 Additional Endpoints
- `GET /threads` - Get all threads
- `GET /threads/{id}` - Get specific thread
- `PUT /threads/{id}` - Update thread
- `DELETE /threads/{id}` - Delete thread
- `GET /threads/{id}/messages` - Get messages

### 🤖 Gemini AI Integration
- **Model**: `gemini-2.0-flash`
- **Language**: Hỗ trợ tiếng Việt và tiếng Anh
- **Response Format**: JSON với usage statistics
- **Timeout**: 30 giây

## Frontend Integration

### API Response Format (Matching Frontend Types)
```typescript
// Health Response
{ ok: boolean }

// Thread Creation
{ ok: boolean, message: string }

// Message Response
{
  thread_id: string,
  user_message_id: string,
  assistant_message_id: string,
  assistant: {
    content: string,
    model?: string,
    usage?: any
  }
}
```

### Frontend API Client
- Sử dụng `api.health()` để check backend
- Sử dụng `api.createThread()` để tạo thread
- Sử dụng `api.sendMessage()` để gửi message đến AI
- Sử dụng localStorage cho thread/message management

## CORS Configuration
- Cho phép tất cả origins (development)
- Cấu hình trong production qua environment variables

## 🔧 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.net/?appName=App` |
| `MONGODB_DB_NAME` | Database name | `chatbotdb` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.0-flash` |
| `HOST` | Server host | `127.0.0.1` |
| `PORT` | Server port | `8000` |
| `RELOAD` | Auto-reload in development | `true` |

## 🛠️ Development

### Database Setup
```bash
# MongoDB Atlas (Recommended)
# 1. Tạo cluster tại https://cloud.mongodb.com
# 2. Lấy connection string
# 3. Cập nhật MONGODB_URI trong .env

# Local MongoDB
# 1. Cài đặt MongoDB locally
# 2. MONGODB_URI=mongodb://localhost:27017
```

### Gemini API Setup
```bash
# 1. Truy cập https://makersuite.google.com/app/apikey
# 2. Tạo API key mới
# 3. Cập nhật GEMINI_API_KEY trong .env
```

## 🚨 Error Handling
- Global exception handler
- HTTP status codes chuẩn
- Error response format nhất quán
- Retry mechanism trong frontend
- Fallback responses khi AI service lỗi

## 📝 Logs
- Server logs với timestamp
- API request/response logging
- Error tracking và debugging