# 🚀 SecureScan.ai - Quick Start Guide

## Current Status

✅ **Backend**: Running on `http://localhost:8001`
✅ **Universal IR Engine**: Fully implemented
✅ **Taint Analysis**: Complete (SQL Injection, XSS, Command Injection, Path Traversal)
✅ **Secrets Detection**: Complete (API keys, passwords, AWS credentials, etc.)
✅ **Frontend Scaffold**: Ready for your v0.dev components
⚠️ **Supabase Table**: Needs to be created (see step 1)

## Step 1: Create Supabase Table (REQUIRED)

The backend is running but needs the database table to store scan results.

### Option A: Using Supabase Dashboard (Recommended)

1. Go to: https://anssjrpiteamrhumrfva.supabase.co/project/_/sql
2. Copy and paste this SQL:

```sql
-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
    id BIGSERIAL PRIMARY KEY,
    job_id UUID UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    findings JSONB DEFAULT '[]'::jsonb,
    total_findings INTEGER DEFAULT 0,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_scans_job_id ON scans(job_id);
CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status);
CREATE INDEX IF NOT EXISTS idx_scans_created_at ON scans(created_at DESC);
```

3. Click **RUN**
4. You should see: "Success. No rows returned"

### Option B: Using the Setup Script

```bash
cd /app
python scripts/setup_supabase.py
```

## Step 2: Test the Backend

Once the table is created, test the API:

```bash
# Test health check
curl http://localhost:8001/

# Upload a test file (with vulnerabilities)
curl -X POST http://localhost:8001/api/upload \
  -F "file=@/app/test_vulnerable.py"

# You'll get a response with a job_id, then check status:
curl http://localhost:8001/api/status/{job_id}

# Get results when completed:
curl http://localhost:8001/api/results/{job_id}
```

## Step 3: Expected Test Results

When you upload `/app/test_vulnerable.py`, the analyzer should detect:

- **3 Hardcoded Secrets**: API key, password, AWS key
- **2 SQL Injection** vulnerabilities
- **1 XSS** vulnerability  
- **1 Command Injection** vulnerability
- **1 Path Traversal** vulnerability

**Total: ~8 findings**

## Step 4: Add Your v0.dev Frontend

Now that the backend is working, you can integrate your v0 UI:

### File Structure
```
/app/frontend/src/
├── lib/
│   └── api.ts           ← API functions ready to use
├── components/          ← Paste your v0 components here
│   └── (your v0 files)
├── App.tsx             ← Replace with your main component
├── main.tsx            ← Entry point (already configured)
└── index.css           ← Tailwind configured
```

### Using the API in Your Components

```typescript
import { uploadFile, getScanStatus, getResults } from './lib/api';
import type { SecurityFinding } from './lib/api';

// Upload file
const response = await uploadFile(file);
const jobId = response.job_id;

// Poll for status
const checkStatus = async () => {
  const status = await getScanStatus(jobId);
  if (status.status === 'completed') {
    const findings: SecurityFinding[] = await getResults(jobId);
    // Display findings
  }
};

// Or use setInterval for polling
```

### Data Contract (TypeScript)

The backend returns findings matching this interface:

```typescript
interface SecurityFinding {
  rule_id: string;           // e.g., "PY-SQL-INJECTION"
  severity: "High" | "Medium" | "Low";
  cwe: string[];             // e.g., ["CWE-89"]
  location: {
    file: string;
    line: number;
  };
  suggestion: string;        // Fix recommendation
  codeSnippet: string;       // The vulnerable code
}
```

## Step 5: Start Frontend Development

```bash
cd /app/frontend
yarn dev
```

Frontend will run on: **http://localhost:5173**

The API client is already configured to talk to `http://localhost:8001`

## Architecture Summary

```
┌─────────────────────┐
│  Your v0.dev UI     │  Port 5173
│  (React + TS)       │
└──────────┬──────────┘
           │
           │ api.ts client
           ↓
┌──────────────────────┐
│  FastAPI Backend     │  Port 8001 ✅ RUNNING
│  (Python)            │
└──────────┬───────────┘
           │
           ├──> Supabase ⚠️ CREATE TABLE FIRST
           │    (PostgreSQL)
           │
           └──> Redis
                (Optional - currently synchronous)
```

## What's Already Built

### Backend (`/app/backend/`)
- ✅ `server.py` - FastAPI app with all endpoints
- ✅ `converter.py` - Universal IR implementation
- ✅ `analyzer.py` - Taint analysis + secrets detection
- ✅ `worker.py` - Redis RQ worker (optional)

### Frontend (`/app/frontend/`)
- ✅ `src/lib/api.ts` - Type-safe API client
- ✅ Vite + React + TypeScript configured
- ✅ Tailwind CSS ready
- ⬜ UI components (you add your v0 code)

### Infrastructure
- ✅ Backend running via supervisor
- ✅ Docker compose file (for future use)
- ✅ Environment variables configured

## Troubleshooting

### Backend not responding?
```bash
sudo supervisorctl status backend
sudo supervisorctl restart backend
tail -f /var/log/supervisor/backend.out.log
```

### Supabase errors?
- Make sure you created the `scans` table (Step 1)
- Check: https://anssjrpiteamrhumrfva.supabase.co/project/_/database/tables

### Frontend can't connect?
- Verify backend is running: `curl http://localhost:8001/`
- Check CORS is allowing your origin
- Open browser dev tools and check network tab

## Next Steps

1. ✅ Create Supabase table (Step 1 above)
2. ✅ Test backend with curl (Step 2 above)
3. ⬜ Paste your v0 components into `/app/frontend/src/components/`
4. ⬜ Update `App.tsx` to use your components
5. ⬜ Start frontend: `cd /app/frontend && yarn dev`
6. ⬜ Test end-to-end flow

## Support Files

- `/app/supabase_setup.sql` - SQL to create the table
- `/app/test_vulnerable.py` - Test file with intentional vulnerabilities
- `/app/scripts/test_backend.py` - Automated backend tests
- `/app/README.md` - Comprehensive documentation

---

**You're 90% there! Just create the Supabase table and start testing. 🎉**
