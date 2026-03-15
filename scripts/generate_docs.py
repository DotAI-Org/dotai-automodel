#!/usr/bin/env python3
"""Generate tiered documentation indexes from source code using AST parsing, regex, and ctags."""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from collections import defaultdict

# Add scripts dir to path
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from parse_python import parse_directory as parse_python_dir, group_by_folder
from parse_frontend import parse_directory as parse_frontend_dir
from parse_other import parse_directory as parse_other_dir

# --- Configuration ---

DEFAULT_BACKEND_CANDIDATES = ["app", "src", "backend"]
DEFAULT_FRONTEND_CANDIDATES = ["static", "frontend", "client"]
DEFAULT_OUTPUT_DIR = "documentation"
DEFAULT_FETCH_PATTERNS = ["fetch"]


def load_config(project_root):
    """Load autodoc.json from project root, falling back to auto-detection."""
    config_path = os.path.join(project_root, "autodoc.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)

    project_name = config.get("project_name", os.path.basename(os.path.abspath(project_root)))

    backend_dirs = config.get("backend_dirs")
    if not backend_dirs:
        backend_dirs = [d for d in DEFAULT_BACKEND_CANDIDATES if os.path.isdir(os.path.join(project_root, d))]

    frontend_dirs = config.get("frontend_dirs")
    if not frontend_dirs:
        frontend_dirs = [d for d in DEFAULT_FRONTEND_CANDIDATES if os.path.isdir(os.path.join(project_root, d))]

    output_dir = config.get("output_dir", DEFAULT_OUTPUT_DIR)
    fetch_patterns = config.get("fetch_patterns", DEFAULT_FETCH_PATTERNS)

    return {
        "project_name": project_name,
        "backend_dirs": backend_dirs,
        "frontend_dirs": frontend_dirs,
        "output_dir": output_dir,
        "fetch_patterns": fetch_patterns,
    }


def resolve_paths(project_root, config):
    """Resolve config values to paths."""
    doc_dir = os.path.join(project_root, config["output_dir"])
    backend_paths = [os.path.join(project_root, d) for d in config["backend_dirs"]]
    frontend_paths = [os.path.join(project_root, d) for d in config["frontend_dirs"]]
    return doc_dir, backend_paths, frontend_paths


# Determine project root: CLI arg > parent of scripts dir
def get_project_root():
    parser = argparse.ArgumentParser(description="Generate documentation indexes.")
    parser.add_argument("project_root", nargs="?", default=os.path.dirname(SCRIPTS_DIR),
                        help="Path to the project root (defaults to parent of scripts dir)")
    args = parser.parse_args()
    return os.path.abspath(args.project_root)


PROJECT_ROOT = get_project_root()
CONFIG = load_config(PROJECT_ROOT)
DOC_DIR, BACKEND_PATHS, FRONTEND_PATHS = resolve_paths(PROJECT_ROOT, CONFIG)

BACKEND_INDEX = os.path.join(DOC_DIR, "backend", "INDEX.md")
FRONTEND_INDEX = os.path.join(DOC_DIR, "frontend", "INDEX.md")
MASTER_INDEX = os.path.join(DOC_DIR, "MASTER_INDEX.md")

# Marker for hand-written sections
HAND_WRITTEN_START = "<!-- HAND-WRITTEN START -->"
HAND_WRITTEN_END = "<!-- HAND-WRITTEN END -->"


def preserve_hand_written(filepath):
    """Read existing file and extract hand-written sections to preserve."""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "r") as f:
        content = f.read()

    # Extract content between markers
    match = re.search(
        re.escape(HAND_WRITTEN_START) + r"(.*?)" + re.escape(HAND_WRITTEN_END),
        content, re.DOTALL
    )
    if match:
        return match.group(1)
    return ""


