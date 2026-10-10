# Playbook 模板（复制此文件到 .local/playbooks/ 后填写）

> 存放位置：`.local/playbooks/<课程>-<实验名>.md`（不上传 Git）
> 生成方式：阶段 8 复盘后自动回写，或手工填写
> 字段说明见 `references/experience-reuse.md` 第 6 节

---

```yaml
id: netsec-aes
identity:
  school: 重庆理工大学
  course: 网络安全
  name: AES 加解密
fingerprint:
  tools: [python, pycryptodome]
  libs: [pycryptodome]
  steps: 6
  outputs: [终端输出, 截图]
  section_titles_hash: a3f9c1
env:
  os: Windows 11
  toolchain: Python 3.11
preconditions:
  - Python 3.11（3.13 装不上 pycryptodome）
  - pycryptodome 已安装
estimated_time: 41min
owner: joes133
recorded: 2026-03-14
last_verified: 2026-09-02
reuse_count: 4
source: verified-twice
confidence: high
```

---

## 步骤

| # | 操作 | 预期结果 | 必须截图 | 耗时 |
|---|---|---|---|---|
| 1 | | | 否 | |
| 2 | | | 是 | |
| 3 | | | 是 | |

## 坑位

格式：**症状 -> 原因 -> 修复**

1. **症状**：
   **原因**：
   **修复**：

2. **症状**：
   **原因**：
   **修复**：

## 回滚

环境搞脏后如何回到干净状态：

```bash
git checkout .
make clean
```

## 报告结构

| 栏目 | 占比 | 备注 |
|---|---|---|
| 实验目的 | 10% | |
| 实验步骤 | 30% | |
| 结果分析 | 40% | 老师最看重这部分 |
| 心得体会 | 20% | |

## 必截图点

- step-02-密钥生成
- step-05-解密结果对比
