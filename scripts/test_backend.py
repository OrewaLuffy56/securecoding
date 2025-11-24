#!/usr/bin/env python3
"""Test script for SecureScan.ai backend"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test the health check endpoint"""
    print("\n✅ Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data.get('status')}")
            print(f"  Supabase: {data.get('supabase')}")
            print(f"  Redis: {data.get('redis')}")
            return True
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_upload_file():
    """Test file upload"""
    print("\n✅ Testing file upload...")
    try:
        # Read the test vulnerable file
        with open('/app/test_vulnerable.py', 'rb') as f:
            files = {'file': ('test_vulnerable.py', f, 'text/x-python')}
            response = requests.post(f"{BASE_URL}/api/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            job_id = data.get('job_id')
            print(f"  Job ID: {job_id}")
            print(f"  Status: {data.get('status')}")
            print(f"  Message: {data.get('message')}")
            return job_id
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def test_scan_status(job_id):
    """Test status checking"""
    print(f"\n✅ Testing status check for job {job_id}...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/api/status/{job_id}")
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                print(f"  Attempt {i+1}: Status = {status}")
                if status == 'completed':
                    print(f"  Total findings: {data.get('total_findings')}")
                    return True
                elif status == 'failed':
                    print(f"  ❌ Job failed")
                    return False
                time.sleep(2)
            else:
                print(f"  ❌ Failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    print("  ⚠️ Timeout waiting for completion")
    return False

def test_get_results(job_id):
    """Test getting results"""
    print(f"\n✅ Testing results retrieval for job {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/results/{job_id}")
        if response.status_code == 200:
            findings = response.json()
            print(f"  Total findings: {len(findings)}")
            print("\n  Findings Summary:")
            for finding in findings[:5]:  # Show first 5
                print(f"    - {finding['rule_id']}: {finding['severity']} (Line {finding['location']['line']})")
            if len(findings) > 5:
                print(f"    ... and {len(findings) - 5} more")
            return True
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SecureScan.ai Backend Test Suite")
    print("="*50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Is the backend running?")
        sys.exit(1)
    
    # Test 2: Upload file
    job_id = test_upload_file()
    if not job_id:
        print("\n❌ File upload failed")
        sys.exit(1)
    
    # Test 3: Check status
    if not test_scan_status(job_id):
        print("\n❌ Status check failed")
        sys.exit(1)
    
    # Test 4: Get results
    if not test_get_results(job_id):
        print("\n❌ Results retrieval failed")
        sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ All tests passed successfully!")
    print("="*50)
