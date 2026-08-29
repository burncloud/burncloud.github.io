const fs = require('fs');
const path = require('path');

const buildDir = path.join(__dirname, 'build');
const generatedHome = path.join(buildDir, 'index.html');
const atlasDir = path.join(buildDir, 'atlas');
const atlasHome = path.join(atlasDir, 'index.html');
const nodeHome = path.join(__dirname, 'static', 'node-home.html');

if (!fs.existsSync(generatedHome)) {
  throw new Error(`Docusaurus root page not found: ${generatedHome}`);
}
if (!fs.existsSync(nodeHome)) {
  throw new Error(`BurnCloud Node landing page not found: ${nodeHome}`);
}

fs.mkdirSync(atlasDir, { recursive: true });
fs.copyFileSync(generatedHome, atlasHome);
fs.copyFileSync(nodeHome, generatedHome);

console.log('Published BurnCloud Node landing page at / and preserved the generated Atlas overview at /atlas/.');
