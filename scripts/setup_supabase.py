#!/usr/bin/env python3
"""Setup Supabase database table for SecureScan.ai"""
from supabase import create_client

SUPABASE_URL = "https://anssjrpiteamrhumrfva.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFuc3NqcnBpdGVhbXJodW1yZnZhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjM5MzA1MDgsImV4cCI6MjA3OTUwNjUwOH0.RPy8fKdRdPptvP3Ca6BagISr495XKIgZnFqx8dmrtaE"

print("📊 Setting up Supabase database...")
print("="*60)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase")
    
    # Try to query the scans table
    try:
        result = supabase.table('scans').select('*').limit(1).execute()
        print(f"✅ Table 'scans' exists! Found {len(result.data)} rows.")
    except Exception as e:
        print(f"\n❌ Table 'scans' does not exist!")
        print(f"Error: {e}")
        print("\n📋 Please run this SQL in your Supabase SQL Editor:\n")
        print("-" * 60)
        with open('/app/supabase_setup.sql', 'r') as f:
            print(f.read())
        print("-" * 60)
        print("\n🌐 Go to: https://anssjrpiteamrhumrfva.supabase.co/project/_/sql")
        print("   Paste the SQL above and click 'Run'")
        
except Exception as e:
    print(f"❌ Failed to connect to Supabase: {e}")
