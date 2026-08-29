from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'site' / 'manual-docs'
DOCS = ROOT / 'docs'
SIDEBAR = ROOT / 'site' / 'sidebars.js'


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
    start = '    // PR_CHANGE_ATLAS_START\n'
    end = '    // PR_CHANGE_ATLAS_END\n'
    pattern = re.compile(re.escape(start) + r'.*?' + re.escape(end), flags=re.S)
    match = pattern.search(text)
    if not match:
        return text, ''
    block = match.group(0)
    return pattern.sub('', text, count=1), block


def indent_block(text: str, spaces: int) -> str:
    prefix = ' ' * spaces
    return '\n'.join(prefix + line if line else line for line in text.splitlines())


def build_sidebar():
    text = SIDEBAR.read_text(encoding='utf-8')
    text, pr_block = extract_pr_block(text)

    prefix = 'module.exports = {\n  docsSidebar: [\n'
    suffix = '  ],\n};'
    if not text.startswith(prefix) or suffix not in text:
        raise RuntimeError('unexpected generated sidebar shape')

    body = text[len(prefix):text.rfind(suffix)]
    body = re.sub(r"^\s*\{type:'doc', id:'index', label:'BurnCloud'\},\n", '', body, count=1)
    body = body.replace('collapsed:false', 'collapsed:true').rstrip()

    # PR history belongs to Technical Reference, always after the generated source categories.
    pr_category = ''
    if pr_block:
        lines = [line for line in pr_block.splitlines()
                 if 'PR_CHANGE_ATLAS_START' not in line and 'PR_CHANGE_ATLAS_END' not in line]
        pr_category = '\n'.join(lines).strip().replace('collapsed:false', 'collapsed:true')

    generated_reference = body
    if pr_category:
        generated_reference += '\n' + pr_category

    sidebar = """module.exports = {
  docsSidebar: [
    {type:'category', label:'BurnCloud', collapsed:false, link:{type:'doc', id:'index'}, items:[
      {type:'category', label:'BurnCloud Node', collapsed:true, link:{type:'doc', id:'burncloud-node/index'}, items:[
        {type:'doc', id:'burncloud-node/local-api-gateway', label:'Local API Gateway'},
        {type:'doc', id:'burncloud-node/hardware-detection', label:'Hardware Detection'},
        {type:'doc', id:'burncloud-node/model-resolver', label:'Model Resolver'},
        {type:'doc', id:'burncloud-node/model-manager', label:'Model Manager'},
        {type:'doc', id:'burncloud-node/runtime-manager', label:'Runtime Manager'},
        {type:'doc', id:'burncloud-node/process-manager', label:'Process Manager'},
      ]},
      {type:'category', label:'BurnCloud Network', collapsed:true, link:{type:'doc', id:'burncloud-network/index'}, items:[]},
    ]},
    {type:'category', label:'Technical Reference', collapsed:true, items:[
"""
    sidebar += indent_block(generated_reference, 6) + '\n'
    sidebar += """    ]},
  ],
};
"""
    SIDEBAR.write_text(sidebar, encoding='utf-8')

    final = SIDEBAR.read_text(encoding='utf-8')
    for required in [
        "label:'BurnCloud Node'",
        "label:'BurnCloud Network'",
        "label:'Technical Reference'",
        'PR Change Atlas（最近 50 条）',
    ]:
        if required not in final:
            raise RuntimeError(f'missing sidebar entry: {required}')
    if final.find("label:'BurnCloud Node'") > final.find("label:'Technical Reference'"):
        raise RuntimeError('BurnCloud Node must appear before Technical Reference')
    if final.rfind('PR Change Atlas（最近 50 条）') < final.rfind('UI-only Actions'):
        raise RuntimeError('PR Change Atlas must remain the last Technical Reference category')


def main():
    copy_manual_docs()
    build_sidebar()
    print('Generated BurnCloud product docs and product-first sidebar hierarchy')


if __name__ == '__main__':
    main()
