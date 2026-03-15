"""Parse frontend JS/HTML files to extract functions, fetch calls, and UI structure."""

import re
import os
import json
import sys
from pathlib import Path
from collections import defaultdict


def extract_functions(source, filename):
    """Extract function declarations from JavaScript source code."""
    functions = []

    # Match: function name(params) {
    for match in re.finditer(r'(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)', source):
        line_num = source[:match.start()].count('\n') + 1
        functions.append({
            "name": match.group(1),
            "params": match.group(2).strip(),
            "line": line_num,
            "is_async": "async" in source[max(0, match.start()-6):match.start()],
        })

    # Match: const/let/var name = (params) => {
    for match in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>', source):
        line_num = source[:match.start()].count('\n') + 1
        functions.append({
            "name": match.group(1),
            "params": match.group(2).strip(),
            "line": line_num,
            "is_async": "async" in match.group(0),
        })

    # Match: const/let/var name = async (params) => {
    for match in re.finditer(r'(?:const|let|var)\s+(\w+)\s*=\s*async\s+\(([^)]*)\)\s*=>', source):
        line_num = source[:match.start()].count('\n') + 1
        # Avoid duplicates
        if not any(f["name"] == match.group(1) and f["line"] == line_num for f in functions):
            functions.append({
                "name": match.group(1),
                "params": match.group(2).strip(),
                "line": line_num,
                "is_async": True,
            })

    return functions


def extract_fetch_calls(source, fetch_patterns=None):
    """Extract fetch/XHR API calls with URL patterns."""
    calls = []
    if fetch_patterns:
        fetch_func = r'(?:' + '|'.join(fetch_patterns) + r')'
    else:
        fetch_func = r'(?:auth|api)?[Ff]etch'

    # Match string literals (single/double quotes only)
    for match in re.finditer(fetch_func + r'\s*\(\s*([\'"])([^\'"]+)\1', source):
        url = match.group(2)
        line_num = source[:match.start()].count('\n') + 1
        method = "GET"
        context = source[match.start():match.start()+300]
        method_match = re.search(r'method\s*:\s*[\'"](\w+)[\'"]', context)
        if method_match:
            method = method_match.group(1).upper()
        calls.append({"url": url, "method": method, "line": line_num})

    # Match template literals (backticks) — normalize ${expressions} to *
    for match in re.finditer(fetch_func + r'\s*\(\s*`([^`]+)`', source):
        url = match.group(1)
        line_num = source[:match.start()].count('\n') + 1
        # Replace all template expressions with *
        normalized = re.sub(r'\$\{[^}]+\}', '*', url)
        method = "GET"
        context = source[match.start():match.start()+300]
        method_match = re.search(r'method\s*:\s*[\'"](\w+)[\'"]', context)
        if method_match:
            method = method_match.group(1).upper()
        calls.append({"url": normalized, "method": method, "line": line_num})

    return calls


def extract_websocket_connections(source):
    """Extract WebSocket connection URLs."""
    connections = []
    for match in re.finditer(r'new\s+WebSocket\s*\(\s*[`\'"]([^`\'"]+)[`\'"]', source):
        url = match.group(1)
        line_num = source[:match.start()].count('\n') + 1
        normalized = re.sub(r'\$\{[^}]+\}', '*', url)
        connections.append({"url": normalized, "line": line_num})
    return connections


def extract_event_listeners(source):
    """Extract DOM event listener registrations."""
    listeners = []
    for match in re.finditer(r'addEventListener\s*\(\s*[\'"](\w+)[\'"]', source):
        event_type = match.group(1)
        line_num = source[:match.start()].count('\n') + 1
        listeners.append({"event": event_type, "line": line_num})
    return listeners


def extract_js_from_html(filepath):
    """Extract JavaScript code blocks from an HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    js_blocks = []
    for match in re.finditer(r'<script[^>]*>(.*?)</script>', content, re.DOTALL):
        js_blocks.append(match.group(1))

    return "\n".join(js_blocks), content


def parse_file(filepath, base_dir, fetch_patterns=None):
    """Parse a single frontend file and return its structure."""
    rel_path = os.path.relpath(filepath, base_dir)
    ext = os.path.splitext(filepath)[1].lower()

    if ext in ('.html', '.htm'):
        js_source, full_content = extract_js_from_html(filepath)
        file_type = "html"
    elif ext in ('.js', '.jsx', '.ts', '.tsx'):
        with open(filepath, "r", encoding="utf-8") as f:
            js_source = f.read()
            full_content = js_source
        file_type = "javascript"
    else:
        return None

    result = {
        "file": filepath,
        "rel_path": rel_path,
        "type": file_type,
        "functions": extract_functions(js_source, filepath),
        "fetch_calls": extract_fetch_calls(js_source, fetch_patterns),
        "websocket_connections": extract_websocket_connections(js_source),
        "event_listeners": extract_event_listeners(js_source),
    }

    return result


def parse_directory(root_dir, base_dir=None, fetch_patterns=None):
    """Parse all frontend files in a directory tree."""
    if base_dir is None:
        base_dir = root_dir

    frontend_extensions = {'.html', '.htm', '.js', '.jsx', '.ts', '.tsx'}
    all_data = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".venv", "venv", "__pycache__")]
        for filename in sorted(filenames):
            ext = os.path.splitext(filename)[1].lower()
            if ext in frontend_extensions:
                filepath = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(filepath, base_dir)
                data = parse_file(filepath, base_dir, fetch_patterns)
                if data:
                    all_data[rel_path] = data

    return all_data


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_frontend.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    base_dir = os.path.dirname(target_dir.rstrip("/"))
    result = parse_directory(target_dir, base_dir)
    print(json.dumps(result, indent=2, default=str))