def generate_backend_index(python_data):
    """Generate backend/INDEX.md from parsed Python data."""
    grouped = group_by_folder(python_data, PROJECT_ROOT)
    lines = []
    lines.append("# Backend Index")
    lines.append("")
    lines.append("*Auto-generated from source code. Do not edit the auto-generated sections.*")
    lines.append("")

    # Collect all routes across files
    all_routes = []
    for rel_path, data in python_data.items():
        for route in data.get("routes", []):
            route["file"] = rel_path
            all_routes.append(route)

    if all_routes:
        lines.append("## API Routes")
        lines.append("")
        lines.append("| Method | Path | Handler | File |")
        lines.append("|--------|------|---------|------|")
        for route in sorted(all_routes, key=lambda r: r["path"]):
            lines.append(f"| {route['method']} | `{route['path']}` | `{route['handler']}()` | `{route['file']}` |")
        lines.append("")

    # Per-folder sections
    for folder, files in sorted(grouped.items()):
        folder_display = folder if folder != "." else "app/"
        lines.append(f"## `{folder_display}/`")
        lines.append("")

        for file_data in files:
            rel = file_data["rel_path"]
            docstring = file_data.get("module_docstring", "")
            lines.append(f"### `{os.path.basename(rel)}`")
            if docstring:
                lines.append(f"> {docstring}")
            lines.append("")

            # Classes
            for cls in file_data.get("classes", []):
                cls_doc = cls.get("docstring", "")
                bases = ", ".join(cls.get("bases", []))
                bases_str = f"({bases})" if bases else ""
                lines.append(f"- **class `{cls['name']}{bases_str}`** (line {cls['line']})")
                if cls_doc:
                    lines.append(f"  > {cls_doc}")
                for method in cls.get("methods", []):
                    async_prefix = "async " if method.get("is_async") else ""
                    params = ", ".join(method.get("params", []))
                    method_doc = method.get("docstring", "")
                    decs = method.get("decorators", [])
                    dec_str = f" `@{decs[0]}`" if decs else ""
                    lines.append(f"  - `{async_prefix}{method['name']}({params})`{dec_str}")
                    if method_doc:
                        lines.append(f"    > {method_doc}")

            # Functions
            for func in file_data.get("functions", []):
                async_prefix = "async " if func.get("is_async") else ""
                params = ", ".join(func.get("params", []))
                func_doc = func.get("docstring", "")
                decs = func.get("decorators", [])
                dec_str = f" `@{decs[0]}`" if decs else ""
                lines.append(f"- `{async_prefix}{func['name']}({params})`{dec_str} (line {func['line']})")
                if func_doc:
                    lines.append(f"  > {func_doc}")

            # Cross-file calls
            resolved = file_data.get("resolved_calls", [])
            if resolved:
                lines.append("")
                lines.append("  **Calls to other modules:**")
                seen = set()
                for call in resolved:
                    key = f"{call['caller']}->{call['source_module']}.{call['callee']}"
                    if key not in seen:
                        seen.add(key)
                        lines.append(f"  - `{call['caller']}` → `{call['source_module']}.{call['callee']}`")

            lines.append("")

    return "\n".join(lines)


def generate_frontend_index(frontend_data):
    """Generate frontend/INDEX.md from parsed frontend data."""
    lines = []
    lines.append("# Frontend Index")
    lines.append("")
    lines.append("*Auto-generated from source code. Do not edit the auto-generated sections.*")
    lines.append("")

    # Collect all fetch calls for the API contract section
    all_fetch_calls = []
    for rel_path, data in frontend_data.items():
        for call in data.get("fetch_calls", []):
            call["file"] = rel_path
            all_fetch_calls.append(call)

    if all_fetch_calls:
        lines.append("## API Calls")
        lines.append("")
        lines.append("| Method | URL | File | Line |")
        lines.append("|--------|-----|------|------|")
        for call in sorted(all_fetch_calls, key=lambda c: c["url"]):
            lines.append(f"| {call['method']} | `{call['url']}` | `{call['file']}` | {call['line']} |")
        lines.append("")

    # WebSocket connections
    all_ws = []
    for rel_path, data in frontend_data.items():
        for conn in data.get("websocket_connections", []):
            conn["file"] = rel_path
            all_ws.append(conn)

    if all_ws:
        lines.append("## WebSocket Connections")
        lines.append("")
        for conn in all_ws:
            lines.append(f"- `{conn['url']}` (`{conn['file']}` line {conn['line']})")
        lines.append("")

    # Per-file sections
    for rel_path, data in sorted(frontend_data.items()):
        lines.append(f"## `{rel_path}`")
        lines.append(f"Type: {data.get('type', 'unknown')}")
        lines.append("")

        functions = data.get("functions", [])
        if functions:
            lines.append("### Functions")
            lines.append("")
            for func in functions:
                async_prefix = "async " if func.get("is_async") else ""
                lines.append(f"- `{async_prefix}{func['name']}({func.get('params', '')})` (line {func['line']})")
            lines.append("")

        listeners = data.get("event_listeners", [])
        if listeners:
            lines.append("### Event Listeners")
            lines.append("")
            event_counts = defaultdict(int)
            for listener in listeners:
                event_counts[listener["event"]] += 1
            for event, count in sorted(event_counts.items()):
                lines.append(f"- `{event}` ({count} listener{'s' if count > 1 else ''})")
            lines.append("")

    return "\n".join(lines)


