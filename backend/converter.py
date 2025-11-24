"""Universal IR Converter for Python AST Analysis"""
from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict
from enum import Enum
import ast
import uuid


class NodeType(Enum):
    PROGRAM = "PROGRAM"
    FUNCTION_DEF = "FUNCTION_DEF"
    CLASS_DEF = "CLASS_DEF"
    CALL_EXPRESSION = "CALL_EXPRESSION"
    ASSIGN = "ASSIGN"
    IMPORT = "IMPORT"
    IF_STATEMENT = "IF_STATEMENT"
    FOR_LOOP = "FOR_LOOP"
    WHILE_LOOP = "WHILE_LOOP"
    RETURN = "RETURN"
    VARIABLE = "VARIABLE"
    LITERAL = "LITERAL"
    BINARY_OP = "BINARY_OP"
    UNKNOWN = "UNKNOWN"


@dataclass
class SourceLocation:
    line: int
    column: int
    end_line: int
    end_column: int
    file_path: str


@dataclass
class IRNode:
    uid: str
    node_type: NodeType
    location: SourceLocation
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_tainted: bool = False
    children: List['IRNode'] = field(default_factory=list)
    parent: Optional['IRNode'] = None

    def add_child(self, child: 'IRNode'):
        child.parent = self
        self.children.append(child)


class PythonConverter:
    """Converts Python AST to Universal IR"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.ir_nodes: List[IRNode] = []

    def parse_to_ir(self, file_content: str) -> IRNode:
        """Parse Python code to Universal IR"""
        try:
            tree = ast.parse(file_content, filename=self.file_path)
            root = self._convert_node(tree)
            return root
        except SyntaxError as e:
            # Return error node
            return IRNode(
                uid=str(uuid.uuid4()),
                node_type=NodeType.UNKNOWN,
                location=SourceLocation(0, 0, 0, 0, self.file_path),
                metadata={"error": str(e), "type": "SyntaxError"}
            )

    def _convert_node(self, node: ast.AST, parent: Optional[IRNode] = None) -> IRNode:
        """Convert a single AST node to IR"""
        location = self._get_location(node)
        node_type = self._get_node_type(node)
        metadata = self._extract_metadata(node)

        ir_node = IRNode(
            uid=str(uuid.uuid4()),
            node_type=node_type,
            location=location,
            metadata=metadata,
            parent=parent
        )

        # Recursively convert children
        for child in ast.iter_child_nodes(node):
            child_ir = self._convert_node(child, ir_node)
            ir_node.children.append(child_ir)

        self.ir_nodes.append(ir_node)
        return ir_node

    def _get_location(self, node: ast.AST) -> SourceLocation:
        """Extract location information from AST node"""
        return SourceLocation(
            line=getattr(node, 'lineno', 0),
            column=getattr(node, 'col_offset', 0),
            end_line=getattr(node, 'end_lineno', 0),
            end_column=getattr(node, 'end_col_offset', 0),
            file_path=self.file_path
        )

    def _get_node_type(self, node: ast.AST) -> NodeType:
        """Map AST node type to Universal IR NodeType"""
        type_mapping = {
            ast.Module: NodeType.PROGRAM,
            ast.FunctionDef: NodeType.FUNCTION_DEF,
            ast.AsyncFunctionDef: NodeType.FUNCTION_DEF,
            ast.ClassDef: NodeType.CLASS_DEF,
            ast.Call: NodeType.CALL_EXPRESSION,
            ast.Assign: NodeType.ASSIGN,
            ast.AugAssign: NodeType.ASSIGN,
            ast.AnnAssign: NodeType.ASSIGN,
            ast.Import: NodeType.IMPORT,
            ast.ImportFrom: NodeType.IMPORT,
            ast.If: NodeType.IF_STATEMENT,
            ast.For: NodeType.FOR_LOOP,
            ast.AsyncFor: NodeType.FOR_LOOP,
            ast.While: NodeType.WHILE_LOOP,
            ast.Return: NodeType.RETURN,
            ast.Name: NodeType.VARIABLE,
            ast.Constant: NodeType.LITERAL,
            ast.BinOp: NodeType.BINARY_OP,
        }
        return type_mapping.get(type(node), NodeType.UNKNOWN)

    def _extract_metadata(self, node: ast.AST) -> Dict[str, Any]:
        """Extract metadata from AST node"""
        metadata = {"ast_type": type(node).__name__}

        # Function metadata
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            metadata.update({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "is_async": isinstance(node, ast.AsyncFunctionDef)
            })

        # Class metadata
        elif isinstance(node, ast.ClassDef):
            metadata["name"] = node.name
            metadata["bases"] = [self._get_name(base) for base in node.bases]

        # Call expression metadata
        elif isinstance(node, ast.Call):
            func_name = self._get_call_name(node.func)
            metadata["function"] = func_name
            metadata["num_args"] = len(node.args)

        # Variable metadata
        elif isinstance(node, ast.Name):
            metadata["name"] = node.id
            metadata["context"] = type(node.ctx).__name__

        # Literal metadata
        elif isinstance(node, ast.Constant):
            metadata["value"] = node.value
            metadata["value_type"] = type(node.value).__name__

        # Assignment metadata
        elif isinstance(node, ast.Assign):
            targets = [self._get_name(t) for t in node.targets]
            metadata["targets"] = targets

        # Import metadata
        elif isinstance(node, ast.Import):
            metadata["modules"] = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            metadata["module"] = node.module
            metadata["names"] = [alias.name for alias in node.names]

        return metadata

    def _get_call_name(self, node: ast.AST) -> str:
        """Get the name of a function call"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"

    def _get_name(self, node: ast.AST) -> str:
        """Get name from various node types"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "unknown"
