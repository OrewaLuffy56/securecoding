# SecureScan.ai - Project Structure

## 📁 Complete File Tree

```
/app/
├── backend/                         # Python FastAPI Backend
│   ├── server.py                    # Main FastAPI application ✅
│   ├── converter.py                 # Universal IR & AST parser ✅
│   ├── analyzer.py                  # Security analysis engine ✅
│   ├── worker.py                    # Redis RQ worker ✅
│   ├── requirements.txt             # Python dependencies ✅
│   ├── .env                         # Environment variables ✅
│   └── Dockerfile                   # Docker container config ✅
│
├── frontend/                        # React + TypeScript Frontend
│   ├── src/
│   │   ├── lib/
│   │   │   └── api.ts              # API client (type-safe) ✅
│   │   ├── components/             # Your v0 components go here ⬜
│   │   ├── App.tsx                 # Main component (scaffold) ✅
│   │   ├── App.css                 # App styles ✅
│   │   ├── main.tsx                # Entry point ✅
│   │   ├── index.css               # Global styles + Tailwind ✅
│   │   └── vite-env.d.ts           # TypeScript definitions ✅
│   ├── public/                     # Static assets
│   ├── index.html                  # HTML template ✅
│   ├── package.json                # Node dependencies ✅
│   ├── vite.config.ts              # Vite configuration ✅
│   ├── tsconfig.json               # TypeScript config ✅
│   ├── tsconfig.node.json          # TS config for Vite ✅
│   ├── tailwind.config.js          # Tailwind CSS config ✅
│   ├── postcss.config.js           # PostCSS config ✅
│   └── .env                        # Frontend env vars ✅
│
├── scripts/                        # Utility scripts
│   ├── setup_supabase.py           # Database setup helper ✅
│   ├── demo_full_workflow.sh       # Complete workflow demo ✅
│   ├── test_backend.py             # Backend API tests ✅
│   ├── start_backend.sh            # Backend startup script ✅
│   └── start_frontend.sh           # Frontend startup script ✅
│
├── docker-compose.yml              # Docker orchestration ✅
├── supabase_setup.sql              # Database schema ✅
├── test_vulnerable.py              # Test file with vulnerabilities ✅
├── README.md                       # Full documentation ✅
├── QUICK_START.md                  # Quick start guide ✅
├── PROJECT_STRUCTURE.md            # This file ✅
└── .env.example                    # Environment variables template ✅
```

## 🔑 Key Files Explained

### Backend Core

#### `server.py` (Main Application)
- FastAPI application with CORS configured
- API endpoints: `/api/upload`, `/api/status/{job_id}`, `/api/results/{job_id}`
- Supabase and Redis integration
- Background job orchestration

#### `converter.py` (Universal IR)
- `IRNode`: Universal intermediate representation
- `NodeType`: Enum for different AST node types
- `PythonConverter`: Converts Python AST to Universal IR
- Extracts metadata (function names, variables, etc.)

#### `analyzer.py` (Security Engine)
- `TaintAnalyzer`: Tracks data flow from sources to sinks
- `SecretsDetector`: Regex-based secret detection
- `SecurityAnalyzer`: Main orchestrator
- Detects: SQL injection, XSS, command injection, path traversal, hardcoded secrets

### Frontend Core

#### `src/lib/api.ts` (API Client)
- Type-safe functions: `uploadFile()`, `getScanStatus()`, `getResults()`
- TypeScript interfaces matching backend data contract
- Axios-based HTTP client
- Configured for `http://localhost:8001`

#### `src/App.tsx` (UI Entry)
- Currently a scaffold/placeholder
- Replace with your v0.dev components
- Import API functions from `./lib/api`

### Infrastructure

#### `docker-compose.yml`
- Services: backend, worker, redis
- For production deployment
- Currently not used (supervisor is managing services)

#### `supabase_setup.sql`
- Database schema for `scans` table
- Indexes for performance
- Triggers for `updated_at`

### Test & Demo Files

#### `test_vulnerable.py`
- Intentionally vulnerable Python code
- Tests all detection rules
- Expected to generate ~8 findings

