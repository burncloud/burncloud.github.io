from pathlib import Path
import re
import shutil
import textwrap

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site' / 'manual-docs'
DOCS = ROOT / 'docs'
SIDEBAR = ROOT / 'site' / 'sidebars.js'

REFERENCE_START = '// BURNCLOUD_TECHNICAL_REFERENCE_START'
REFERENCE_END = '// BURNCLOUD_TECHNICAL_REFERENCE_END'


def copy_manual_docs():
    if not SOURCE.is_dir():
        raise RuntimeError(f'manual docs source not found: {SOURCE}')

    index_source = SOURCE / 'index.md'
    if not index_source.is_file():
        raise RuntimeError('manual BurnCloud overview is missing')
    shutil.copyfile(index_source, DOCS / 'index.md')

    for name in ('burncloud-node', 'burncloud-network'):
        src = SOURCE / name
        dst = DOCS / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def extract_pr_block(text: str):
    pattern = re.compile(
        r'^[ \t]*// PR_CHANGE_ATLAS_START[ \t]*\n'
        r'.*?'
        r'^[ \t]*// PR_CHANGE_ATLAS_END[ \t]*(?:\n|$)',
        flags=re.M | re.S,
    )
    match = pattern.search(text)
    if not match:
        return text, ''
    block = match.group(0)
    return text[:match.start()] + text[match.end():], block


def indent_block(text: str, spaces: int) -> str:
    prefix = ' ' * spaces
    return '\n'.join(prefix + line if line else line for line in text.splitlines())


def scan_matching(text: str, start: int, opening: str, closing: str) -> int:
    if start >= len(text) or text[start] != opening:
        raise RuntimeError(f'expected {opening!r} at index {start}')

    depth = 0
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    i = start

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ''

        if line_comment:
            if ch == '\n':
                line_comment = False
            i += 1
            continue

        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
                continue
            i += 1
            continue

        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue

        if ch in ("'", '"', '`'):
            quote = ch
            i += 1
            continue

        if ch == '/' and nxt == '/':
            line_comment = True
            i += 2
            continue

        if ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue

        if ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return i

        i += 1

    raise RuntimeError(f'unbalanced {opening}{closing} block')


def array_after(text: str, marker: str) -> str:
    marker_pos = text.find(marker)
    if marker_pos < 0:
        raise RuntimeError(f'missing sidebar marker: {marker}')

    start = text.find('[', marker_pos + len(marker))
    if start < 0:
        raise RuntimeError(f'missing array after {marker}')

    end = scan_matching(text, start, '[', ']')
    return text[start + 1:end]


def top_level_objects(text: str):
    spans = []
    quote = None
    escaped = False
    line_comment = False
    block_comment = False
    brace_depth = 0
    bracket_depth = 0
    start = None
    i = 0

    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ''

        if line_comment:
            if ch == '\n':
                line_comment = False
            i += 1
            continue

        if block_comment:
            if ch == '*' and nxt == '/':
                block_comment = False
                i += 2
                continue
            i += 1
            continue

        if quote:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue

        if ch in ("'", '"', '`'):
            quote = ch
            i += 1
            continue

        if ch == '/' and nxt == '/':
            line_comment = True
            i += 2
            continue

        if ch == '/' and nxt == '*':
            block_comment = True
            i += 2
            continue

        if ch == '[':
            bracket_depth += 1
        elif ch == ']':
            bracket_depth -= 1
        elif ch == '{':
            if brace_depth == 0 and bracket_depth == 0:
                start = i
            brace_depth += 1
        elif ch == '}':
            brace_depth -= 1
            if brace_depth == 0 and bracket_depth == 0 and start is not None:
                spans.append((start, i + 1))
                start = None

        i += 1

    return [text[start:end] for start, end in spans]


def item_field(item: str, field: str):
    pattern = rf"\b{re.escape(field)}\s*:\s*(['\"])(.*?)\1"
    match = re.search(pattern, item, flags=re.S)
    return match.group(2) if match else None


def item_items_array(item: str):
    marker_pos = item.find('items:')
    if marker_pos < 0:
        return None
    start = item.find('[', marker_pos + len('items:'))
    if start < 0:
        return None
    end = scan_matching(item, start, '[', ']')
    return item[start + 1:end]


def unwrap_legacy_product_reference(content: str) -> str:
    """Strip old BurnCloud -> Technical Reference wrappers recursively.

    Older versions of build_sidebar() fed the already-generated sidebar back into
    the next build, so every run could add another BurnCloud/Technical Reference
    layer. Keep this recovery path so running the fixed generator against an
    already-corrupted sidebar repairs it in one pass.
    """
    current = content

    for _ in range(20):
        objects = top_level_objects(current)
        product = next(
            (
                item for item in objects
                if item_field(item, 'type') == 'category'
                and item_field(item, 'label') == 'BurnCloud'
            ),
            None,
        )
        technical = next(
            (
                item for item in objects
                if item_field(item, 'type') == 'category'
                and item_field(item, 'label') == 'Technical Reference'
            ),
            None,
        )

        if product is None or technical is None:
            return current

        inner = item_items_array(technical)
        if inner is None:
            return current
        current = inner

    raise RuntimeError('too many nested legacy product sidebar wrappers')


