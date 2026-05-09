# CellMind 精简版 - 快速上手指南

## 这套工具能做什么

帮你自动发小红书、知乎、闲鱼。只要配置一次，每天自动跑，省下每天2-3小时重复操作。

---

## 第一步：确认环境

**需要：**
- Windows 10/11 系统
- Microsoft Edge 浏览器（已登录账号）
- Python 3.8+（无Python的先装：https://www.python.org/downloads/）

**检查Python是否安装：**
按 Win+R，输入 `cmd`，回车，输入：
```
python --version
```
看到版本号（如 3.11.x）就说明装了。

---

## 第二步：安装依赖

打开命令行（Win+R → cmd），依次执行：

```
pip install playwright
python -m playwright install chromium
```

安装完成后，验证：
```
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

看到 `OK` 就说明安装成功。

---

## 第三步：获取脚本文件

购买后联系客服（闲鱼私信），获取完整文件包，包含：
- `xiaohongshu_poster.py` - 小红书自动发布脚本
- `zhihu_poster.py` - 知乎自动发布脚本
- `xianyu_publisher.py` - 闲鱼自动发布脚本
- `comment_engagement.py` - 跟帖运营脚本（选配）

---

## 第四步：配置账号

**Edge确保已登录：**
打开 Edge → 登录你的小红书/知乎/闲鱼账号，保持登录状态。

**第一次运行会自动打开浏览器**，请确保Edge没有其他窗口在跑，否则会提示Profile被占用。

---

## 第五步：发第一条

**小红书：**
```
python xiaohongshu_poster.py "你的标题" "你的正文内容"
```

**知乎：**
```
python zhihu_poster.py "你的标题" "你的正文内容"
```

**闲鱼：**
```
python xianyu_publisher.py "商品标题" "商品描述" 35
```

第一次运行会弹出Edge窗口，按照正常发布流程操作一遍。以后再跑就是全自动了。

---

## 常见问题

**Q: 提示 Profile 被占用？**
A: 关掉所有 Edge 窗口后再运行。或者确保只有一个 Edge 实例在跑。

**Q: 显示没登录？**
A: 第一次运行需要 Edge 已登录对应平台账号。登录后再重新运行。

**Q: 能发视频吗？**
A: 当前版本主要支持图文模式。视频需要手动切换标签页。

**Q: 会被平台风控吗？**
A: 使用真实浏览器配置，不是无头模式，Cookie自动保持，风控概率极低。已实测小红书、知乎、闲鱼均可稳定发布。

---

## 进阶：每天定时自动发

配合 Windows 任务计划程序（Task Scheduler），可以每天定时跑：

1. 打开「任务计划程序」
2. 创建基本任务 → 命名如 "CellMind每日发布"
3. 触发器：每天早上9点
4. 操作：启动程序 → 填 `python`，参数填 `E:\CellMind\runtime\xhs_cellmind_01.py`
5. 完成

---

## 技术支持

遇到问题直接闲鱼私信客服，提供截图和错误信息，远程协助帮你跑通。

---

*CellMind 精简体验版 | 一次付费，永久使用*