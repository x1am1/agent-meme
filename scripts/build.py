#!/usr/bin/env python3
"""编译 stickers.yaml → 可发布的 JSON 版本"""

import yaml
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
DATA_FILE = os.path.join(ROOT, "data", "stickers.yaml")
OUTPUT_FILE = os.path.join(ROOT, "dist", "stickerdex.json")
MINIMAL_OUTPUT = os.path.join(ROOT, "dist", "stickerdex.min.json")


def build():
    if not os.path.exists(DATA_FILE):
        print(f"❌ 数据文件不存在: {DATA_FILE}")
        sys.exit(1)

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    stickers = data.get("stickers", [])

    # 完整版
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    full = {
        "meta": {
            "name": "agent-meme",
            "version": "1.0.0",
            "count": len(stickers),
            "built": datetime.utcnow().isoformat() + "Z",
        },
        "stickers": stickers,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=2)

    # 精简版（仅匹配用字段，给 Agent 做向量检索）
    minimal = {
        "meta": {
            "name": "agent-meme",
            "version": "1.0.0",
            "count": len(stickers),
            "built": datetime.utcnow().isoformat() + "Z",
        },
        "stickers": [
            {
                "id": s["id"],
                "vad": s["vad"],
                "irony": s["irony"],
                "intimacy": s["intimacy"],
                "aggression": s["aggression"],
                "tags": s["tags"],
            }
            for s in stickers
        ],
    }
    with open(MINIMAL_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(minimal, f, ensure_ascii=False)

    print(f"✅ 完整版: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")
    print(f"✅ 精简版: {MINIMAL_OUTPUT} ({os.path.getsize(MINIMAL_OUTPUT)} bytes)")
    print(f"   共 {len(stickers)} 个表情包")


if __name__ == "__main__":
    build()