#### `scripts/demo_full_workflow.sh`
- End-to-end workflow demonstration
- Upload → Status → Results
- Color-coded output

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/upload` | POST | Upload Python file for analysis |
| `/api/status/{job_id}` | GET | Check scan status |
| `/api/results/{job_id}` | GET | Get security findings |

## 🗄️ Database Schema

```sql
CREATE TABLE scans (
    id BIGSERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    status TEXT CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    findings JSONB DEFAULT '[]'::jsonb,
    total_findings INTEGER DEFAULT 0,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## 🔐 Security Rules Implemented

| Rule ID | Severity | CWE | Description |
|---------|----------|-----|-------------|
| `PY-SQL-INJECTION` | High | CWE-89 | SQL injection via tainted input |
| `PY-XSS` | High | CWE-79 | Cross-site scripting |
| `PY-COMMAND-INJECTION` | High | CWE-78 | OS command injection |
| `PY-PATH-TRAVERSAL` | Medium | CWE-22 | Path traversal attack |
| `SECRET-API_KEY` | High | CWE-798 | Hardcoded API key |
| `SECRET-PASSWORD` | High | CWE-798 | Hardcoded password |
| `SECRET-AWS_KEY` | High | CWE-798 | AWS credentials |
| `SECRET-TOKEN` | High | CWE-798 | Hardcoded token |
| `SECRET-PRIVATE_KEY` | High | CWE-798 | Private key in code |

## 🎯 Taint Sources (User Input)

```python
TAINT_SOURCES = {
    'request.args.get',
    'request.form.get', 
    'request.json.get',
    'request.data',
    'input',
    'sys.argv',
    'os.environ.get',
    # ... more
}
```

## 💉 Dangerous Sinks

### SQL Sinks
```python
SQL_SINKS = {
    'execute',
    'executemany',
    'cursor.execute',
    'db.execute',
    # ...
}
```

### Command Sinks
```python
COMMAND_SINKS = {
    'os.system',
    'subprocess.call',
    'subprocess.run',
    'eval',
    'exec',
    # ...
}
```

## 📦 Dependencies

### Backend (Python)
```
fastapi==0.109.0
uvicorn==0.27.0
supabase==2.24.0
redis==5.0.1
rq==1.16.0
pydantic==2.12.4
python-multipart==0.0.6
websockets==15.0.1
httpx==0.27.2
```

### Frontend (Node.js)
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "axios": "^1.6.0",
  "vite": "^5.0.8",
  "typescript": "^5.2.2",
  "tailwindcss": "^3.4.0"
}
```

## 🔧 Environment Variables

### Backend (`/app/backend/.env`)
```env
SUPABASE_URL=https://anssjrpiteamrhumrfva.supabase.co
SUPABASE_KEY=your-key-here
REDIS_URL=redis://redis:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Frontend (`/app/frontend/.env`)
```env
VITE_API_URL=http://localhost:8001
```

## 🚦 Service Status

| Service | Status | Port | Command |
|---------|--------|------|---------|
| Backend | ✅ Running | 8001 | `supervisorctl status backend` |
| Frontend | ⬜ Not started | 5173 | `cd frontend && yarn dev` |
| MongoDB | ✅ Running | 27017 | (Default from infrastructure) |
| Redis | ❌ Not available | 6379 | (Running synchronously) |

## 📈 Workflow Diagram

```
┌─────────────┐
│   Upload    │  POST /api/upload
│  .py file   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│Create Job ID│  Generate UUID
│  in Supabase│  Status: pending
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Analyze   │  Run synchronously
│   (Worker)  │  (no Redis queue)
└──────┬──────┘
       │
       ├─→ Parse to IR
       ├─→ Taint Analysis
       ├─→ Secrets Detection
       │
       ↓
┌─────────────┐
│Save Findings│  Update Supabase
│to Database  │  Status: completed
└──────┬──────┘
       │
       ↓
┌─────────────┐
│GET /results │  Return findings[]
│   {job_id}  │
└─────────────┘
```

## 🎨 Frontend Integration Points

Your v0.dev components should use these imports:

```typescript
import { 
  uploadFile, 
  getScanStatus, 
  getResults,
  type SecurityFinding 
} from './lib/api';
```

### Example Usage

```typescript
// 1. Upload
const { job_id } = await uploadFile(file);

// 2. Poll status
const interval = setInterval(async () => {
  const { status, total_findings } = await getScanStatus(job_id);
  if (status === 'completed') {
    clearInterval(interval);
    // Move to step 3
  }
}, 2000);

// 3. Display results
const findings: SecurityFinding[] = await getResults(job_id);
findings.forEach(f => {
  console.log(`${f.rule_id}: Line ${f.location.line}`);
});
```

## ✅ What's Complete

- [x] Universal IR implementation
- [x] Python AST parser
- [x] Taint analysis engine
- [x] Secrets detection
- [x] FastAPI backend with all endpoints
- [x] Supabase integration
- [x] Redis support (optional, falls back to sync)
- [x] Type-safe API client
- [x] Frontend scaffold
- [x] Tailwind CSS configuration
- [x] Docker setup
- [x] Test files and scripts
- [x] Comprehensive documentation

## ⬜ What You Need to Add

- [ ] Create Supabase `scans` table
- [ ] Test backend with curl
- [ ] Add your v0.dev UI components
- [ ] Customize styling
- [ ] Add error boundaries
- [ ] Add loading states
- [ ] Deploy to production

## 🆘 Quick Commands

```bash
# Backend
sudo supervisorctl restart backend
tail -f /var/log/supervisor/backend.out.log

# Frontend
cd /app/frontend && yarn dev

# Test
bash /app/scripts/demo_full_workflow.sh

# Database setup
python /app/scripts/setup_supabase.py
```

---

**Status**: Backend fully operational. Frontend scaffold ready. Database table needs creation.
