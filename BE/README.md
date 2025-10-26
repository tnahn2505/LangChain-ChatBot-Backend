# ChatBot Backend API

## Cấu trúc dự án (Following Architecture Document)

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

## Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Cấu hình environment
```bash
cp .env.example .env
# Chỉnh sửa .env theo môi trường của bạn
```

### 3. Chạy ứng dụng
```bash
# Development
python main.py

# Hoặc với uvicorn
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## API Endpoints (Matching Frontend)

### Core Endpoints (Frontend sử dụng)
- `GET /health` - Health check (frontend api.health())
- `POST /threads` - Create thread (frontend api.createThread())
- `POST /threads/{id}/messages` - Send message to AI (frontend api.sendMessage())

### Additional Endpoints (Future use)
- `GET /threads` - Get all threads
- `GET /threads/{id}` - Get specific thread
- `PUT /threads/{id}` - Update thread
- `DELETE /threads/{id}` - Delete thread
- `GET /threads/{id}/messages` - Get messages

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

## Error Handling
- Global exception handler
- HTTP status codes chuẩn
- Error response format nhất quán
- Retry mechanism trong frontend