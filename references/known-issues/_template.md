# 坑位库模板

> **公开区**（`references/known-issues/common/`）：按**工具**组织，不含学校/老师信息，可上传
> **私有区**（`.local/known-issues/`）：按**课程**组织，含个人信息，不上传

判定方法：报错信息里不含课程专有名词 -> 归为通用坑位，可公开。

---

## 条目格式

### <一句话症状>

- **环境**：Windows 11 / Python 3.13
- **现象**：
  ```
  <原始报错信息>
  ```
- **原因**：
- **修复**：
- **验证**：修复后如何确认真的好了
- **记录**：2026-03-14 / joes133 / 复用 2 次

---

## 示例（通用坑位，可公开）

### pycryptodome 在 Python 3.13 下编译失败

- **环境**：Windows 11 / Python 3.13
- **现象**：
  ```
  error: Microsoft Visual C++ 14.0 is required
  ```
- **原因**：3.13 还没有对应的预编译 wheel，需要本地编译
- **修复**：降级到 Python 3.11，或安装 pycryptodomex
- **验证**：`python -c "from Crypto.Cipher import AES; print('ok')"`
- **记录**：2026-03-14 / joes133 / 复用 3 次
