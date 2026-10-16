# 攻略：在 VirtualBox NAT 网络里做扫描实验（vbox-nat-scan）

> 适用场景：网安课设/实验要求扫描 VirtualBox NAT 网段（如 10.0.2.0/24）内的靶机，
> 而 NAT「只出不进」，宿主机（脚本运行处）无法直达网段内 VM。
> 本攻略在 2026-10-14 实验二首次跑通，全部步骤为真实执行记录。

## 1. 先确认事实，不要想当然

```bash
# 列出所有 VM 与网卡模式
VBoxManage showvminfo "<VM名>" | grep -iE "State|NIC [0-9]"
# 列出 NAT 网络与网段
VBoxManage list natnets          # 确认 DHCP 开启与网段（默认 10.0.2.0/24）
# 实测宿主机可达性（预期失败——这就是根因）
ping -n 2 -w 1500 10.0.2.1       # 100% 丢包 = NAT 隔离确认
```

关键认知：**NAT 网络里 VM 之间能互访、VM 能上外网，但宿主机到不了任何 VM**。
所以「从宿主机跑 nmap 扫靶机」在 NAT 下天生走不通，这不是配置错误，是模式特性。

## 2. 推荐方案：扫描平台放进网段内（不破坏 NAT 组网）

思路：在 NAT 网段内的 Kali 里执行 nmap，宿主机通过 **VBox guestcontrol 通道**
（VirtualBox 内部通道，不经网络）下发命令并回收输出。

### 2.1 下发命令（宿主机执行）

```bash
VBoxManage guestcontrol "<Kali VM名>" run --username kali --password kali \
  --exe /bin/bash -- -c "echo kali | sudo -S nmap -sn 10.0.2.0/24"
```

- `run` 的 stdout/stderr 经通道回传宿主机，直接重定向落盘就是真实证据；
- 提权用 `echo <密码> | sudo -S`（guestcontrol 无 tty，不能交互输密码）。

### 2.2 两段式扫描（先发现后深扫）

```bash
# 第一段：主机发现（快，~2s）
nmap -sn 10.0.2.0/24
# 第二段：对存活主机逐个深扫（慢，网关约 168s / 靶机约 14s）
nmap -sS -sV -O -T4 10.0.2.3
```

### 2.3 输出回收

方式 A（稳）：stdout 重定向到宿主机文件，天然真实。
方式 B：Kali 内写文件再 `guestcontrol copyfrom` 回传——**有坑**：
sudo 生成的文件属主是 root，kali 会话读不到；且本环境 copyfrom 偶发
`VERR_GENERAL_FAILURE`。若必须用，脚本里 `chown -R kali:kali` + `chmod -R 666`。
**结论：优先方式 A。**

## 3. 已踩过的坑（按踩雷顺序）

| # | 坑 | 结论 |
|---|---|---|
| 1 | 给 Kali/Metasploitable2 配 NAT 端口转发（natpf1）后宿主机 SSH 仍连不上 | Kali 的 sshd 默认不随桌面自启；端口转发可用但服务未必在。别在 sshd 上死磕 |
| 2 | 建议用户把 VM 改成 Host-Only 网络 | 错误建议：网安课设就是 NAT 组网，不该动。先问用户环境约定，再提方案 |
| 3 | guestcontrol copyfrom 报 VERR_GENERAL_FAILURE | 属主/权限问题 + VBox 已知坑，改用 stdout 回收 |
| 4 | Kali 桌面截屏只拍到黑屏/锁屏 | 屏保休眠：`VBoxManage controlvm <VM> keyboardputscancode 1c` 唤醒；锁屏用 `loginctl unlock-sessions` 解锁 |
| 5 | qterminal 窗口开了但截图里是透明的、看不到文字 | VirtualBox 3D 合成下 qterminal 的半透明窗口在截图帧缓冲里不渲染。文本控制台（如 Metasploitable2 的 tty）截图反而可靠，但会遇屏幕休眠黑屏 |
| 6 | 中文路径 + sudo 输出混杂 `[sudo] password` 行 | 落盘前 `grep -v '^\[sudo\]'`；宿主机脚本统一 `PYTHONIOENCODING=utf-8` |

## 4. 拿不到"终端运行截图"怎么办（卡壳即停）

若 VM 桌面的真实终端截图因渲染问题拿不到（第 5 条坑），按 skill 的「卡壳即停」规则：
明确告知用户卡在哪、缺什么、需要他做什么、报告会缺哪块，把决策权交回。
**不要**用渲染图冒充真实截图。可接受的替代证据：
- 真实命令 + 真实原始输出文本（stdout 落盘件）进报告代码节；
- 用真实数据绘制的浅色系文档图（拓扑图/流程图），标注"数据来源：nmap 实测"。

## 5. 一页速查

```bash
VBM="C:/Program Files/Oracle/VirtualBox/VBoxManage.exe"
# 跑命令（在 Kali 内）
"$VBM" guestcontrol "<VM>" run --username kali --password kali --exe /bin/bash -- -c "<命令>"
# 唤醒/解锁桌面
"$VBM" controlvm "<VM>" keyboardputscancode 1c
"$VBM" guestcontrol "<VM>" run --username kali --password kali --exe /bin/bash -- -c "echo kali | sudo -S loginctl unlock-sessions"
# 截屏
"$VBM" controlvm "<VM>" screenshotpng <输出.png>
```
