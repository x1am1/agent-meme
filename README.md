# Agent Meme

**给 AI Agent 用的表情包知识库。**

Agent 根据对话语境计算六维情绪向量，从库中匹配最合适的表情包。不是给人看的百科，是给 Agent 做的结构化语义检索。

## 核心设计

每个表情包 6 个量化维度（0-1.0）：

| 维度 | 含义 | 来源 |
|------|------|------|
| Valence 效价 | 正面 ↔ 负面 | VAD 心理学模型 |
| Arousal 唤醒度 | 平静 ↔ 激动 | VAD 心理学模型 |
| Dominance 支配度 | 弱势 ↔ 强势 | VAD 心理学模型 |
| Irony 反讽度 | 字面 ↔ 反话 | 表情包定制 |
| Intimacy 亲密度 | 正式 ↔ 死党 | 表情包定制 |
| Aggression 攻击性 | 友善 ↔ 攻击 | 表情包定制 |

Agent 将当前对话语境量化为 6 个数值 → 与库中表情包做余弦相似度匹配 → 得分超过阈值就发。

## 快速开始

### 添加表情包

```bash
python3 scripts/add.py
```

交互式输入，自动追加到 `data/stickers.yaml`。

### 校验数据

```bash
python3 scripts/validate.py
```

### 编译发布

```bash
python3 scripts/build.py
# → dist/stickerdex.json     (完整版)
# → dist/stickerdex.min.json (精简版，仅向量+标签)
```

## 项目结构

```
agent-meme/
├── SKILL.md              # Agent 使用说明
├── schema.yaml            # 字段规范
├── data/
│   └── stickers.yaml      # 所有表情包数据
├── assets/                # 图片/动图（按系列分目录）
├── scripts/
│   ├── add.py             # 交互式新增
│   ├── validate.py        # 校验（CI 用）
│   └── build.py           # 编译 JSON
└── dist/                  # 构建产物（gitignore）
```

## 贡献

一个表情包 = 一个 PR。新增：

1. 图片放入 `assets/{系列名}/`
2. 运行 `python3 scripts/add.py` 生成元数据
3. 提交 PR，CI 自动校验

## License

MIT
