#!/bin/bash
# Complete workflow demo for SecureScan.ai

echo "🔐 SecureScan.ai - Full Workflow Demo"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Health Check
echo "Step 1: Health Check"
echo "-------------------"
HEALTH=$(curl -s http://localhost:8001/)
if echo "$HEALTH" | grep -q "operational"; then
    echo -e "${GREEN}✅ Backend is running${NC}"
    echo "$HEALTH" | python -m json.tool
else
    echo -e "${RED}❌ Backend is not running${NC}"
    exit 1
fi
echo ""

# Step 2: Upload test file
echo "Step 2: Upload Vulnerable Test File"
echo "-----------------------------------"
UPLOAD_RESPONSE=$(curl -s -X POST http://localhost:8001/api/upload -F "file=@/app/test_vulnerable.py")

if echo "$UPLOAD_RESPONSE" | grep -q "job_id"; then
    JOB_ID=$(echo "$UPLOAD_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin)['job_id'])")
    echo -e "${GREEN}✅ File uploaded successfully${NC}"
    echo "Job ID: $JOB_ID"
else
    echo -e "${RED}❌ Upload failed${NC}"
    echo "$UPLOAD_RESPONSE"
    echo ""
    echo -e "${YELLOW}⚠️  Did you create the Supabase table?${NC}"
    echo "Run: python /app/scripts/setup_supabase.py"
    exit 1
fi
echo ""

# Step 3: Check status
echo "Step 3: Check Scan Status"
echo "------------------------"
MAX_RETRIES=10
for i in $(seq 1 $MAX_RETRIES); do
    echo "Attempt $i/$MAX_RETRIES..."
    STATUS_RESPONSE=$(curl -s http://localhost:8001/api/status/$JOB_ID)
    STATUS=$(echo "$STATUS_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('status', 'unknown'))" 2>/dev/null || echo "error")
    
    if [ "$STATUS" = "completed" ]; then
        echo -e "${GREEN}✅ Scan completed!${NC}"
        TOTAL_FINDINGS=$(echo "$STATUS_RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total_findings', 0))")
        echo "Total findings: $TOTAL_FINDINGS"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo -e "${RED}❌ Scan failed${NC}"
        exit 1
    else
        echo "Status: $STATUS (waiting...)"
        sleep 2
    fi
done
echo ""

# Step 4: Get results
echo "Step 4: Get Security Findings"
echo "----------------------------"
RESULTS=$(curl -s http://localhost:8001/api/results/$JOB_ID)

if echo "$RESULTS" | grep -q "rule_id"; then
    echo -e "${GREEN}✅ Results retrieved successfully${NC}"
    echo ""
    echo "Security Findings:"
    echo "$RESULTS" | python -c "
import sys, json
findings = json.load(sys.stdin)
for i, f in enumerate(findings, 1):
    severity_color = {
        'High': '\033[0;31m',
        'Medium': '\033[1;33m',
        'Low': '\033[0;34m'
    }.get(f['severity'], '')
    print(f\"{i}. [{severity_color}{f['severity']}\033[0m] {f['rule_id']}\")
    print(f\"   Location: {f['location']['file']}:{f['location']['line']}\")
    print(f\"   CWE: {', '.join(f['cwe'])}\")
    print(f\"   Suggestion: {f['suggestion'][:80]}...\")
    print()
"
else
    echo -e "${RED}❌ Failed to get results${NC}"
    echo "$RESULTS"
    exit 1
fi

echo ""
echo "======================================"
echo -e "${GREEN}✅ Full workflow completed successfully!${NC}"
echo "======================================"
echo ""
echo "📊 Summary:"
echo "  - Backend API: ✅ Working"
echo "  - File Upload: ✅ Working"
echo "  - Analysis Engine: ✅ Working"
echo "  - Database: ✅ Working"
echo ""
echo "🎯 Next: Integrate your v0.dev frontend!"
echo "   1. cd /app/frontend"
echo "   2. Paste your components into src/components/"
echo "   3. Update src/App.tsx"
echo "   4. yarn dev"
