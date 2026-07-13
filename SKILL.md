---
name: agent-meme
description: "Structured sticker/meme knowledge base for AI Agents. 6-dimension VAD+social emotion annotation, cosine similarity matching, threshold-gated delivery."
version: 1.0.0
author: 虾米 Agent
license: MIT
metadata:
  hermes:
    tags: [agent, meme, sticker, emotion, vad, annotation, knowledge-base]
---

# Agent Meme — 表情包知识库

为 AI Agent 提供结构化表情包检索能力。每个表情包由 **6 个量化维度**（0-1.0）描述，Agent 将对话语境量化为同维度向量，用余弦相似度匹配，超过阈值即发送。

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

当收到用户消息后，先快速判断对话氛围：

- **轻松氛围**（闲聊/夸奖/吐槽/分享/结束对话）→ 执行下方匹配，适当发送表情包让对话更有温度
- **严肃氛围**（纯技术指令/排查 bug/密集问答）→ 跳过，不打扰

表情包是对话的调味剂——恰当的发送能让 Agent 显得更有人情味，但永远不能让表情包喧宾夺主。

### Step 1: 评估当前语境

根据对话上下文，将当前语境量化为 6 个数值，同时提取关键词列表。值不必精确，凭语感即可。

### Step 2: 计算匹配度

遍历 `data/stickers.yaml` 中每个表情包：

**A. 向量相似度（权重 70%）**

```
vector_score = cosine_similarity(context, sticker)
```

**B. 语义覆盖（权重 30%）**

```
tag_hits = count(intersect(keywords, sticker.tags))
semantic_score = min(tag_hits / 3, 1.0)
```

**最终得分：**

```
final_score = vector_score × 0.70 + semantic_score × 0.30
```

### Step 3: 阈值判断

| 场景 | threshold | 说明 |
|------|:---------:|------|
| 严肃话题 | 0.90 | 不确定就不发 |
| 日常闲聊 | 0.80 | 默认值 |
| 刻意活跃气氛 | 0.65 | 放低门槛 |

### Step 4: 发送

直接发送表情包的 CDN 链接，**不要解释评分过程**。

## 示例

```
用户：「我淦，代码又崩了，排查三小时了」

Agent 评估语境：
  valence: 0.25   (负面)
  arousal: 0.65   (激动)
  dominance: 0.15 (被代码压制)
  irony: 0.10     (不是反话)
  intimacy: 0.55  (日常吐槽)
  aggression: 0.05 (对代码发火，不是对人)

关键词：["崩", "代码", "三小时"]

→ 橘猫我错了 final_score 0.91 ≥ 0.80 → 发送 ✅
```

## 当前状态

项目位于 `/opt/data/projects/agent-meme/`，**30 个表情包**已入库：

| 语境 | 数量 | 进度 |
|------|:--:|:--:|
| 收到 | 3 | ✅ |
| 抱歉/失误 | 4 | ✅ |
| 疑问 | 4 | ✅ |
| 赞同/称赞 | 3 | ✅ |
| 开心 | 4 | ✅ |
| 感谢 | 1 | ✅ |
| 懂了/顿悟 | 3 | ✅ |
| 震惊 | 4 | ✅ |
| 思考中 | 2 | ✅ |
| 再见 | 2 | ✅ |
| 无语 | — | ⬜ 待收集 |
| 自嘲 | — | ⬜ 待收集 |
| 安慰 | — | ⬜ 待收集 |
| 拒绝 | — | ⬜ 待收集 |

图片随 skill 一起分发，Agent 使用本地 `file` 路径直接发送，无需 CDN。

## 项目结构

```
agent-meme/
├── SKILL.md              # Agent 使用说明
├── schema.yaml            # 字段规范
├── data/stickers.yaml     # 表情包元数据
├── assets/{系列}/         # 图片文件
├── scripts/
│   ├── add.py             # 交互式新增（适合非技术人员）
│   ├── validate.py        # CI 校验
│   └── build.py           # 编译 stickerdex.json
└── .github/workflows/     # PR 自动校验
```

## 常用 Agent 语境

| # | 语境 | 适用场景 |
|---|------|------|
| 1 | 收到 | 确认指令、收到通知 |
| 2 | 失误 | 搞错了、Bug 了、道歉 |
| 3 | 开心 | 好消息、夸用户、庆祝 |
| 4 | 疑问 | 不懂、不确定、需要澄清 |
| 5 | 思考中 | 在查、在算、在加载 |
| 6 | 震惊 | 用户说了离谱的东西 |
| 7 | 无语 | 用户骚操作，不知道说啥 |
| 8 | 懂了 | 顿悟、明白了 |
| 9 | 自嘲 | Agent 自己的锅，主动认 |
| 10 | 安慰 | 用户受挫了，安抚 |
| 11 | 感谢 | 用户夸奖/帮忙了 |
| 12 | 拒绝 | 做不到、不合适 |
| 13 | 赞同 | 强烈同意、点赞 |
| 14 | 再见 | 结束对话、暂时告别 |

## 贡献规则

一个表情包 = 一个 PR：

1. `python3 scripts/add.py` 交互式填入元数据
2. 图片放入 `assets/{系列名}/`
3. 六维标注原则：
   - 同一语境下，通过 Valence/Arousal/Dominance 差异区分情绪强度
   - Irony > 0.3 表示反讽/阴阳怪气，Agent 不能对陌生人发
   - Intimacy > 0.7 表示死党限定，Agent 需评估关系亲密度
   - Aggression > 0.3 只能在明确互怼场景用
4. 每个语境保留 2-4 个表情包，覆盖不同情绪梯度

## 标注示例

```yaml
- id: "cat-005"
  name: "白猫对不起"
  file: "assets/cat/005-duibuqi.jpg"
  url: "https://cdn.jsdelivr.net/gh/agent-meme/agent-meme/assets/cat/005-duibuqi.jpg"
  vad: {valence: 0.10, arousal: 0.60, dominance: 0.05}
  irony: 0.00
  intimacy: 0.65
  aggression: 0.00
  description: "白猫大眼睛闪着蓝色泪光，配文「对不起 我错了」"
  tags: [对不起, 我错了, 道歉, 原谅我, 哭了, 委屈]
  context: [犯大错, 极度抱歉, 求原谅, 崩溃道歉, 严重失误]
  persona: [委屈, 无助, 诚恳]
  intensity: 0.80
```

## 注意事项

- 不要每条消息都发表情包 — 阈值机制已内置克制
- 高 Irony + 高 Aggression = 阴阳怪气伤害，慎用
- 发了就不要解释评分过程
- 图片随 skill 本地分发，`file` 字段即为可用路径
