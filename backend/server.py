"""FastAPI Backend for SecureScan.ai"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import redis
from rq import Queue
from supabase import create_client, Client
import uuid

from analyzer import SecurityAnalyzer, SecurityFinding

# Initialize FastAPI
app = FastAPI(title="SecureScan.ai API", version="1.5.0")

# CORS Configuration - Allow frontend on localhost:5173 and preview URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        os.environ.get("APP_URL", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://anssjrpiteamrhumrfva.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFuc3NqcnBpdGVhbXJodW1yZnZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM5MzA1MDgsImV4cCI6MjA3OTUwNjUwOH0.RPy8fKdRdPptvP3Ca6BagISr495XKIgZnFqx8dmrtaE")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Supabase connected successfully")
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    supabase = None

# Initialize Redis
redis_client = None
task_queue = None
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_port = int(os.environ.get('REDIS_PORT', '6379'))

try:
    redis_client = redis.Redis(host=redis_host, port=redis_port, db=0, decode_responses=True, socket_connect_timeout=2)
    redis_client.ping()  # Test connection
    task_queue = Queue(connection=redis_client)
    print("✅ Redis connected successfully")
except Exception as e:
    print(f"⚠️ Redis connection failed: {e}. Running in synchronous mode.")
    redis_client = None
    task_queue = None


# Pydantic Models
class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ScanStatus(BaseModel):
    job_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: Optional[int] = 0
    total_findings: Optional[int] = 0


class FindingResponse(BaseModel):
    rule_id: str
    severity: str
    cwe: List[str]
    location: dict
    suggestion: str
    codeSnippet: str


# Background job function
def analyze_file_job(job_id: str, file_content: str, file_name: str):
    """Background job to analyze file"""
    try:
        # Update status to processing
        if supabase:
            supabase.table('scans').update({
                'status': 'processing',
                'updated_at': datetime.utcnow().isoformat()
            }).eq('job_id', job_id).execute()

        # Run security analysis
        analyzer = SecurityAnalyzer(file_content, file_name)
        findings = analyzer.analyze()

        # Convert findings to dict
        findings_data = [
            {
                "rule_id": f.rule_id,
                "severity": f.severity,
                "cwe": f.cwe,
                "location": f.location,
                "suggestion": f.suggestion,
                "codeSnippet": f.codeSnippet
            }
            for f in findings
        ]

        # Update database with results
        if supabase:
            supabase.table('scans').update({
                'status': 'completed',
                'findings': findings_data,
                'total_findings': len(findings),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('job_id', job_id).execute()

        return {"success": True, "findings_count": len(findings)}

    except Exception as e:
        # Update status to failed
        if supabase:
            supabase.table('scans').update({
                'status': 'failed',
                'error': str(e),
                'updated_at': datetime.utcnow().isoformat()
            }).eq('job_id', job_id).execute()
        raise e


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "SecureScan.ai API",
        "version": "1.5.0",
        "status": "operational",
        "supabase": "connected" if supabase else "disconnected",
        "redis": "connected" if redis_client else "disconnected"
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a Python file for security analysis
    """
    # Validate file type
    if not file.filename.endswith('.py'):
        raise HTTPException(status_code=400, detail="Only Python (.py) files are supported")

    try:
        # Read file content
        content = await file.read()
        file_content = content.decode('utf-8')

        # Generate job ID
        job_id = str(uuid.uuid4())

        # Create scan record in Supabase
        if supabase:
            try:
                supabase.table('scans').insert({
                    'job_id': job_id,
                    'file_name': file.filename,
                    'status': 'pending',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }).execute()
            except Exception as db_error:
                print(f"Database insert error: {db_error}")
                # Continue even if DB fails

        # Queue analysis job (or run synchronously if Redis unavailable)
        if task_queue:
            task_queue.enqueue(analyze_file_job, job_id, file_content, file.filename)
        else:
            # Run synchronously
            analyze_file_job(job_id, file_content, file.filename)

        return UploadResponse(
            job_id=job_id,
            status="pending",
            message=f"File '{file.filename}' uploaded successfully and queued for analysis"
        )

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid UTF-8 encoding in file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/status/{job_id}", response_model=ScanStatus)
async def get_scan_status(job_id: str):
    """
    Get the status of a scan job
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        response = supabase.table('scans').select('*').eq('job_id', job_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        scan_data = response.data[0]
        return ScanStatus(
            job_id=job_id,
            status=scan_data.get('status', 'unknown'),
            progress=100 if scan_data.get('status') == 'completed' else 50,
            total_findings=scan_data.get('total_findings', 0)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@app.get("/api/results/{job_id}", response_model=List[FindingResponse])
async def get_results(job_id: str):
    """
    Get analysis results for a completed scan
    """
    if not supabase:
        raise HTTPException(status_code=503, detail="Database unavailable")

    try:
        response = supabase.table('scans').select('*').eq('job_id', job_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        scan_data = response.data[0]

        if scan_data.get('status') != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Scan not completed. Current status: {scan_data.get('status')}"
            )

        findings = scan_data.get('findings', [])
        return findings

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Results retrieval failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
