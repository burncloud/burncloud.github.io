const fs=require('fs'); const path=require('path');
const root=path.resolve(__dirname,'../../content'); let changed=0;
function walk(dir){for(const ent of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,ent.name);if(ent.isDirectory())walk(p);else if(ent.isFile()&&p.endsWith('.md')){const old=fs.readFileSync(p,'utf8');const next=old.replaceAll('/#/', '/');if(next!==old){fs.writeFileSync(p,next);changed++;}}}}
walk(root); console.log(`Normalized Docusaurus links in ${changed} Markdown file(s).`);
