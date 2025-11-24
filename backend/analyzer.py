"""Security Analysis Engine with Taint Analysis"""
from typing import List, Set, Dict, Any, Optional
from dataclasses import dataclass
import re
from converter import IRNode, NodeType


@dataclass
class SecurityFinding:
    rule_id: str
    severity: str  # "High", "Medium", "Low"
    cwe: List[str]
    location: Dict[str, Any]
    suggestion: str
    codeSnippet: str


class TaintAnalyzer:
    """Taint analysis engine for tracking data flow"""

    # Define taint sources (user input)
    TAINT_SOURCES = {
        'request.args.get', 'request.form.get', 'request.json.get',
        'request.data', 'request.get_json', 'input', 'sys.argv',
        'os.environ.get', 'flask.request', 'request.query_params',
        'request.body', 'request.POST', 'request.GET'
    }

    # Define dangerous sinks
    SQL_SINKS = {
        'execute', 'executemany', 'cursor.execute', 'raw',
        'cursor.executemany', 'db.execute', 'connection.execute'
    }

    XSS_SINKS = {
        'render_template_string', 'make_response', 'Response',
        'HttpResponse', 'render', 'html'
    }

    COMMAND_SINKS = {
        'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
        'os.popen', 'commands.getoutput', 'eval', 'exec'
    }

    PATH_TRAVERSAL_SINKS = {
        'open', 'file', 'os.path.join', 'Path', 'os.remove',
        'os.unlink', 'shutil.rmtree'
    }

    def __init__(self, ir_root: IRNode):
        self.ir_root = ir_root
        self.tainted_vars: Set[str] = set()
        self.findings: List[SecurityFinding] = []

    def analyze(self) -> List[SecurityFinding]:
        """Run full taint analysis"""
        self._mark_taint_sources(self.ir_root)
        self._check_sql_injection(self.ir_root)
        self._check_xss(self.ir_root)
        self._check_command_injection(self.ir_root)
        self._check_path_traversal(self.ir_root)
        return self.findings

    def _mark_taint_sources(self, node: IRNode):
        """Mark all tainted variables from sources"""
        if node.node_type == NodeType.ASSIGN:
            # Check if assignment comes from tainted source
            for child in node.children:
                if child.node_type == NodeType.CALL_EXPRESSION:
                    func_name = child.metadata.get('function', '')
                    if any(source in func_name for source in self.TAINT_SOURCES):
                        # Mark the assigned variable as tainted
                        targets = node.metadata.get('targets', [])
                        for target in targets:
                            self.tainted_vars.add(target)
                            node.is_tainted = True

        # Recursively process children
        for child in node.children:
            self._mark_taint_sources(child)

    def _check_sql_injection(self, node: IRNode):
        """Check for SQL injection vulnerabilities"""
        if node.node_type == NodeType.CALL_EXPRESSION:
            func_name = node.metadata.get('function', '')
            if any(sink in func_name for sink in self.SQL_SINKS):
                # Check if any argument is tainted
                if self._has_tainted_args(node):
                    self.findings.append(SecurityFinding(
                        rule_id="PY-SQL-INJECTION",
                        severity="High",
                        cwe=["CWE-89"],
                        location={
                            "file": node.location.file_path,
                            "line": node.location.line
                        },
                        suggestion="Use parameterized queries or ORM methods to prevent SQL injection. Never concatenate user input directly into SQL queries.",
                        codeSnippet=self._extract_code_snippet(node)
                    ))

        for child in node.children:
            self._check_sql_injection(child)

    def _check_xss(self, node: IRNode):
        """Check for XSS vulnerabilities"""
        if node.node_type == NodeType.CALL_EXPRESSION:
            func_name = node.metadata.get('function', '')
            if any(sink in func_name for sink in self.XSS_SINKS):
                if self._has_tainted_args(node):
                    self.findings.append(SecurityFinding(
                        rule_id="PY-XSS",
                        severity="High",
                        cwe=["CWE-79"],
                        location={
                            "file": node.location.file_path,
                            "line": node.location.line
                        },
                        suggestion="Sanitize user input before rendering in HTML. Use template auto-escaping or explicit escaping functions.",
                        codeSnippet=self._extract_code_snippet(node)
                    ))

        for child in node.children:
            self._check_xss(child)

    def _check_command_injection(self, node: IRNode):
        """Check for command injection vulnerabilities"""
        if node.node_type == NodeType.CALL_EXPRESSION:
            func_name = node.metadata.get('function', '')
            if any(sink in func_name for sink in self.COMMAND_SINKS):
                if self._has_tainted_args(node):
                    self.findings.append(SecurityFinding(
                        rule_id="PY-COMMAND-INJECTION",
                        severity="High",
                        cwe=["CWE-78"],
                        location={
                            "file": node.location.file_path,
                            "line": node.location.line
                        },
                        suggestion="Avoid using shell=True. Use subprocess with a list of arguments and validate all user inputs.",
                        codeSnippet=self._extract_code_snippet(node)
                    ))

        for child in node.children:
            self._check_command_injection(child)

    def _check_path_traversal(self, node: IRNode):
        """Check for path traversal vulnerabilities"""
        if node.node_type == NodeType.CALL_EXPRESSION:
            func_name = node.metadata.get('function', '')
            if any(sink in func_name for sink in self.PATH_TRAVERSAL_SINKS):
                if self._has_tainted_args(node):
                    self.findings.append(SecurityFinding(
                        rule_id="PY-PATH-TRAVERSAL",
                        severity="Medium",
                        cwe=["CWE-22"],
                        location={
                            "file": node.location.file_path,
                            "line": node.location.line
                        },
                        suggestion="Validate and sanitize file paths. Use os.path.basename() or restrict access to a whitelist of directories.",
                        codeSnippet=self._extract_code_snippet(node)
                    ))

        for child in node.children:
            self._check_path_traversal(child)

    def _has_tainted_args(self, call_node: IRNode) -> bool:
        """Check if call has tainted arguments"""
        for child in call_node.children:
            if child.node_type == NodeType.VARIABLE:
                var_name = child.metadata.get('name', '')
                if var_name in self.tainted_vars:
                    return True
            # Check for string formatting with tainted vars
            elif child.node_type == NodeType.BINARY_OP:
                if self._check_tainted_in_expr(child):
                    return True
        return False

    def _check_tainted_in_expr(self, node: IRNode) -> bool:
        """Recursively check if expression contains tainted variables"""
        if node.node_type == NodeType.VARIABLE:
            var_name = node.metadata.get('name', '')
            if var_name in self.tainted_vars:
                return True
        for child in node.children:
            if self._check_tainted_in_expr(child):
                return True
        return False

    def _extract_code_snippet(self, node: IRNode) -> str:
        """Extract code snippet around the vulnerable location"""
        return f"Line {node.location.line}: {node.metadata.get('function', 'unknown')}(...)"


