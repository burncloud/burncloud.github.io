from __future__ import annotations

import re
from pathlib import PurePosixPath

import enrich_execution_truth_v4 as v4

# Only parse calls that are NOT object-method syntax (`obj.method()`).
# Without Rust type inference, guessing the receiver type would create false edges.
v4.CALL_NAME_RE = re.compile(
    r"(?<!\.)\b([A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*)\s*\("
)

_MASK_CACHE: dict[int, tuple[str, str]] = {}


def mask_non_code(text: str) -> str:
    """Mask comments and literal contents while preserving positions/newlines.

    Handles normal strings, raw strings, nested block comments, line comments,
    byte strings, char literals, and distinguishes Rust lifetimes (`'a`, `'_`)
    from character literals. The output has exactly the same length as input.
    """
    out = list(text)
    i = 0
    n = len(text)

    def blank(a: int, b: int):
        for k in range(a, min(b, n)):
            if out[k] != "\n":
                out[k] = " "

    while i < n:
        if text.startswith("//", i):
            j = text.find("\n", i + 2)
            if j < 0:
                j = n
            blank(i, j)
            i = j
            continue

        if text.startswith("/*", i):
            start = i
            depth = 1
            i += 2
            while i < n and depth:
                if text.startswith("/*", i):
                    depth += 1; i += 2
                elif text.startswith("*/", i):
                    depth -= 1; i += 2
                else:
                    i += 1
            blank(start, i)
            continue

        # Raw strings: r"...", r#"..."#, br#"..."# etc.
        raw = re.match(r"(?:b)?r(#{0,16})\"", text[i:])
        if raw:
            hashes = raw.group(1)
            start = i
            content_start = i + raw.end()
            end_marker = '"' + hashes
            j = text.find(end_marker, content_start)
            i = n if j < 0 else j + len(end_marker)
            blank(start, i)
            continue

        # Normal / byte string.
        prefix = 2 if text.startswith('b"', i) else (1 if text[i] == '"' else 0)
        if prefix:
            start = i
            i += prefix
            esc = False
            while i < n:
                c = text[i]
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == '"':
                    i += 1
                    break
                i += 1
            blank(start, i)
            continue

        if text[i] == "'":
            # Lifetime if `'` is followed by an identifier and there is no
            # immediate closing quote after that identifier: 'a, 'static, '_ .
            lm = re.match(r"'[A-Za-z_][A-Za-z0-9_]*", text[i:])
            if lm:
                after = i + lm.end()
                if after >= n or text[after] != "'":
                    i += lm.end()
                    continue

            # Otherwise treat it as a char literal and mask until closing quote.
            start = i
            i += 1
            esc = False
            while i < n:
                c = text[i]
                if esc:
                    esc = False
                elif c == "\\":
                    esc = True
                elif c == "'":
                    i += 1
                    break
                i += 1
            blank(start, i)
            continue

        i += 1

    return "".join(out)


def masked(text: str) -> str:
    key = id(text)
    cached = _MASK_CACHE.get(key)
    if cached is not None and cached[0] is text:
        return cached[1]
    m = mask_non_code(text)
    _MASK_CACHE[key] = (text, m)
    return m


def safe_match_brace(text: str, open_pos: int) -> int:
    code = masked(text)
    depth = 0
    for i in range(open_pos, len(code)):
        c = code[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def module_matches_path(module: str, path: str) -> bool:
    """Conservative module-name check for calls like `scheduler::foo()`.

    A module token may correspond to `foo.rs` or `foo/mod.rs`. This deliberately
    does not try to understand crate re-exports: unresolved is better than wrong.
    """
    p = PurePosixPath(path)
    if p.name == f"{module}.rs":
        return True
    if p.name == "mod.rs" and p.parent.name == module:
        return True
    return False


def resolve_explicit_call(self: v4.RustIndex, call: str):
    parts = call.split("::")
    if len(parts) < 2:
        return None
    qualifier = parts[-2]
    method = parts[-1]

    # Associated call Type::method(): require an exact parsed impl owner match.
    exact = self.by_qual.get(f"{qualifier}::{method}", [])
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None

    # Module function module::function(): only accept a unique free function
    # whose source path itself matches the module token. Never fall back to
    # global method-name uniqueness (e.g. Body::empty must NOT become
    # PriceCache::empty merely because `empty` is unique inside BurnCloud).
    free = [
        d for d in self.by_name.get(method, [])
        if d.qual is None and module_matches_path(qualifier, d.path)
    ]
    if len(free) == 1:
        return free[0]
    return None


def safe_internal_calls(self: v4.RustIndex, d: v4.FnDef):
    code = mask_non_code(d.body)
    raw = [m.group(1) for m in v4.CALL_NAME_RE.finditer(code)]
    out = []
    seen = set()

    for c in raw:
        last = c.split("::")[-1]
        if last in v4.SKIP_NAMES or last == d.name:
            continue

        target = None
        if c.startswith("Self::") and d.qual:
            owner = d.qual.rsplit("::", 1)[0]
            xs = self.by_qual.get(f"{owner}::{last}", [])
            if len(xs) == 1:
                target = xs[0]
        elif "::" in c:
            target = resolve_explicit_call(self, c)
        else:
            # Bare helper call: prefer a unique function in the same source file.
            local = [x for x in self.by_file.get(d.path, []) if x.name == last]
            if len(local) == 1:
                target = local[0]
            else:
                xs = self.by_name.get(last, [])
                if len(xs) == 1:
                    target = xs[0]

        if target is None:
            continue
        key = (c, target.path, target.name, target.qual)
        if key in seen:
            continue
        seen.add(key)
        out.append((c, target))

    return out


# Monkey-patch the shared V4 generator so all its existing page/category logic,
# special direct-mode flows, source-table rendering and validation semantics are
# retained, while the Rust parsing/call resolution becomes conservative.
v4.match_brace = safe_match_brace
v4.RustIndex.internal_calls = safe_internal_calls


if __name__ == "__main__":
    v4.main()
