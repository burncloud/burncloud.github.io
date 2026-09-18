# burncloud.github.io

BurnCloud 的 Docusaurus 文档站点。

仓库只维护两类源码：

- `docs/`：唯一文档内容源；
- `site/`：Docusaurus 工程、导航、样式和依赖。

GitHub Pages 由 `.github/workflows/deploy-docusaurus.yml` 构建并直接部署 `site/build` artifact。生成后的 HTML、JS、CSS 不提交回 `main`。

## 本地构建

```bash
cd site
npm ci
npm run build
```

Docusaurus 直接读取 `../docs`。