class SecretsDetector:
    """Detect hardcoded secrets and credentials"""

    SECRET_PATTERNS = {
        'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([a-zA-Z0-9_\-]{20,})["\']',
        'password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{{6,}})["\']',
        'aws_key': r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*["\']([A-Z0-9]{{20}})["\']',
        'private_key': r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
        'token': r'(?i)(token|jwt|bearer)\s*[=:]\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']',
    }

    def __init__(self, code: str, file_path: str):
        self.code = code
        self.file_path = file_path
        self.findings: List[SecurityFinding] = []

    def detect(self) -> List[SecurityFinding]:
        """Detect secrets in code"""
        lines = self.code.split('\n')
        for line_num, line in enumerate(lines, 1):
            for secret_type, pattern in self.SECRET_PATTERNS.items():
                matches = re.finditer(pattern, line)
                for match in matches:
                    self.findings.append(SecurityFinding(
                        rule_id=f"SECRET-{secret_type.upper()}",
                        severity="High",
                        cwe=["CWE-798"],
                        location={
                            "file": self.file_path,
                            "line": line_num
                        },
                        suggestion=f"Remove hardcoded {secret_type} and use environment variables or secret management systems.",
                        codeSnippet=line.strip()
                    ))
        return self.findings


class SecurityAnalyzer:
    """Main security analyzer orchestrator"""

    def __init__(self, code: str, file_path: str):
        self.code = code
        self.file_path = file_path

    def analyze(self) -> List[SecurityFinding]:
        """Run all security analyses"""
        all_findings = []

        # Run secrets detection
        secrets_detector = SecretsDetector(self.code, self.file_path)
        all_findings.extend(secrets_detector.detect())

        # Run taint analysis
        from converter import PythonConverter
        converter = PythonConverter(self.file_path)
        ir_root = converter.parse_to_ir(self.code)
        taint_analyzer = TaintAnalyzer(ir_root)
        all_findings.extend(taint_analyzer.analyze())

        return all_findings
