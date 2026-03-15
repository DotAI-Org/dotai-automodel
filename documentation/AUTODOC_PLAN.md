# AutoDoc System — Build Plan

## Objective
Auto-generate tiered documentation from source code that gives Claude full project context at session start. Updates on every file write/edit via a PostToolUse hook.

## Architecture

### Three Parsers
1. **Python `ast` module** — `.py` files → functions, classes, docstrings, imports, call graph
2. **TypeScript compiler API** — `.js/.ts/.tsx` files → functions, components, JSDoc, imports, renders (future, when frontend migrates)
3. **universal-ctags** — everything else → symbol names, kinds, line numbers

### Output: Tiered Index Files
```
documentation/
├── MASTER_INDEX.md        # Project overview, links to backend/frontend, deploy/run/test
├── backend/
│   └── INDEX.md           # Per-folder sections: files, functions, docstrings, cross-file calls
└── frontend/
    └── INDEX.md           # Per-file sections: functions, fetch calls, UI components
```

### Cross-Domain API Mapping
- Extract route decorators from Python (`@app.get("/api/...")`)
- Extract fetch/XHR calls from JS (`fetch("/api/...")`, template literals normalized)
- Match by URL pattern in MASTER_INDEX.md

### Hook
PostToolUse on `Write|Edit` runs the generation script. Regenerates from current file state — handles additions, modifications, deletions.

---

## Build Steps

### Step 1: Add docstrings to existing codebase (one-time)
- All Python files in `app/` that lack docstrings
- Module-level docstrings for each file
- Function/class-level docstrings
- Skip test files (they're self-documenting via test names)

### Step 2: Build Python parser (`scripts/parse_python.py`)
- Walk `app/` directory
- Use `ast` module to extract per file:
  - Module docstring
  - Imports (from X import Y)
  - Classes with docstrings
  - Functions with docstrings, parameters, decorators
  - Function call graph (resolve calls to imported modules)
- Output: structured dict grouped by folder

### Step 3: Build frontend parser (`scripts/parse_frontend.py`)
- For current vanilla JS (embedded in HTML): regex-based extraction
  - Function declarations
  - fetch() calls with URL patterns
  - Event listeners
- For future React/TS: TypeScript compiler API (deferred)
- Output: structured dict

### Step 4: Build ctags parser (`scripts/parse_other.py`)
- Run universal-ctags on non-py, non-js files
- Parse JSON output
- Group by file, filter to relevant kinds (function, class, target, service)
- Output: structured dict

### Step 5: Build index generator (`scripts/generate_docs.py`)
- Main script that orchestrates all three parsers
- Generates MASTER_INDEX.md:
  - Hand-written section (preserved across regenerations) — project purpose, deploy/run/test
  - Auto-generated section — file tree, backend/frontend summaries, API contract map
- Generates backend/INDEX.md:
  - Section per folder (db/, agent/, stages/, auth/, chat/, llm/, models/)
  - Each section: files, functions with docstrings, cross-file relationships
- Generates frontend/INDEX.md:
  - Files, functions, fetch calls, UI sections

### Step 6: Configure hook
- Add PostToolUse hook to `.claude/settings.json`
- Matcher: `Write|Edit`
- Command: runs `generate_docs.py`

### Step 7: Test
- Edit a Python file, verify INDEX updates
- Delete a function, verify it disappears from INDEX
- Add a new file, verify it appears

---

## File Inventory

### Files to create:
- `scripts/generate_docs.py` — main orchestrator
- `scripts/parse_python.py` — Python AST parser
- `scripts/parse_frontend.py` — JS/HTML parser
- `scripts/parse_other.py` — ctags wrapper
- `documentation/MASTER_INDEX.md` — generated
- `documentation/backend/INDEX.md` — generated
- `documentation/frontend/INDEX.md` — generated

### Files to modify:
- All `app/**/*.py` — add docstrings (one-time)
- `.claude/settings.json` — add hook config
