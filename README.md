# labrunner

**Don't fake it. Run it.**
实验不只写在纸上，要真的跑起来。

An agent skill for lab coursework: it reads your assignment docs,
really runs the experiment step by step, captures screenshots as evidence,
and fills in your report template.

---

## 它解决什么

labmate ——报告->文字。
labrunner ——先把实验**真的跑一遍**，再据实写报告。

| labrunner |
|---|
| 明确的工作流程 |
| 在真实环境里执行每一步 |
| 运行结果是真跑出来的 |
| 截图是它自己截的 |
| 跑不通就降级并明确告诉你 |
| 扩展... |


---

## 工作流程

```
阶段 0  收资料       登记你给的 PDF / Word / 图片 / 文本
阶段 0.5 申请存储    告知用途与预估占用，和你确认产物放哪
阶段 1  体检         核对齐全性与矛盾，产出《待确认清单》
阶段 2  对齐         你补齐资料、裁决冲突
阶段 2.5 经验匹配    （开发中）
阶段 3  定档         强制询问：质量档（高/中/低）+ 执行模式（A/B/C）
阶段 4  环境与权限   申请权限、探测环境、判定截图能力、冒烟测试
阶段 5  学号姓名     模板有就填，没有就跳过
阶段 6  执行         跑一步 -> 截一张 -> 再跑下一步，全程记账
阶段 7  交付         填模板 -> 回读校验 -> 打包
阶段 8  复盘         时间账本 + 复盘总结（）
```

**核心红线**

- 事先与你核对好文件，避免歧义和冲突
- 不编造运行结果。跑不出来就如实降级并告知
- 不破坏你的原始文件。所有原件先备份到 `00-raw/`
- 高危操作停下来问：删原文件、联网提交、装系统软件、产生费用
- 写文件一律 UTF-8，写完必回读校验，绝不给你一份乱码的报告

---

## 安装

### Windows（PowerShell）

```powershell
git clone https://github.com/joes133/labrunner.git
cd labrunner
.\install.ps1
```

### macOS / Linux

```bash
git clone https://github.com/joes133/labrunner.git
cd labrunner
chmod +x install.sh && ./install.sh
```

### 支持哪些 agent

`SKILL.md` 用的是开放的 Agent Skills 标准，同一份文件在各家通用，
区别只有**装到哪个目录**。

```powershell
.\install.ps1 -List             # 看看支持哪些（* 号 = 你机器上已装）
.\install.ps1                   # 默认只装 WorkBuddy
.\install.ps1 -Client claude    # 明确指定装到某一个
```

默认只装 WorkBuddy——labrunner 不往你没点名的目录里写东西。
要用别的客户端，`-Client` 显式指一下就行。

| 客户端 | 安装位置 | 备注 |
|---|---|---|
| WorkBuddy / CodeBuddy | `~/.workbuddy/skills/labrunner` | 主要开发环境 |
| Claude Code | `~/.claude/skills/labrunner` | 完整支持 |
| Cursor | `~/.cursor/skills/labrunner` | 完整支持 |
| Codex CLI | `~/.codex/skills/labrunner` | 完整支持 |
| OpenCode / Cline / Gemini CLI | `~/.agents/skills/labrunner` | 完整支持 |
| Kiro | `~/.kiro/agents/labrunner` | 完整支持 |
| Trae / 豆包 | — | 暂无兼容标准，需手动把 `SKILL.md` 内容贴作系统提示 |

### 依赖

```bash
pip install pillow python-docx chardet
# Windows 上需要自动定位窗口，额外装：
pip install pywin32
```

缺少依赖时脚本会给出安装提示，不会静默失败。

**平台差异**：窗口定位（`capture.py`）依赖 Windows + pywin32。
macOS / Linux 上会自动降级为全屏截图，其余功能不受影响。

---

## 使用

在支持 skill 的 agent 里，直接说：

```
帮我做这个实验            （然后附上资料）
写实验报告
跑一下这次的实验作业
```

也可以直接用斜杠命令唤起（补全时会显示 `/labrunner [实验资料路径]`）：

```
/labrunner
```

它会先核对资料是否齐全、有没有互相矛盾的地方，
跟你确认产物要存到哪、要什么质量档，然后申请环境权限，跑起来。

**产出目录**

```
outputs/<课程>-<实验名>-<日期>/
  00-raw/       原始资料副本（只读）
  01-work/      脚本、日志、timeline.md、frictions.md
  02-shots/     截图 step-<序号>-<说明>.png
  03-report/    最终报告
```

---

## 质量档与执行模式

**质量档**

| 档 | 图片 | 水印 |
|---|---|---|
| 高 | 关键步骤 + 结果必配 | 有（学号姓名） |
| 中 | 按需 | 无 |
| 低 | 无 | 无 |

**执行模式**

| 模式 | 说明 |
|---|---|
| A 全自动真图 | 本机 GUI / 虚拟机窗口可控，自动定位截图 |
| B 协作真图 | 云端 / 远程环境，它出《请截图清单》，你配合截 |
| C 无图文字 | 放弃截图，用文字 + 命令输出 |

任何档位都会真实执行。跑不通就降级，并且会明确告诉你降级在哪一步。

---

## 目录结构

```
labrunner/
  SKILL.md                     主指令（流程 + 红线）
  scripts/
    detect_encoding.py         编码探测与安全读取
    capture.py                 窗口定位 / 置前 / 截图（含 DPI 修正）
    watermark.py               高质量档水印
    fill_docx.py               按占位符填模板 + 回读校验
  references/
    quality-matrix.md          定档判定细则
    anti-mojibake.md           乱码防护细则
    experience-reuse.md        经验复用模块设计（已定稿，未实现）
    playbooks/                 攻略模板（null）
    known-issues/              坑位库模板（null）
  .local/                      个人配置（不上传 Git）
```

---

## Roadmap

- [ ] **经验复用**：跑完自动沉淀攻略（坑位 / 节奏 / 环境），
      下次跑同类实验时可选择加载，省一半时间。
      设计已定稿，见 `references/experience-reuse.md`，暂未开发。

---

## 关于学术诚信

labrunner 帮你**执行**实验和**整理**报告，不替你编造结果。
它不会生成可直接提交的成品答案——所有的运行结果都来自真实执行，
报告内容都基于你提供的资料和真实产出的证据。

用它可以省下重复劳动的时间，但实验本身还是要你理解。

---

## License

MIT
