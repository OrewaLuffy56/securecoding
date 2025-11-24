# SecureScan.ai - Comprehensive AI Coding Pattern Analyzer

## 🎯 Project Overview

SecureScan.ai is an advanced security analysis tool that uses Universal IR (Intermediate Representation) and taint analysis to detect vulnerabilities in Python code.

### Key Features
- **Universal IR Conversion**: Converts Python AST to a language-agnostic IR
- **Taint Analysis**: Tracks data flow from sources (user input) to dangerous sinks
- **Pattern Detection**: Identifies SQL injection, XSS, command injection, path traversal
- **Secrets Detection**: Finds hardcoded API keys, passwords, and credentials
- **Async Processing**: Uses Redis + RQ for background job processing

## 🏗️ Architecture

```
┌───────────────────┐
│  Frontend (React)  │
│  Port: 5173       │
└───────┬───────────┘
        │
        │ HTTP (CORS)
        │
┌───────┴───────────┐
│  Backend (FastAPI) │
│  Port: 8000       │
└───────┬───────────┘
        │
        ├───────> Supabase (Database)
        │
        └───────> Redis (Queue)
                   │
                   v
            RQ Worker (Analyzer)
```

## 🛠️ Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI**: Modern web framework
- **Supabase**: PostgreSQL database
- **Redis + RQ**: Background job processing
- **AST**: Python Abstract Syntax Tree parser

### Frontend
- **React 18** with TypeScript
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Axios**: HTTP client

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Supabase account

### 1. Set Up Supabase Database

Run this SQL in your Supabase SQL Editor:

```sql
CREATE TABLE scans (
    id BIGSERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    findings JSONB,
    total_findings INTEGER DEFAULT 0,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_scans_job_id ON scans(job_id);
CREATE INDEX idx_scans_status ON scans(status);
```

### 2. Start Backend with Docker

```bash
# Start all services (backend, worker, redis)
docker-compose up -d

# View logs
docker-compose logs -f backend
```

### 3. Start Frontend

```bash
cd frontend
yarn install
yarn dev
```

Frontend will be available at: **http://localhost:5173**

Backend API at: **http://localhost:8000**

## 📊 API Endpoints

### 1. Upload File
```http
POST /api/upload
Content-Type: multipart/form-data

Response:
{
  "job_id": "uuid",
  "status": "pending",
  "message": "File uploaded successfully"
}
```

### 2. Check Status
```http
GET /api/status/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "completed",
  "progress": 100,
  "total_findings": 5
}
```

### 3. Get Results
```http
GET /api/results/{job_id}

Response: [
  {
    "rule_id": "PY-SQL-INJECTION",
    "severity": "High",
    "cwe": ["CWE-89"],
    "location": {
      "file": "app.py",
      "line": 42
    },
    "suggestion": "Use parameterized queries...",
    "codeSnippet": "cursor.execute(...)"
  }
]
```

## 🔍 Security Checks Implemented

### Taint Analysis
- ✅ SQL Injection (CWE-89)
- ✅ XSS (CWE-79)
- ✅ Command Injection (CWE-78)
- ✅ Path Traversal (CWE-22)

### Pattern Detection
- ✅ Hardcoded API Keys
- ✅ Hardcoded Passwords
- ✅ AWS Credentials
- ✅ Private Keys
- ✅ JWT Tokens

## 📝 Frontend Integration Guide

### Using the API Client

Your v0.dev components should import from `src/lib/api.ts`:

```typescript
import { uploadFile, getScanStatus, getResults } from './lib/api';
import type { SecurityFinding } from './lib/api';

const handleUpload = async (file: File) => {
  const response = await uploadFile(file);
  const jobId = response.job_id;
  
  // Poll for status
  const interval = setInterval(async () => {
    const status = await getScanStatus(jobId);
    if (status.status === 'completed') {
      clearInterval(interval);
      const findings = await getResults(jobId);
      // Display findings
    }
  }, 2000);
};
```

## 🧪 Testing the Backend

### Test with cURL

```bash
# Upload a test file
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.py"

# Check status
curl http://localhost:8000/api/status/{job_id}

# Get results
curl http://localhost:8000/api/results/{job_id}
```

### Test Python File Example

Create `test.py`:
```python
import os
from flask import request

# This should trigger SQL injection warning
def vulnerable_query():
    user_input = request.args.get('id')
    query = f"SELECT * FROM users WHERE id = {user_input}"
    cursor.execute(query)

# This should trigger secrets detection
API_KEY = "sk_live_abcdef123456789012345678901234567890"
```

## 📚 Universal IR Structure

```python
class NodeType(Enum):
    PROGRAM = "PROGRAM"
    FUNCTION_DEF = "FUNCTION_DEF"
    CALL_EXPRESSION = "CALL_EXPRESSION"
    ASSIGN = "ASSIGN"
    VARIABLE = "VARIABLE"
    # ... more types

@dataclass
class IRNode:
    uid: str
    node_type: NodeType
    location: SourceLocation
    metadata: Dict[str, Any]
    is_tainted: bool
    children: List['IRNode']
```

## 🔧 Development Commands

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Worker (separate terminal)
python worker.py

# Frontend
cd frontend
yarn dev

# Docker
docker-compose up --build
docker-compose down
```

## 📝 Environment Variables

### Backend (.env)
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
REDIS_URL=redis://redis:6379/0
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🚦 Next Steps

1. ✅ Backend is complete and ready
2. ✅ Frontend scaffold is set up
3. 🔵 Create Supabase table (see SQL above)
4. 🔵 Paste your v0.dev components into `frontend/src/components/`
5. 🔵 Update `App.tsx` to use your components
6. 🔵 Test end-to-end workflow

## 🐛 Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
# Check if Supabase credentials are correct
```

### Redis connection failed
```bash
docker-compose up redis -d
# Ensure redis service is running
```

### Frontend can't connect to backend
- Check CORS settings in `main.py`
- Verify `VITE_API_URL` in frontend `.env`
- Ensure backend is running on port 8000

## 💬 Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Verify Supabase table exists
3. Test API with cURL first
4. Check browser console for frontend errors

---

**Built with ❤️ by the SecureScan.ai team**
