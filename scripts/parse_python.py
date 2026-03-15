"""Parse Python files using the ast module to extract structure, docstrings, and call relationships."""

import ast
import os
import json
import sys
from pathlib import Path
from collections import defaultdict


def get_module_docstring(tree):
    """Extract the module-level docstring from an AST tree."""
    return ast.get_docstring(tree) or ""


def get_imports(tree):
    """Extract import statements from an AST tree."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append({"from": module, "name": alias.name, "alias": alias.asname})
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append({"from": None, "name": alias.name, "alias": alias.asname})
    return imports


def get_decorators(node):
    """Extract decorator names from a function or class node."""
    decorators = []
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            decorators.append(dec.id)
        elif isinstance(dec, ast.Attribute):
            decorators.append(ast.unparse(dec))
        elif isinstance(dec, ast.Call):
            if isinstance(dec.func, ast.Attribute):
                # e.g. @app.get("/path")
                name = ast.unparse(dec.func)
                args = [ast.unparse(a) for a in dec.args]
                decorators.append(f"{name}({', '.join(args)})")
            elif isinstance(dec.func, ast.Name):
                name = dec.func.id
                args = [ast.unparse(a) for a in dec.args]
                decorators.append(f"{name}({', '.join(args)})")
    return decorators


def get_function_calls(node):
    """Extract function call names from within a function body."""
    calls = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                calls.add(child.func.id)
            elif isinstance(child.func, ast.Attribute):
                calls.add(ast.unparse(child.func))
    return sorted(calls)


def get_parameters(node):
    """Extract parameter names from a function definition."""
    params = []
    for arg in node.args.args:
        params.append(arg.arg)
    return params


def extract_router_prefixes(tree):
    """Extract APIRouter/FastAPI router variable names and their prefix arguments."""
    prefixes = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Call):
                func = node.value
                func_name = ""
                if isinstance(func.func, ast.Name):
                    func_name = func.func.id
                elif isinstance(func.func, ast.Attribute):
                    func_name = func.func.attr
                if func_name in ("APIRouter", "FastAPI"):
                    prefix = ""
                    for kw in func.keywords:
                        if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                            prefix = kw.value.value
                    prefixes[target.id] = prefix
    return prefixes


def parse_file(filepath):
    """Parse a single Python file and return its structure."""
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:
        return None

    result = {
        "file": filepath,
        "module_docstring": get_module_docstring(tree),
        "imports": get_imports(tree),
        "classes": [],
        "functions": [],
        "router_prefixes": extract_router_prefixes(tree),
    }

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            cls = {
                "name": node.name,
                "docstring": ast.get_docstring(node) or "",
                "line": node.lineno,
                "decorators": get_decorators(node),
                "methods": [],
                "bases": [ast.unparse(b) for b in node.bases],
            }
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method = {
                        "name": item.name,
                        "docstring": ast.get_docstring(item) or "",
                        "line": item.lineno,
                        "params": get_parameters(item),
                        "decorators": get_decorators(item),
                        "calls": get_function_calls(item),
                        "is_async": isinstance(item, ast.AsyncFunctionDef),
                    }
                    cls["methods"].append(method)
            result["classes"].append(cls)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func = {
                "name": node.name,
                "docstring": ast.get_docstring(node) or "",
                "line": node.lineno,
                "params": get_parameters(node),
                "decorators": get_decorators(node),
                "calls": get_function_calls(node),
                "is_async": isinstance(node, ast.AsyncFunctionDef),
            }
            result["functions"].append(func)

    return result


def resolve_call_targets(file_data, all_files_data):
    """Resolve function calls to their source modules using import information."""
    import_map = {}
    for imp in file_data["imports"]:
        name = imp["alias"] or imp["name"]
        source = imp["from"] or imp["name"]
        import_map[name] = source

    resolved_calls = []
    all_functions = set()
    for item in file_data["functions"]:
        for call in item["calls"]:
            base_name = call.split(".")[0] if "." in call else call
            if base_name in import_map:
                resolved_calls.append({
                    "caller": item["name"],
                    "callee": call,
                    "source_module": import_map[base_name],
                })
    for cls in file_data["classes"]:
        for method in cls["methods"]:
            for call in method["calls"]:
                base_name = call.split(".")[0] if "." in call else call
                if base_name in import_map:
                    resolved_calls.append({
                        "caller": f"{cls['name']}.{method['name']}",
                        "callee": call,
                        "source_module": import_map[base_name],
                    })

    return resolved_calls


def extract_routes(file_data):
    """Extract API route definitions from decorators, resolving router prefixes."""
    router_prefixes = file_data.get("router_prefixes", {})
    routes = []
    for func in file_data["functions"]:
        for dec in func["decorators"]:
            for method in ["get", "post", "put", "delete", "patch", "websocket"]:
                if f".{method}(" in dec:
                    # Extract router variable name (e.g., "api_router" from "api_router.get(...)")
                    router_var = dec.split(f".{method}(")[0]
                    prefix = router_prefixes.get(router_var, "")
                    # Extract path from decorator
                    path_start = dec.find("(") + 1
                    path_end = dec.find(")")
                    path = dec[path_start:path_end].strip("'\"")
                    full_path = prefix + path
                    routes.append({
                        "method": method.upper(),
                        "path": full_path,
                        "handler": func["name"],
                        "docstring": func["docstring"],
                    })
    return routes


def parse_directory(root_dir, base_dir=None):
    """Parse all Python files in a directory tree."""
    if base_dir is None:
        base_dir = root_dir

    all_data = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip __pycache__ and venv
        dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "venv", ".venv", "node_modules")]
        for filename in sorted(filenames):
            if filename.endswith(".py") and filename != "__init__.py":
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, base_dir)
                data = parse_file(filepath)
                if data:
                    data["rel_path"] = rel_path
                    all_data[rel_path] = data

    # Resolve cross-file calls
    for rel_path, data in all_data.items():
        data["resolved_calls"] = resolve_call_targets(data, all_data)
        data["routes"] = extract_routes(data)

    return all_data


def group_by_folder(all_data, base_dir):
    """Group parsed file data by their parent folder."""
    grouped = defaultdict(list)
    for rel_path, data in sorted(all_data.items()):
        folder = os.path.dirname(rel_path)
        if not folder:
            folder = "."
        grouped[folder].append(data)
    return dict(grouped)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_python.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    base_dir = os.path.dirname(target_dir.rstrip("/"))
    result = parse_directory(target_dir, base_dir)
    print(json.dumps(result, indent=2, default=str))
