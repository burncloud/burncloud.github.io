# burncloud.github.io

BurnCloud 的 Docusaurus 技术文档站点，包含源码入口 Atlas、产品/实施文档和按目标 `crates/` 业务目录展开的代码规则。

架构规则的手工源文件位于：

- `site/manual-docs/architecture/`

构建时会同步到 `docs/architecture/`，并由 `site/sidebars.composed.js` 组成左侧目录。

## 规则与源码

架构规则定义目标边界，不代表现有源码已经完成迁移。源码行为发生变化后，应重新核对技术参考；目录迁移则应通过独立 Issue 逐步完成。
