# Testing Instructions

## After Creating the Supabase Table, Run:

```bash
# Option 1: Full automated test
bash /app/scripts/demo_full_workflow.sh

# Option 2: Manual testing
# 1. Test health
curl http://localhost:8001/

# 2. Upload a test file
curl -X POST http://localhost:8001/api/upload \
  -F "file=@/app/test_vulnerable.py"

# Copy the job_id from response, then:

# 3. Check status
curl http://localhost:8001/api/status/{YOUR_JOB_ID}

# 4. Get results (once completed)
curl http://localhost:8001/api/results/{YOUR_JOB_ID}
```

## Expected Results:
- ~8 security findings
- Hardcoded secrets detected
- SQL injection vulnerabilities
- XSS, Command injection, Path traversal