def extract_marked_reference(text: str):
    start = text.find(REFERENCE_START)
    end = text.find(REFERENCE_END)
    if start < 0 and end < 0:
        return None
    if start < 0 or end < 0 or end < start:
        raise RuntimeError('invalid BurnCloud technical reference markers')

    body_start = text.find('\n', start)
    if body_start < 0:
        return ''
    return textwrap.dedent(text[body_start + 1:end]).strip()


def normalize_reference(text: str) -> str:
    text = textwrap.dedent(text).strip()
    text = text.replace('collapsed:false', 'collapsed:true')
    text, pr_block = extract_pr_block(text)
    text = text.rstrip()

    # PR history belongs to Technical Reference, always after generated source categories.
    if pr_block:
        lines = [
            line for line in textwrap.dedent(pr_block).splitlines()
            if 'PR_CHANGE_ATLAS_START' not in line and 'PR_CHANGE_ATLAS_END' not in line
        ]
        pr_category = '\n'.join(lines).strip().replace('collapsed:false', 'collapsed:true')
        if pr_category:
            text = (text + '\n' + pr_category).strip()

    return text


def extract_reference_body(text: str) -> str:
    marked = extract_marked_reference(text)
    if marked is not None:
        return normalize_reference(marked)

    content = array_after(text, 'docsSidebar:')
    content = unwrap_legacy_product_reference(content)
    content = re.sub(
        r"^\s*\{type:'doc', id:'index', label:'BurnCloud'\},\s*",
        '',
        content,
        count=1,
    )
    return normalize_reference(content)


def render_sidebar(generated_reference: str) -> str:
    sidebar = """module.exports = {
  docsSidebar: [
    {type:'category', label:'BurnCloud', collapsed:false, link:{type:'doc', id:'index'}, items:[
      {type:'category', label:'BurnCloud Node', collapsed:true, link:{type:'doc', id:'burncloud-node/index'}, items:[
        {type:'doc', id:'burncloud-node/local-api-gateway', label:'Local API Gateway'},
        {type:'doc', id:'burncloud-node/protocol-routing', label:'Protocol Routing'},
        {type:'doc', id:'burncloud-node/hardware-detection', label:'Hardware Detection'},
        {type:'doc', id:'burncloud-node/model-resolver', label:'Model Resolver'},
        {type:'doc', id:'burncloud-node/model-manager', label:'Model Manager'},
        {type:'doc', id:'burncloud-node/runtime-manager', label:'Runtime Manager'},
        {type:'doc', id:'burncloud-node/process-manager', label:'Process Manager'},
      ]},
      {type:'doc', id:'burncloud-network/index', label:'BurnCloud Network'},
    ]},
    {type:'category', label:'Technical Reference', collapsed:true, items:[
      // BURNCLOUD_TECHNICAL_REFERENCE_START
"""
    sidebar += indent_block(generated_reference, 6) + '\n'
    sidebar += """      // BURNCLOUD_TECHNICAL_REFERENCE_END
    ]},
  ],
};
"""
    return sidebar


def validate_sidebar(sidebar: str):
    for required in [
        "label:'BurnCloud Node'",
        "label:'Protocol Routing'",
        "label:'BurnCloud Network'",
        "label:'Technical Reference'",
        'PR Change Atlas（最近 50 条）',
    ]:
        if required not in sidebar:
            raise RuntimeError(f'missing sidebar entry: {required}')

    if sidebar.find("label:'BurnCloud Node'") > sidebar.find("label:'Technical Reference'"):
        raise RuntimeError('BurnCloud Node must appear before Technical Reference')
    if sidebar.rfind('PR Change Atlas（最近 50 条）') < sidebar.rfind('UI-only Actions'):
        raise RuntimeError('PR Change Atlas must remain the last Technical Reference category')

    top_labels = [item_field(item, 'label') for item in top_level_objects(array_after(sidebar, 'docsSidebar:'))]
    if top_labels != ['BurnCloud', 'Technical Reference']:
        raise RuntimeError(f'unexpected top-level product sidebar: {top_labels}')

    reference = extract_reference_body(sidebar)
    reference_labels = [item_field(item, 'label') for item in top_level_objects(reference)]
    if 'BurnCloud' in reference_labels or 'Technical Reference' in reference_labels:
        raise RuntimeError(f'nested product sidebar detected: {reference_labels}')

    # The generator must be idempotent. A second pass over its own output must
    # produce byte-for-byte identical sidebars.js content.
    rerendered = render_sidebar(extract_reference_body(sidebar))
    if rerendered != sidebar:
        raise RuntimeError('product sidebar generation is not idempotent')


def build_sidebar():
    text = SIDEBAR.read_text(encoding='utf-8')
    generated_reference = extract_reference_body(text)
    sidebar = render_sidebar(generated_reference)
    validate_sidebar(sidebar)
    SIDEBAR.write_text(sidebar, encoding='utf-8')


def main():
    copy_manual_docs()
    build_sidebar()
    print('Generated BurnCloud product docs and idempotent product-first sidebar hierarchy')


if __name__ == '__main__':
    main()
