#!/usr/bin/env python3
"""交互式新增表情包 — 按提示输入即可，自动生成 YAML 条目并追加到 stickers.yaml"""

import yaml
import os
import sys
import re
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "stickers.yaml")
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")


def ask(prompt, default=None, validator=None):
    """带默认值的交互式输入"""
    if default:
        p = f"{prompt} [{default}]: "
    else:
        p = f"{prompt}: "
    while True:
        val = input(p).strip()
        if not val and default:
            val = default
        if not val:
            print("  ⚠ 不能为空")
            continue
        if validator and not validator(val):
            continue
        return val


def ask_num(prompt, lo=0.0, hi=1.0, default=None):
    """输入 0-1.0 的数值"""
    while True:
        val = ask(prompt, default=str(default) if default is not None else None)
        try:
            n = float(val)
            if lo <= n <= hi:
                return round(n, 2)
            print(f"  ⚠ 范围 {lo}-{hi}")
        except ValueError:
            print("  ⚠ 请输入数字")


def ask_list(prompt, min_items=1):
    """输入逗号分隔的列表"""
    items = []
    print(f"\n{prompt}（逗号分隔，至少 {min_items} 个，空行结束）:")
    while True:
        line = input("  ").strip()
        if not line:
            if len(items) >= min_items:
                break
            print(f"  还需要至少 {min_items - len(items)} 个")
            continue
        items.extend([x.strip() for x in line.split(",") if x.strip()])
        if len(items) >= min_items:
            print(f"  已输入 {len(items)} 个，继续添加或回车结束")
    return items


def pick_series():
    """选择或创建系列"""
    existing = []
    if os.path.isdir(ASSETS_DIR):
        existing = [d for d in os.listdir(ASSETS_DIR) if os.path.isdir(os.path.join(ASSETS_DIR, d)) and not d.startswith(".")]

    print("\n现有系列:")
    for i, s in enumerate(existing, 1):
        print(f"  {i}. {s}")
    print(f"  n. 新建系列")

    choice = ask("选择系列 (1-{})".format(len(existing)), default=None)
    if choice.lower() == "n":
        name = ask("系列名 (kebab-case)", validator=lambda x: bool(re.match(r"^[a-z0-9-]+$", x)))
        os.makedirs(os.path.join(ASSETS_DIR, name), exist_ok=True)
        return name

    try:
        idx = int(choice) - 1
        return existing[idx]
    except (ValueError, IndexError):
        print("  无效选择，请输入数字")
        return pick_series()


def get_next_id(series):
    """获取系列下一个序号"""
    data = load_data()
    max_n = 0
    prefix = f"{series}-"
    for s in data.get("stickers", []):
        sid = s.get("id", "")
        if sid.startswith(prefix):
            try:
                n = int(sid.split("-")[-1])
                max_n = max(max_n, n)
            except (ValueError, IndexError):
                pass
    return f"{prefix}{max_n + 1:03d}"


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"stickers": []}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write(
            "# Agent Meme — 表情包数据集\n"
            "# 维基式维护，一条 PR 一个表情包\n"
            "# 图片文件放在 assets/{系列名}/ 下\n\n"
        )
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)


def main():
    print("=" * 50)
    print("  Agent Meme — 新增表情包")
    print("=" * 50)

    # 1. 系列
    series = pick_series()
    sticker_id = get_next_id(series)
    print(f"\n  ID 自动分配: {sticker_id}")

    # 2. 基本信息
    print("\n--- 基本信息 ---")
    name = ask("名称")
    emoji = ask("关联 emoji", default="", validator=lambda x: True)

    file_path = ask("图片文件名", default=f"{sticker_id.split('-')[-1]}-{name}.gif")
    file_path = f"assets/{series}/{file_path}"
    url = ask("CDN URL（留空自动生成 jsDelivr）", default="")
    if not url:
        url = f"https://cdn.jsdelivr.net/gh/agent-meme/agent-meme/{file_path}"

    # 3. VAD 维度
    print("\n--- VAD 情绪维度 (0-1.0) ---")
    valence = ask_num("  Valence 效价 (0=负面, 1=正面)", default=0.5)
    arousal = ask_num("  Arousal 唤醒度 (0=平静, 1=亢奋)", default=0.5)
    dominance = ask_num("  Dominance 支配度 (0=弱势, 1=强势)", default=0.5)

    # 4. 社交维度
    print("\n--- 社交维度 (0-1.0) ---")
    irony = ask_num("  Irony 反讽度 (0=字面, 1=完全相反)", default=0.0)
    intimacy = ask_num("  Intimacy 亲密度 (0=正式, 1=死党)", default=0.5)
    aggression = ask_num("  Aggression 攻击性 (0=友善, 1=攻击)", default=0.0)

    # 5. 语义
    print("\n--- 语义描述 ---")
    desc = ask("画面描述 (一句话)")
    tags = ask_list("标签", min_items=3)
    ctx = ask_list("适用场景", min_items=2)
    persona = ask_list("适合人设（可选，空行跳过）", min_items=0)

    intensity = ask_num("\nIntensity 力度 (0=微表情, 1=极度夸张)", default=0.5)

    # 6. 构建条目
    entry = {
        "id": sticker_id,
        "name": name,
        "file": file_path,
        "url": url,
        "vad": {
            "valence": valence,
            "arousal": arousal,
            "dominance": dominance,
        },
        "irony": irony,
        "intimacy": intimacy,
        "aggression": aggression,
        "description": desc,
        "tags": tags,
        "context": ctx,
        "intensity": intensity,
        "version": 1,
    }
    if emoji:
        entry["emoji"] = emoji
    if persona:
        entry["persona"] = persona

    # 7. 确认
    print("\n" + "=" * 50)
    print(yaml.dump(entry, allow_unicode=True, default_flow_style=False, sort_keys=False))
    print("=" * 50)

    confirm = ask("确认追加到 stickers.yaml? (y/N)", default="n")
    if confirm.lower() != "y":
        print("已取消")
        return

    data = load_data()
    data.setdefault("stickers", []).append(entry)
    save_data(data)
    print(f"✅ 已追加 {sticker_id} — {name}")
    print(f"   请将图片文件放入: {file_path}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\n已取消")
        sys.exit(0)
