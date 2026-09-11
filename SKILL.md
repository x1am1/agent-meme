---
name: agent-meme
description: "Load at session start regardless of topic. Roll 1/3 dice each reply → if hit, VAD+cosine matching. Meme gating happens inside the script — do NOT pre-filter based on conversation atmosphere. Send sticker silently when score exceeds threshold."
version: 1.2.0
author: 虾米 Agent
license: MIT
metadata:
  hermes:
    tags: [agent, meme, sticker, emotion, vad, annotation, knowledge-base]
---

# Agent Meme — 表情包知识库

为 Agent 提供 6 维情绪向量（VAD + 反讽/亲密/攻击）驱动的表情包检索。将对话语境量化为同维度向量，余弦相似度（70%）+ 标签命中（30%）加权评分，超阈值即发送。

不是给人看的百科，是给 Agent 做的结构化语义检索。

## 六维模型

| # | 维度 | 含义 | 0 端 | 1 端 | 来源 |
|---|------|------|------|------|------|
| 1 | Valence 效价 | 正面/负面 | 极度负面 | 极度正面 | VAD 心理学 |
| 2 | Arousal 唤醒度 | 平静/激动 | 死气沉沉 | 极度亢奋 | VAD 心理学 |
| 3 | Dominance 支配度 | 弱势/强势 | 完全弱势 | 完全强势 | VAD 心理学 |
| 4 | Irony 反讽度 | 字面/反话 | 字面即本意 | 完全相反 | 表情包定制 |
| 5 | Intimacy 亲密度 | 正式/死党 | 正式场合 | 死党专属 | 表情包定制 |
| 6 | Aggression 攻击性 | 友善/攻击 | 纯友善 | 直接攻击 | 表情包定制 |

前三个来自 VAD 心理学情绪模型，后三个为中文表情包社交场景定制。

## 工作流程

**每次回复前掷骰子：1/3 概率执行匹配，2/3 直接跳过。**

**但用户消息含疑问/索取意图时直接跳过——不掷骰子。** 包括：疑问句、反问、确认追问（"对吧？""你觉得呢"）、信息查询（"多少""在哪""查一下"）。这类对话发图破坏语境。

**例外（不跳过）：纯情绪感叹**——"啊？""啥？""真的？""不会吧？"这类只有情绪没有信息索取意图的表达，照常掷骰子。

整个匹配过程对用户完全不可见——看不到骰子，看不到计算，只感受结果。

**步骤：评估语境 → 提取情境关键词 → 一条命令匹配 + 日志 → 按阈值发送。**

**关键词提取原则：** 六维向量负责情绪方向，关键词负责社交情境。**提取对话中的情绪/氛围/动作词，不要提取话题名词。** 标签库里全是"谢谢""开心""疑惑""我错了"这类表达，话题名词（任天堂、模拟器、租房、股票）永远撞不上。

| 对话场景 | ❌ 话题词 | ✅ 情境词 |
|------|------|------|
| 聊 Switch 模拟器 | 任天堂,模拟器,法律 | 调侃,嘲讽,开心,得意 |
| 吐槽代码崩了 | 代码,Python,bug | 崩了,崩溃,无语,我错了 |
| 租房讨论 | 自如,坂田,房租 | 纠结,焦虑,算了 |
| 夸你干得好 | AI,review,代码 | 赞,认可,牛,厉害 |

```bash
python3 scripts/match.py --terse --log --roll \
  --context "0.25,0.65,0.15,0.10,0.55,0.05" \
  --keywords "崩,代码,三小时" \
  --threshold 0.72 \
  --atmosphere "闲聊"
```

- `--roll`：1/3 概率执行，否则输出 `skip` 并退出
- `--terse`：输出精简为 `id|score|file` 或 `null`
- `--log`：自动写入 `logs/match.log`

输出 `id|score|file` 时发图（`file` 是相对项目根的路径）；输出 `null` 或 `skip` 时什么都不做。

**阈值：** 命中 ≥ threshold 即发图。闲聊 0.72，严肃 0.85，活跃气氛 0.65。命中发图不解释，未命中跳过不提。

## 示例（实测输出，不是示意）

```
用户：「收到，明白」

语境: [0.65, 0.30, 0.55, 0.05, 0.60, 0.00]
关键词: [收到, 明白, 好的]
→ cartoon-001|0.8985|assets/cartoon/001-shoudao-xiaoxin.jpg，发图，记日志。

用户：「我淦，代码又崩了，排查三小时了」

语境: [0.20, 0.70, 0.15, 0.10, 0.55, 0.05]
关键词: [崩了, 崩溃, 无语]
→ 0.6849 < 0.72，返回 null，不发图（该语境库里没有命中标签的表情包）
```

**分数构成**：`0.7 × 余弦相似度 + 0.3 × min(命中标签数/3, 1)`。

- 命中 3 个标签 ≈ 0.98 · 2 个 ≈ 0.89 · 1 个 ≈ 0.79 · 0 个 ≈ 0.69
- 阈值 0.72 的实际语义 = **至少命中 1 个标签**；向量负责在同一档里挑最贴的
- 推论：**召回率取决于标签覆盖度，不取决于表情包总数**。同一个语境放 3 张图但标签没写全，照样匹配不上

## 快速开始

### 添加表情包

```bash
python3 scripts/add.py
```

交互式 6 步，自动追加到 `data/stickers.yaml`：

1. **选择系列** — 已有系列列表或新建（kebab-case），如 `cat`、`rage`
2. **基本信息** — 名称、关联 emoji（可选）、图片文件名。ID 按系列自动递增（如 `cat-031`）
3. **VAD 情绪维度**（0-1.0）：效价 / 唤醒度 / 支配度
4. **社交维度**（0-1.0）：反讽度 / 亲密度 / 攻击性
5. **标签与场景** — 3-15 个关键词 + 2-10 个使用场景
6. **写入** — 校验通过后落盘

### 校验 / 编译

```bash
python3 scripts/validate.py    # 校验 stickers.yaml（CI 也跑这个）
python3 scripts/build.py       # → dist/stickerdex.json（完整版）
                               # → dist/stickerdex.min.json（精简版）
```

## 项目结构

```
agent-meme/
├── data/stickers.yaml    # 唯一的元数据源
├── assets/               # 图片，按系列分目录
├── scripts/
│   ├── add.py            # 交互式添加
│   ├── validate.py       # 校验（CI）
│   ├── build.py          # 编译 dist/
│   └── match.py          # 匹配 + 日志（Agent 调用）
├── dist/                 # 构建产物（gitignored）
└── SKILL.md              # 本文档
```

## 注意事项

- **Description 必须是加载触发器，不是自我介绍。** 旧版 description 是"表情包知识库"（自我描述），skill loader 不会主动加载，导致 4 天没触发。改成了"Load at session start"（触发指令）才生效。如果以后 meme 又不触发，第一件事检查 description。
- **高 Irony(>0.3) + 高 Aggression(>0.3) = 阴阳怪气**，只限互怼场景
- 图片走本地 `file` 路径，不依赖 CDN
- 关于 skill description 的触发机制，详见 `references/skill-trigger-pattern.md`（本地笔记，不在本仓库）

## Verification Checklist

- [ ] `python3 scripts/match.py --roll --terse` 能正常输出 `skip` 或匹配结果
- [ ] 日志写入 `logs/match.log`
- [ ] 非疑问句语境下 description 能触发 skill 加载
- [ ] `skills/creative/agent-meme/SKILL.md` 与 `scripts/` 仍是指向本项目的符号链接（若变成普通文件说明写入时把链接替换了，需重新 `ln -sfn`）