def _normalize_api_path(path):
    """Normalize an API path for matching: strip prefixes, replace params with *."""
    # Replace {param} with *
    path = re.sub(r'\{[^}]+\}', '*', path)
    # Strip leading ${VAR}/ or */
    path = re.sub(r'^\*/', '/', path)
    # Strip /api prefix if present
    path = re.sub(r'^/api(?=/)', '', path)
    return path


def generate_api_contract(python_data, frontend_data):
    """Generate the API contract mapping between backend routes and frontend calls."""
    # Collect backend routes
    backend_routes = {}
    for rel_path, data in python_data.items():
        for route in data.get("routes", []):
            normalized = _normalize_api_path(route["path"])
            key = f"{route['method']}:{normalized}"
            backend_routes[key] = {
                "method": route["method"],
                "path": route["path"],
                "handler": route["handler"],
                "file": rel_path,
                "docstring": route.get("docstring", ""),
            }

    # Collect frontend fetch calls
    frontend_calls = {}
    for rel_path, data in frontend_data.items():
        for call in data.get("fetch_calls", []):
            normalized = _normalize_api_path(call["url"])
            key = f"{call['method']}:{normalized}"
            if key not in frontend_calls:
                frontend_calls[key] = []
            frontend_calls[key].append({
                "method": call["method"],
                "url": call["url"],
                "file": rel_path,
                "line": call["line"],
            })

    # Match
    lines = []
    lines.append("## API Contract (Backend ↔ Frontend)")
    lines.append("")
    lines.append("| Backend Route | Handler | Frontend Call | Frontend File |")
    lines.append("|---------------|---------|---------------|---------------|")

    matched_routes = set()
    for key, route in sorted(backend_routes.items()):
        if key in frontend_calls:
            for fc in frontend_calls[key]:
                lines.append(
                    f"| `{route['method']} {route['path']}` | `{route['handler']}()` in `{route['file']}` "
                    f"| `{fc['url']}` | `{fc['file']}:{fc['line']}` |"
                )
            matched_routes.add(key)
        else:
            lines.append(
                f"| `{route['method']} {route['path']}` | `{route['handler']}()` in `{route['file']}` "
                f"| *no frontend call found* | - |"
            )

    # Frontend calls with no matching backend route
    for key, calls in sorted(frontend_calls.items()):
        if key not in matched_routes:
            for fc in calls:
                lines.append(
                    f"| *no backend route found* | - "
                    f"| `{fc['method']} {fc['url']}` | `{fc['file']}:{fc['line']}` |"
                )

    lines.append("")
    return "\n".join(lines)


def generate_other_index(other_data):
    """Generate a section for config and other files."""
    lines = []

    config = other_data.get("config", {})
    ctags = other_data.get("ctags", {})

    if not config and not ctags:
        return ""

    lines.append("## Configuration & Other Files")
    lines.append("")

    for rel_path, data in sorted(config.items()):
        file_type = data.get("type", "")
        lines.append(f"### `{rel_path}`")

        if file_type == "env":
            lines.append(f"Environment variables: {', '.join(f'`{v}`' for v in data.get('variables', []))}")
        elif file_type == "requirements":
            lines.append(f"Packages: {', '.join(f'`{p}`' for p in data.get('packages', []))}")
        elif file_type == "yaml":
            lines.append(f"Top-level keys: {', '.join(f'`{k}`' for k in data.get('top_level_keys', []))}")
        elif file_type == "gitignore":
            lines.append(f"Patterns: {len(data.get('patterns', []))} entries")
        elif file_type == "dockerfile":
            for d in data.get("directives", []):
                lines.append(f"- `{d['instruction']}` {d['value']}")
        elif file_type == "docker-compose":
            lines.append(f"Services: {', '.join(f'`{s}`' for s in data.get('services', []))}")
        elif file_type == "markdown":
            for h in data.get("headings", [])[:5]:
                indent = "  " * (h["level"] - 1)
                lines.append(f"{indent}- {h['title']}")
        elif file_type == "ini":
            lines.append(f"Sections: {', '.join(f'`{s}`' for s in data.get('sections', []))}")
        elif file_type == "toml":
            lines.append(f"Sections: {', '.join(f'`{s}`' for s in data.get('sections', []))}")

        lines.append("")

    # ctags symbols for other files
    if ctags:
        lines.append("### Other Symbols (via ctags)")
        lines.append("")
        for rel_path, data in sorted(ctags.items()):
            symbols = data.get("symbols", [])
            if symbols:
                symbol_strs = [f"`{s['name']}` ({s['kind']})" for s in symbols[:10]]
                lines.append(f"**`{rel_path}`**: {', '.join(symbol_strs)}")
        lines.append("")

    return "\n".join(lines)


