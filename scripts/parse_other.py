"""Parse non-Python, non-JS files using universal-ctags for symbol extraction."""

import subprocess
import json
import os
import sys
from collections import defaultdict


# File extensions handled by the Python and frontend parsers
HANDLED_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.htm',
}

# Extensions to skip entirely
SKIP_EXTENSIONS = {
    '.pyc', '.pyo', '.so', '.dylib', '.dll',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot',
    '.zip', '.tar', '.gz', '.bz2',
    '.db', '.sqlite', '.sqlite3',
    '.lock',
}

# Directories to skip
SKIP_DIRS = {
    '__pycache__', 'venv', '.venv', 'node_modules', '.git',
    '.pytest_cache', '.mypy_cache', '.tox', 'dist', 'build',
}

# Relevant ctags kinds to keep
RELEVANT_KINDS = {
    'function', 'class', 'method', 'variable', 'constant',
    'interface', 'type', 'enum', 'struct', 'module',
    'target', 'service', 'key', 'anchor',
}


def find_ctags():
    """Find the universal-ctags binary."""
    for path in ['/opt/homebrew/bin/ctags', '/usr/local/bin/ctags']:
        if os.path.exists(path):
            # Verify it's universal-ctags
            try:
                result = subprocess.run([path, '--version'], capture_output=True, text=True)
                if 'Universal Ctags' in result.stdout:
                    return path
            except Exception:
                continue
    return None


