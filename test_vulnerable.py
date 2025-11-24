"""Test file with intentional vulnerabilities for testing SecureScan.ai"""
import os
import subprocess
from flask import request, render_template_string

# Hardcoded secrets - should trigger SECRET-API_KEY, SECRET-PASSWORD
API_KEY = "sk_live_abcdef123456789012345678901234567890"
DATABASE_PASSWORD = "super_secret_password_123"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"


def vulnerable_sql_query(cursor):
    """SQL Injection vulnerability - should trigger PY-SQL-INJECTION"""
    user_id = request.args.get('id')
    # Dangerous: direct string concatenation
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return query


def vulnerable_xss():
    """XSS vulnerability - should trigger PY-XSS"""
    user_input = request.args.get('message')
    # Dangerous: rendering user input without escaping
    html = f"<div>{user_input}</div>"
    return render_template_string(html)


def vulnerable_command_injection():
    """Command Injection vulnerability - should trigger PY-COMMAND-INJECTION"""
    filename = request.args.get('file')
    # Dangerous: user input in shell command
    result = os.system(f"cat {filename}")
    return result


def vulnerable_path_traversal():
    """Path Traversal vulnerability - should trigger PY-PATH-TRAVERSAL"""
    user_file = request.args.get('filename')
    # Dangerous: user-controlled file path
    with open(f"/uploads/{user_file}", 'r') as f:
        content = f.read()
    return content


def another_sql_injection(db):
    """Another SQL injection example"""
    username = request.form.get('username')
    password = request.form.get('password')
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    db.execute(query)


def command_injection_subprocess():
    """Command injection via subprocess"""
    user_input = request.json.get('command')
    subprocess.run(user_input, shell=True)


if __name__ == "__main__":
    print("This file contains intentional vulnerabilities for testing")
    print(f"API Key: {API_KEY}")