def generate_master_index(python_data, frontend_data, other_data):
    """Generate MASTER_INDEX.md combining all sources."""
    lines = []
    lines.append(f"# Project Index — {CONFIG['project_name']}")
    lines.append("")

    # Preserve hand-written section
    hand_written = preserve_hand_written(MASTER_INDEX)
    lines.append(HAND_WRITTEN_START)
    if hand_written:
        lines.append(hand_written.rstrip())
    else:
        lines.append("")
        lines.append("## About")
        lines.append(f"{CONFIG['project_name']} — add a description here.")
        lines.append("")
        lines.append("## How to Run")
        lines.append("```bash")
        lines.append("# Add run instructions here")
        lines.append("```")
        lines.append("")
        lines.append("## How to Test")
        lines.append("```bash")
        lines.append("# Add test instructions here")
        lines.append("```")
        lines.append("")
    lines.append(HAND_WRITTEN_END)
    lines.append("")
    lines.append("---")
    lines.append("*Everything below is auto-generated. Do not edit.*")
    lines.append("")

    # Project structure overview
    lines.append("## Project Structure")
    lines.append("")

    # Count files
    py_count = len(python_data)
    fe_count = len(frontend_data)
    other_count = len(other_data.get("config", {})) + len(other_data.get("ctags", {}))

    backend_label = ", ".join(f"`{d}/`" for d in CONFIG["backend_dirs"])
    frontend_label = ", ".join(f"`{d}/`" for d in CONFIG["frontend_dirs"])
    lines.append(f"- **Backend** ({backend_label}): {py_count} Python files → [backend/INDEX.md](backend/INDEX.md)")
    lines.append(f"- **Frontend** ({frontend_label}): {fe_count} files → [frontend/INDEX.md](frontend/INDEX.md)")
    lines.append(f"- **Config/Other**: {other_count} files")
    lines.append("")

    # Backend folder summary
    grouped = group_by_folder(python_data, PROJECT_ROOT)
    lines.append("### Backend Folders")
    lines.append("")
    for folder, files in sorted(grouped.items()):
        folder_display = folder if folder != "." else "app/"
        file_names = [os.path.basename(f["rel_path"]) for f in files]
        lines.append(f"- `{folder_display}/` — {', '.join(f'`{n}`' for n in file_names)}")
    lines.append("")

    # API contract
    api_contract = generate_api_contract(python_data, frontend_data)
    if api_contract:
        lines.append(api_contract)

    # Other files
    other_section = generate_other_index(other_data)
    if other_section:
        lines.append(other_section)

    return "\n".join(lines)


def main():
    """Run all parsers and generate documentation indexes."""
    # Parse backend dirs
    python_data = {}
    for bp in BACKEND_PATHS:
        if os.path.isdir(bp):
            python_data.update(parse_python_dir(bp, PROJECT_ROOT))

    # Parse frontend dirs
    frontend_data = {}
    for fp in FRONTEND_PATHS:
        if os.path.isdir(fp):
            frontend_data.update(parse_frontend_dir(fp, PROJECT_ROOT, CONFIG["fetch_patterns"]))

    other_data = parse_other_dir(PROJECT_ROOT, PROJECT_ROOT)

    # Ensure output directories exist
    os.makedirs(os.path.join(DOC_DIR, "backend"), exist_ok=True)
    os.makedirs(os.path.join(DOC_DIR, "frontend"), exist_ok=True)

    # Generate
    backend_content = generate_backend_index(python_data)
    frontend_content = generate_frontend_index(frontend_data)
    master_content = generate_master_index(python_data, frontend_data, other_data)

    # Write
    with open(BACKEND_INDEX, "w") as f:
        f.write(backend_content)

    with open(FRONTEND_INDEX, "w") as f:
        f.write(frontend_content)

    with open(MASTER_INDEX, "w") as f:
        f.write(master_content)

    # Summary to stdout (gets injected into Claude's context via hook)
    print(f"[autodoc] Updated: MASTER_INDEX.md, backend/INDEX.md, frontend/INDEX.md")
    print(f"[autodoc] Backend: {len(python_data)} files, Frontend: {len(frontend_data)} files")


if __name__ == "__main__":
    main()