def run_ctags(directory, base_dir):
    """Run universal-ctags on a directory and return parsed JSON output."""
    ctags_bin = find_ctags()
    if not ctags_bin:
        return {}

    # Collect files that aren't handled by other parsers
    files_to_scan = []
    for dirpath, dirnames, filenames in os.walk(directory):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in sorted(filenames):
            ext = os.path.splitext(filename)[1].lower()
            if ext in HANDLED_EXTENSIONS or ext in SKIP_EXTENSIONS:
                continue
            filepath = os.path.join(dirpath, filename)
            files_to_scan.append(filepath)

    if not files_to_scan:
        return {}

    # Write file list to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('\n'.join(files_to_scan))
        filelist_path = f.name

    try:
        result = subprocess.run(
            [ctags_bin, '--output-format=json', '--fields=+nKS', '-L', filelist_path],
            capture_output=True, text=True, timeout=30
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {}
    finally:
        os.unlink(filelist_path)

    tags = {}
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        try:
            tag = json.loads(line)
        except json.JSONDecodeError:
            continue

        kind = tag.get('kind', '')
        if kind not in RELEVANT_KINDS:
            continue

        filepath = tag.get('path', '')
        rel_path = os.path.relpath(filepath, base_dir)

        if rel_path not in tags:
            tags[rel_path] = {
                "file": filepath,
                "rel_path": rel_path,
                "symbols": [],
            }

        tags[rel_path]["symbols"].append({
            "name": tag.get("name", ""),
            "kind": kind,
            "line": tag.get("line", 0),
            "scope": tag.get("scope", ""),
            "scope_kind": tag.get("scopeKind", ""),
        })

    return tags


def parse_config_files(directory, base_dir):
    """Parse known config file formats for structure."""
    config_data = {}

    for dirpath, dirnames, filenames in os.walk(directory):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in sorted(filenames):
            filepath = os.path.join(dirpath, filename)
            rel_path = os.path.relpath(filepath, base_dir)
            ext = os.path.splitext(filename)[1].lower()

            if ext in HANDLED_EXTENSIONS or ext in SKIP_EXTENSIONS:
                continue

            try:
                info = None

                if filename == '.env' or filename == '.env.example':
                    info = _parse_env_file(filepath)
                elif filename == 'requirements.txt':
                    info = _parse_requirements(filepath)
                elif filename == 'Dockerfile':
                    info = _parse_dockerfile(filepath)
                elif filename in ('docker-compose.yml', 'docker-compose.yaml'):
                    info = _parse_docker_compose(filepath)
                elif ext in ('.yaml', '.yml'):
                    info = _parse_yaml_keys(filepath)
                elif ext == '.toml':
                    info = _parse_toml_keys(filepath)
                elif filename == '.gitignore':
                    info = _parse_gitignore(filepath)
                elif ext == '.md':
                    info = _parse_markdown_headings(filepath)
                elif ext == '.cfg' or ext == '.ini':
                    info = _parse_ini_sections(filepath)

                if info:
                    config_data[rel_path] = {
                        "file": filepath,
                        "rel_path": rel_path,
                        **info,
                    }
            except Exception:
                continue

    return config_data


def _parse_env_file(filepath):
    """Extract variable names from a .env file (not values)."""
    variables = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                var_name = line.split('=', 1)[0].strip()
                variables.append(var_name)
    return {"type": "env", "variables": variables}


def _parse_requirements(filepath):
    """Extract package names from requirements.txt."""
    packages = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                pkg = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('[')[0].strip()
                if pkg:
                    packages.append(pkg)
    return {"type": "requirements", "packages": packages}


def _parse_dockerfile(filepath):
    """Extract key directives from a Dockerfile."""
    directives = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                parts = line.split(None, 1)
                if parts and parts[0].upper() in ('FROM', 'EXPOSE', 'CMD', 'ENTRYPOINT', 'WORKDIR', 'ENV', 'COPY', 'RUN'):
                    directives.append({"instruction": parts[0].upper(), "value": parts[1] if len(parts) > 1 else ""})
    return {"type": "dockerfile", "directives": directives}


def _parse_docker_compose(filepath):
    """Extract service names from docker-compose.yml."""
    services = []
    with open(filepath, 'r') as f:
        in_services = False
        for line in f:
            stripped = line.strip()
            if stripped == 'services:':
                in_services = True
                continue
            if in_services and not line.startswith(' ') and not line.startswith('\t') and stripped:
                in_services = False
            if in_services and line.startswith('  ') and not line.startswith('    ') and stripped.endswith(':'):
                services.append(stripped[:-1].strip())
    return {"type": "docker-compose", "services": services}


def _parse_yaml_keys(filepath):
    """Extract top-level keys from a YAML file."""
    keys = []
    with open(filepath, 'r') as f:
        for line in f:
            if line and not line.startswith(' ') and not line.startswith('\t') and not line.startswith('#'):
                stripped = line.strip()
                if stripped.endswith(':'):
                    keys.append(stripped[:-1])
                elif ':' in stripped:
                    keys.append(stripped.split(':')[0].strip())
    return {"type": "yaml", "top_level_keys": keys}


def _parse_toml_keys(filepath):
    """Extract section headers from a TOML file."""
    sections = []
    with open(filepath, 'r') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                sections.append(stripped[1:-1])
    return {"type": "toml", "sections": sections}


def _parse_gitignore(filepath):
    """Extract patterns from .gitignore."""
    patterns = []
    with open(filepath, 'r') as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                patterns.append(stripped)
    return {"type": "gitignore", "patterns": patterns}


def _parse_markdown_headings(filepath):
    """Extract headings from a Markdown file."""
    headings = []
    with open(filepath, 'r') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('#'):
                level = len(stripped) - len(stripped.lstrip('#'))
                title = stripped.lstrip('#').strip()
                headings.append({"level": level, "title": title})
    return {"type": "markdown", "headings": headings}


def _parse_ini_sections(filepath):
    """Extract sections from an INI/CFG file."""
    sections = []
    with open(filepath, 'r') as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('[') and stripped.endswith(']'):
                sections.append(stripped[1:-1])
    return {"type": "ini", "sections": sections}


def parse_directory(root_dir, base_dir=None):
    """Parse all non-Python, non-JS files in a directory tree."""
    if base_dir is None:
        base_dir = root_dir

    result = {
        "ctags": run_ctags(root_dir, base_dir),
        "config": parse_config_files(root_dir, base_dir),
    }
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_other.py <directory>")
        sys.exit(1)

    target_dir = sys.argv[1]
    result = parse_directory(target_dir, target_dir)
    print(json.dumps(result, indent=2, default=str))
