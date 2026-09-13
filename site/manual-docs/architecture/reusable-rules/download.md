---
title: "Download 规则"
slug: /architecture/reusable-rules/download/
---

# Download 规则

- 下载前由资源 Owner 判断调用方是否有权访问。
- 使用资源 ID，不直接相信调用方提交的文件系统路径。
- 大文件通过 Streaming 处理，不一次性读入内存。
- 文件名、路径和响应头在使用前验证。
- 中断、取消和失败必须释放资源。
- 测试聚焦授权、文件不存在、中断、范围请求和资源释放。

正确：授权通过后，根据受控 FileId 打开流。  
错误：直接打开 URL 参数中的本地路径。
