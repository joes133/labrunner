# 经验索引

> 当前为空。经验匹配模块尚未实现（见 `references/experience-reuse.md`）。
> 未来启用后，本文件列出所有可用 playbook 的匹配元数据，
> 供阶段 2.5 做三层匹配（L1 身份 / L2 指纹 / L3 环境）。

## 格式

```yaml
- id: netsec-aes
  identity: { school: ..., course: ..., name: ... }
  fingerprint: { tools: [...], steps: N, outputs: [...] }
  env: { os: ..., toolchain: ... }
  last_verified: 2026-09-02
  reuse_count: 4
  confidence: high
  file: .local/playbooks/netsec-aes.md
```

## 条目

（暂无）
