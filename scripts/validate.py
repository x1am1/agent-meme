#!/usr/bin/env python3
"""校验 stickers.yaml 是否符合 schema 规范 — 给 CI 用的"""

import yaml
import os
import sys
import re

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "stickers.yaml")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_TOP = ["id", "name", "file", "url", "vad", "irony", "intimacy", "aggression", "description", "tags", "context", "intensity", "version"]
REQUIRED_VAD = ["valence", "arousal", "dominance"]
RANGE_0_1 = ["valence", "arousal", "dominance", "irony", "intimacy", "aggression", "intensity"]

errors = []
ids_seen = set()


def err(msg):
    errors.append(msg)
    print(f"  ❌ {msg}")


def main():
    if not os.path.exists(DATA_FILE):
        err(f"数据文件不存在: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not data or "stickers" not in data:
        err("缺少 stickers 根键")
        sys.exit(1)

    stickers = data["stickers"]
    print(f"共 {len(stickers)} 个表情包\n")

    for i, s in enumerate(stickers):
        sid = s.get("id", f"#{i+1}")
        prefix = f"[{sid}]"

        # 去重
        if sid in ids_seen:
            err(f"{prefix} ID 重复")
        ids_seen.add(sid)

        # 必填字段
        for key in REQUIRED_TOP:
            if key not in s:
                err(f"{prefix} 缺少必填字段: {key}")

        # VAD
        vad = s.get("vad", {})
        for key in REQUIRED_VAD:
            if key not in vad:
                err(f"{prefix} vad 缺少: {key}")

        # 范围检查
        for key in RANGE_0_1:
            val = None
            if key in ["valence", "arousal", "dominance"]:
                val = vad.get(key)
            elif key in s:
                val = s[key]
            if val is not None and not (0.0 <= val <= 1.0):
                err(f"{prefix} {key}={val} 超出 0-1.0")

        # ID 格式
        if not re.match(r"^[a-z0-9-]+$", str(sid)):
            err(f"{prefix} ID 格式非法: {sid}")

        # 标签数量
        tags = s.get("tags", [])
        if len(tags) < 3:
            err(f"{prefix} tags 至少 3 个，当前 {len(tags)}")
        if len(tags) > 15:
            err(f"{prefix} tags 最多 15 个，当前 {len(tags)}")

        # 场景数量
        ctx = s.get("context", [])
        if len(ctx) < 2:
            err(f"{prefix} context 至少 2 个，当前 {len(ctx)}")

        # 描述长度
        desc = s.get("description", "")
        if len(desc) > 200:
            err(f"{prefix} description 超 200 字: {len(desc)}")

        # URL 格式
        url = s.get("url", "")
        if url and not url.startswith(("http://", "https://")):
            err(f"{prefix} URL 格式错误: {url}")

        # 文件引用
        file_path = s.get("file", "")
        if file_path:
            full_path = os.path.join(ROOT, file_path)
            # 不检查文件是否存在（图片可能还没提交）

    print(f"\n{'='*40}")
    if errors:
        print(f"❌ {len(errors)} 个错误")
        sys.exit(1)
    else:
        print(f"✅ 全部通过 — {len(stickers)} 个表情包")


if __name__ == "__main__":
    main()
