#!/usr/bin/env python3
"""Fork i18n maintenance audits.

Modes:
  duplicates                 Report duplicate keys in the zh catalog.
  new-strings [BASE]         English UI strings upstream added since BASE that are
                             not yet in the catalog (the translation worklist).
  mark-synced                Record upstream/main as the last-synced base.

BASE defaults to the recorded last-synced commit (.git/fork-sync-base), else the
merge-base of main and upstream/main. Run new-strings BEFORE merging, or pass the
previous upstream tip as BASE after a merge.

Strings are read from the git blobs (upstream/main vs BASE), not the working tree,
so the worklist is correct whether or not the merge has happened. AST extraction
folds implicit multi-line concatenation and skips docstrings and f-string parts,
which a text grep cannot.
"""

from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path

# Bootstrap/recovery UI that runs before Qt and before the language setting is
# readable; it stays English on purpose, so it is never reported.
ENGLISH_ONLY_FILES = {
    "negpy/desktop/windows_data_dialog.py",
    "negpy/desktop/startup.py",
    "negpy/kernel/system/user_directory.py",
}

BASE_FILE = Path(".git/fork-sync-base")


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def _blob(ref: str, path: str) -> str:
    return _git("show", f"{ref}:{path}")


def _default_base() -> str:
    if BASE_FILE.exists():
        return BASE_FILE.read_text().strip()
    return _git("merge-base", "main", "upstream/main").strip()


def _string_constants(src: str) -> set[str]:
    """Plain string literals in src, minus docstrings and f-string fragments."""
    if not src.strip():
        return set()
    tree = ast.parse(src)
    skip: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                skip.add(id(body[0].value))
        if isinstance(node, ast.JoinedStr):
            for part in node.values:
                if isinstance(part, ast.Constant):
                    skip.add(id(part))
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in skip:
            out.add(node.value)
    return out


def _ui_like(s: str) -> bool:
    t = s.strip()
    if len(t) < 3 or not t[:1].isalpha():
        return False
    # Drop code-ish single tokens: field keys, paths, identifiers.
    if " " not in t and t == t.lower() and any(c in t for c in "_.-/"):
        return False
    return True


def _catalog() -> dict[str, str]:
    return importlib.import_module("negpy.kernel.system.i18n_zh").STRINGS


def duplicates() -> int:
    from collections import Counter

    src = Path("negpy/kernel/system/i18n_zh.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    keys: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(getattr(node, "value", None), ast.Dict):
            keys += [ast.literal_eval(k) for k in node.value.keys]
    dupes = [k for k, c in Counter(keys).items() if c > 1]
    print(f"catalog keys: {len(keys)}")
    if dupes:
        print("DUPLICATE KEYS:")
        for d in dupes:
            print("  -", d[:90])
        return 1
    print("duplicates: none")
    return 0


def new_strings(base_arg: str | None) -> int:
    base = base_arg or _default_base()
    if not base:
        print("error: no BASE; pass one explicitly", file=sys.stderr)
        return 2
    print(f"base: {base}")
    print(f"head: upstream/main ({_git('rev-parse', '--short', 'upstream/main').strip()})")

    files = _git("diff", "--name-only", base, "upstream/main", "--", "negpy/").split()
    files = [f for f in files if f.endswith(".py") and "/tests/" not in f and not f.startswith("tests/")]
    files = [f for f in files if f not in ENGLISH_ONLY_FILES]

    catalog = _catalog()
    missing: list[tuple[str, str]] = []
    for path in sorted(files):
        added = _string_constants(_blob("upstream/main", path)) - _string_constants(_blob(base, path))
        for s in sorted(added):
            if _ui_like(s) and s not in catalog:
                missing.append((path, s))

    if not missing:
        print("\nNo untranslated upstream UI strings. Catalog is current.")
        return 0
    print(f"\nNEEDS TRANSLATION ({len(missing)} string(s)):")
    last = None
    for path, s in missing:
        if path != last:
            print(f"\n  {path}")
            last = path
        one = " ".join(s.split())
        print(f"    - {one[:110]}")
    return 1


def mark_synced() -> int:
    tip = _git("rev-parse", "upstream/main").strip()
    if not tip:
        print("error: cannot resolve upstream/main", file=sys.stderr)
        return 2
    BASE_FILE.write_text(tip + "\n")
    print(f"recorded last-synced base: {tip[:12]} -> {BASE_FILE}")
    return 0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    mode = sys.argv[1]
    if mode == "duplicates":
        return duplicates()
    if mode == "new-strings":
        return new_strings(sys.argv[2] if len(sys.argv) > 2 else None)
    if mode == "mark-synced":
        return mark_synced()
    print(f"unknown mode: {mode}\n", file=sys.stderr)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
