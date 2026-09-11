# Agent Meme

**给 AI Agent 用的表情包知识库。**

Agent 根据对话语境计算六维情绪向量，从库中匹配最合适的表情包。一次调用完成匹配+日志。

## 核心设计

每个表情包 6 个量化维度（0-1.0）：

| 维度 | 含义 | 来源 |
|------|------|------|
| Valence 效价 | 负面 ↔ 正面 | VAD 心理学 |
| Arousal 唤醒度 | 平静 ↔ 激动 | VAD 心理学 |
| Dominance 支配度 | 弱势 ↔ 强势 | VAD 心理学 |
| Irony 反讽度 | 字面 ↔ 反话 | 表情包定制 |
| Intimacy 亲密度 | 正式 ↔ 死党 | 表情包定制 |
| Aggression 攻击性 | 友善 ↔ 攻击 | 表情包定制 |

Agent 将对话语境量化为 6 维 → **分数 = 0.7 × 余弦相似度 + 0.3 × 标签命中率**（每命中 1 个标签 +0.1，命中 3 个封顶）→ 超阈值即发。

## Agent 使用

```bash
# 一条命令：匹配 + 日志
python3 scripts/match.py --terse --log \
  --context "0.65,0.30,0.55,0.05,0.60,0.00" \
  --keywords "收到,明白,好的" \
  --threshold 0.72 \
  --atmosphere "日常闲聊"

# 输出: cartoon-001|0.8985|assets/cartoon/001-shoudao-xiaoxin.jpg  (命中)
# 输出: null                                                        (未命中)
```

**实测分数区间**（阈值 0.72 时的含义）：命中 3 个标签 ≈ 0.98 · 2 个 ≈ 0.89 · 1 个 ≈ 0.79 · 0 个 ≈ 0.69。
所以阈值 0.72 的实际语义是「**至少命中 1 个标签且向量不跑偏**」，标签覆盖度直接决定召回。

详细说明见 `SKILL.md`。

## 快速开始

### 添加表情包

```bash
python3 scripts/add.py
```

6 步交互，自动追加到 `data/stickers.yaml`。

### 校验

```bash
python3 scripts/validate.py
```

### 编译

```bash
python3 scripts/build.py
# → dist/stickerdex.json     (完整版)
# → dist/stickerdex.min.json (精简版)
```

## 项目结构

```
agent-meme/
├── SKILL.md              # Agent 使用说明
├── schema.yaml           # 字段规范
├── data/stickers.yaml    # 30 个表情包数据
├── assets/{系列}/        # 图片文件
├── scripts/
│   ├── match.py          # 匹配引擎（含日志）
│   ├── add.py            # 交互式新增
│   ├── validate.py       # CI 校验
│   └── build.py          # 编译 stickerdex.json
├── dist/                 # 构建产物
├── logs/                 # 匹配日志
└── .github/workflows/    # PR 自动校验
```

## 贡献

一个表情包 = 一个 PR：

1. 图片放入 `assets/{系列名}/`
2. 运行 `python3 scripts/add.py` 生成元数据
3. 提交 PR，CI 自动校验

## License

MIT
