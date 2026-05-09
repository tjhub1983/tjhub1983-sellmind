# -*- coding: utf-8 -*-
"""CellMind-Sell 安装脚本
运行此脚本自动安装所有依赖
"""
import subprocess, sys

def install():
    print("Installing CellMind-Sell dependencies...")
    print("=" * 50)

    steps = [
        ("安装 playwright", [sys.executable, "-m", "pip", "install", "playwright", "-q"]),
        ("安装 Chromium 浏览器", [sys.executable, "-m", "playwright", "install", "chromium"]),
    ]

    for name, cmd in steps:
        print(f"\n>>> {name}...")
        try:
            result = subprocess.run(cmd, capture_output=False)
            if result.returncode == 0:
                print(f"  ✅ {name} 完成")
            else:
                print(f"  ⚠️  {name} 遇到问题，继续...")
        except Exception as e:
            print(f"  ❌ 错误: {e}")

    print("\n" + "=" * 50)
    print("安装完成！")
    print("\n快速开始:")
    print("  python scripts/xiaohongshu_poster.py '标题' '正文'")
    print("  python scripts/zhihu_poster.py '标题' '正文'")
    print("  python scripts/xianyu_publisher.py '标题' '描述' 35")
    print("  python scripts/comment_engagement.py")
    print("\n详细文档: docs/CELLMIND_USER_GUIDE.md")

if __name__ == "__main__":
    install()