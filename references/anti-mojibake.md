# 乱码防护细则

Windows 中文环境下改用户的 Word / 文本文件，乱码是最容易翻车的地方。
本文件列出的规则是**硬性要求**，不是建议。

---

## 一、六个风险点与对策

| 风险点 | 对策 |
|---|---|
| 写文件编码不确定 | 一律显式 UTF-8。Python `encoding='utf-8'`；Node `'utf8'`。不依赖系统默认值 |
| Shell 重定向写中文 | **禁用** `echo 中文 > file`、`cat <<EOF`。Git Bash 下必炸。改用 Write 工具或 Python 脚本 |
| 读模板猜错编码 | 先探测：BOM -> UTF-8 -> GBK 回退。用 `scripts/detect_encoding.py` |
| 直接改 docx 内部 XML | **禁止**。正则替换 XML 极易破坏文档结构。统一用 python-docx 按 run / 单元格操作 |
| 终端中文输出 | 跑脚本前置 `PYTHONIOENCODING=utf-8`（Windows PowerShell 可用 `$env:PYTHONIOENCODING='utf-8'`） |
| 写完好坏未知 | **写完必回读校验**：把关键字段读回来比对，确认没变成问号再继续 |

---

## 二、两条保险

1. **动模板前先备份**到 `00-raw/`，改坏了能回滚。
2. **小步写入**：每写一段就校验一次，不要一次性生成整篇再检查。

---

## 三、python-docx 操作要点

**填充段落：按锚点定位，不要整篇替换**

```python
# 正确：找到含锚点的 run，只改那一处
for p in doc.paragraphs:
    if '{{学号}}' in p.text:
        for run in p.runs:
            if '{{学号}}' in run.text:
                run.text = run.text.replace('{{学号}}', student_id)

# 错误：整段重写会丢格式
p.text = p.text.replace('{{学号}}', student_id)
```

**填充表格：定位到单元格，逐 run 处理**

```python
cell = doc.tables[0].cell(row, col)
for p in cell.paragraphs:
    for run in p.runs:
        ...
```

**保留原格式的关键**：只改 `run.text`，不动 `run.font`。
这样字体、字号、颜色、加粗全部保留。

**插入图片**

```python
doc.add_picture(path, width=Inches(5.5))   # 必须指定宽度，否则按原始像素可能撑破页面
```

---

## 四、回读校验的标准动作

写完 docx 后立即：

```python
import docx
d = docx.Document(path)
text = '\n'.join(p.text for p in d.paragraphs)
# 检查1：是否出现替换失败的标志
assert '{{' not in text, '存在未替换的占位符'
# 检查2：是否出现乱码标志
assert '\ufffd' not in text, '检测到 U+FFFD 替换字符，编码已损坏'
# 检查3：关键字段是否还在
assert student_id in text, '学号未写入'
```

三个断言全过才算写成功。

---

## 五、依赖缺失时的提示

不要静默失败。缺 python-docx 时输出：

```
缺少 python-docx，请安装：
  pip install python-docx
```

不要尝试用 zipfile + 正则手工改 docx——那就是乱码的源头。
