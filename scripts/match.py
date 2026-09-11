#!/usr/bin/env python3
"""匹配 + 日志：给定语境向量 + 关键词，返回最佳表情包并自动记录。

用法:
  # 完整 JSON（给人看/调试）
  python3 match.py --context "0.6,0.3,0.55,0.0,0.5,0.0" --keywords "谢谢,开心"

  # 精简输出 + 自动日志（Agent 用，~15 token）
  python3 match.py --terse --log \
    --context "0.6,0.3,0.55,0.0,0.5,0.0" \
    --keywords "谢谢,开心" \
    --threshold 0.80 \
    --atmosphere "日常闲聊"
"""

import yaml, math, json, argparse, os, sys, random
from datetime import datetime, timezone, timedelta

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(SKILL_DIR, "data", "stickers.yaml")
LOG_DIR = os.path.join(SKILL_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "match.log")
TZ = timezone(timedelta(hours=8))

DIM_ORDER = ["valence", "arousal", "dominance", "irony", "intimacy", "aggression"]


def load_stickers():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["stickers"]


def sticker_vector(s):
    v = s.get("vad", {})
    return [
        v.get("valence", 0.5),
        v.get("arousal", 0.5),
        v.get("dominance", 0.5),
        s.get("irony", 0.0),
        s.get("intimacy", 0.5),
        s.get("aggression", 0.0),
    ]


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def match(context_vector, keywords, stickers, threshold=0.80, top=5):
    results = []
    for s in stickers:
        sv = sticker_vector(s)
        vector_score = cosine(context_vector, sv)
        tags = s.get("tags", [])
        tag_hits = len(set(k.lower() for k in keywords) & set(t.lower() for t in tags))
        semantic_score = min(tag_hits / 3, 1.0)
        final_score = vector_score * 0.70 + semantic_score * 0.30
        results.append({
            "score": round(final_score, 4),
            "id": s["id"],
            "name": s["name"],
            "file": s["file"],
            "description": s.get("description", ""),
            "vector_score": round(vector_score, 4),
            "semantic_score": round(semantic_score, 4),
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    top_n = results[:top]
    best = top_n[0] if top_n and top_n[0]["score"] >= threshold else None

    return {"match": best, "candidates": top_n}


def write_log(context_vector, keywords, threshold, atmosphere, best, top_score=0):
    entry = {
        "ts": datetime.now(TZ).isoformat(timespec="seconds"),
        "context": {k: v for k, v in zip(DIM_ORDER, context_vector)},
        "keywords": keywords,
        "threshold": threshold,
        "atmosphere": atmosphere,
        "match_id": best["id"] if best else None,
        "match_score": best["score"] if best else top_score,
        "sent": best is not None,
    }
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Agent Meme 表情包匹配")
    parser.add_argument("--context", required=True, help="逗号分隔6维: v,a,d,i,int,agg")
    parser.add_argument("--keywords", default="", help="逗号分隔关键词")
    parser.add_argument("--threshold", type=float, default=0.80)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--terse", action="store_true", help="精简输出: id|score|file 或 null")
    parser.add_argument("--log", action="store_true", help="自动写入 logs/match.log")
    parser.add_argument("--atmosphere", default="日常闲聊", help="氛围标签（配合 --log）")
    parser.add_argument("--roll", action="store_true", help="1/3 概率执行匹配，否则输出 skip 并退出")

    args = parser.parse_args()

    # 随机骰子：1/3 概率继续，否则跳过
    if args.roll and random.randint(1, 3) != 1:
        if args.log:
            entry = {"ts": datetime.now(TZ).isoformat(timespec="seconds"), "rolled": "skip", "sent": False}
            os.makedirs(LOG_DIR, exist_ok=True)
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        print("skip")
        sys.exit(0)
    context = [float(x.strip()) for x in args.context.split(",")]
    if len(context) != 6:
        print(json.dumps({"error": "context 需要6个数值"}, ensure_ascii=False))
        sys.exit(1)

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    stickers = load_stickers()
    result = match(context, keywords, stickers, args.threshold, args.top)

    if args.log:
        top_score = result["candidates"][0]["score"] if result["candidates"] else 0
        write_log(context, keywords, args.threshold, args.atmosphere, result["match"], top_score)

    if args.terse:
        m = result["match"]
        if m:
            print(f"{m['id']}|{m['score']}|{m['file']}")
        else:
            print("null")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
