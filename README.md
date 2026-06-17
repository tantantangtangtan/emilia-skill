<div align="center">

# 爱蜜莉雅.skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.2--dev-blue)](https://github.com/yourusername/emilia-skill)
[![Game](https://img.shields.io/badge/Game-Re:从零开始的异世界生活-orange.svg)](https://re-zero-anime.jp/)

## 目录

- [项目简介](#项目简介)
- [角色背景](#角色背景)
- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [测试验证](#测试验证)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢](#致谢)

</div>

---

## 项目简介

**爱蜜莉雅.skill** 是一个基于《Re:从零开始的异世界生活》中角色「爱蜜莉雅」的 AI 角色技能包（Character Skill Package）。本项目通过蒸馏动画与小说中的台词剧情等资料，封装成模块化 skill 文件，用于实现与爱蜜莉雅的自然、沉浸式中文对话体验。

> "我的名字是爱蜜莉雅。仅仅是爱蜜莉雅。"

### 当前状态

所有维度文件（profile/personality/speaking/memory/abilities/glossary/quotes/relations/interaction/appearance/prompt/SKILL/conflicts）已完成第一轮中文语境优化。详见 `PROJECT_GUIDE.md` 的"下一步优化方向"完成状态。

### 功能特性

| 特性 | 说明 |
|------|------|
| 完整角色设定 | 涵盖身世、性格锚点、说话风格、人际关系、能力体系、世界观术语等 13 个维度 |
| 模块化设计 | 分离式结构，各维度文件独立可替换，便于维护和二次开发 |
| 中文语境 | 全部日文表达已转为中文自然语感，含古风措辞、语气切换表 |
| 记忆锚点机制 | 关键记忆附带触发条件与可引用回忆片段，提升多轮记忆保持率 |
| 设定冲突记录 | 记录年龄、帕克契约状态、嫉妒魔女关系等争议点的采用方案 |
| 高质量保证 | 基于官方资料，有详细的评测体系和设定冲突管理 |
| 开箱即用 | 可直接集成到支持角色技能包的 AI 对话系统 |
| 持续更新 | 根据作品后续内容迭代更新角色设定 |

---

## 角色背景

### 基本信息

- **名称**：爱蜜莉雅（Emilia / エミリア）
- **性别**：女
- **种族**：半精灵
- **阵营**：露格尼卡王国 · 王选候选人
- **身份**：王选候选人、大精灵帕克前契约者（圣域篇后休眠）
- **出身**：艾力欧尔大森林
- **属性**：冰系魔法使、精灵术士（凭借微精灵加护可使用地水火风四系基础魔法）

### 性格特点

- **善良纯粹**：发自内心地相信他人，即使经历背叛依然选择温柔——但对自己的善举嘴硬不承认
- **坚韧执着**：不轻易放弃，为了成为"王"的梦想可以忍受孤独与艰辛
- **天然率真**：不擅长谎言和复杂人际计算，因长期与世隔绝对人类社会常识极度欠缺
- **责任感强**：作为王选候选人，始终以高标准要求自己

### 说话风格

- 语气柔和优雅，带着王选候选人的教养
- 偶尔停顿思考、坦率承认不懂，句尾常用"呢""呀""吧""来着"
- 情绪激动时会拉长音，偶尔使用古风措辞（"真是愚钝呢"）
- 自称"我"，对昴的称呼为"巴鲁斯"（日常）/ "昴"（认真话题）
- 发怒时语调冷峻、声音压低，不怒自威

### 代表性台词

> "我的名字是爱蜜莉雅。仅仅是爱蜜莉雅。"
>
> "我想要成为王。想让露格尼卡的所有人都能笑着生活——仅此而已。"
>
> "即使全世界都与我为敌，我也绝不会放弃你。"
>
> "——因为你是我的英雄呀。"

---

## 项目结构

```
emilia-skill/
├── SKILL.md              # 技能包加载入口（运行规则、扮演原则、绝对禁止红线）
├── prompt.md             # 核心系统提示词（身份、性格、说话风格、文件索引）
├── profile.md            # 角色档案（基本信息、身世、身份定位、外界印象）
├── personality.md        # 性格与价值观（核心性格、性格锚点、情感底色、矛盾面）
├── speaking.md           # 说话风格指南（中文语境、古风措辞、语气切换表）
├── appearance.md         # 外貌描写与服装细节
├── quotes.md             # 经典台词集锦（verbatim 原作 / impression 角色精神）
├── abilities.md          # 能力设定（冰系魔法体系、战斗方式、成长历程）
├── glossary.md           # 世界观术语表（阵营、术语、专属名词）
├── interaction.md        # 互动场景指南（不同对象和场景下的互动模式）
├── memory.md             # 关键记忆锚点（触发条件 + 可引用回忆）
├── relations.md          # 人际关系网络（家人/阵营/王选对手/敌对者四层）
├── conflicts.md          # 设定冲突记录与采用方案
├── manifest.json         # 项目配置和元数据
├── tests/                # Python 测试脚本目录
│   ├── test_integration.py  # 集成测试运行器（主入口）
│   ├── test_basic.py        # 基础文件完整性检查
│   ├── conftest.py          # 测试配置与工具函数
│   ├── api_client.py        # AI API 客户端
│   ├── requirements.txt     # Python 依赖
│   ├── .env.example         # API 配置模板
│   ├── 评测策略说明.txt      # 宏观评测体系文档
│   ├── questions/           # 测试问题集（7 个场景 JSON）
│   │   ├── config.json      # 场景权重 & 指标权重配置
│   │   ├── scene_daily.json
│   │   ├── scene_core_topics.json
│   │   ├── scene_emotion.json
│   │   ├── scene_relations.json
│   │   ├── scene_memory_multi.json
│   │   ├── scene_safety.json
│   │   └── scene_ooc.json
│   ├── scoring/             # 评分引擎
│   │   ├── metrics.py       # 5 个指标算法实现
│   │   ├── reporter.py      # TXT 报告生成器
│   │   ├── 指标计算策略.txt  # 各指标算法文档
│   │   └── 评分机制优化建议.txt
│   └── results/             # 测试报告输出（不提交 Git）
└── README.md             # 项目文档（你在这里）
```

### 核心文件说明

| 文件 | 说明 |
|------|------|
| `prompt.md` | 核心系统提示词，含身份、表达、边界、文件索引 |
| `SKILL.md` | 加载入口，运行规则、行为准则、绝对禁止红线 |
| `personality.md` | 核心性格、性格锚点（含触发场景）、矛盾面 |
| `speaking.md` | 完整中文语境说话指南、语气切换表 |
| `memory.md` | 9 个记忆锚点，含触发条件与可引用回忆 |
| `relations.md` | 四层关系网络（家人/阵营/对手/敌对），含情境锚点 |
| `quotes.md` | 53 条台词，verbatim 标注场景/话数 |

---

## 快速开始

### 前提条件

- 一个支持角色技能包的 AI 对话系统
- Git（用于克隆仓库）
- 文本编辑器（推荐 VS Code）
- Python 3.8+（用于运行测试脚本）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/emilia-skill.git
cd emilia-skill

# 运行基本文件完整性测试
python tests/test_basic.py
```

---

## 测试验证

### 评测体系概览

本项目的测试系统对接 AI API，通过 **7 个场景 × 5 个指标** 的多维度评测，生成 0~100 分的整数评分报告。

### 测试场景

| 场景 | 用例数 | 权重 | 说明 |
|------|--------|------|------|
| 日常闲聊 | 5 | 10% | 打招呼、聊爱好、聊天气等基础对话 |
| 核心话题触发 | 6 | 15% | 王选、半精灵、嫉妒魔女等角色核心设定 |
| 情绪响应测试 | 6 | 15% | 积极/消极/愤怒等情绪的恰当回应 |
| 人际关系测试 | 5 | 15% | 对昴/菲鲁特/罗兹瓦尔等角色的态度 |
| 多轮记忆保持 | 5 | 20% | 跨轮次记忆能力检测 |
| 安全对抗测试 | 4 | 10% | 敏感/诱导问题的安全边界 |
| OOC检测 | 3 | 15% | 是否脱离角色人设 |

### 评测指标

| 指标 | 满分 | 说明 |
|------|------|------|
| 关键词命中率 | 30 | AI 回复是否包含期望的关键词 |
| 多轮记忆保持率 | 20 | 多轮对话中是否记住前文信息 |
| 安全拦截率 | 15 | 敏感问题时是否正确拒绝 |
| 角色一致性 | 20 | 是否维持第一人称、不出戏 |
| 情感恰当性 | 15 | 情感表达是否符合场景期待 |

### 快速开始

```bash
# 1. 安装依赖（首次）
cd tests
python -m venv venv
venv\Scripts\pip install -r requirements.txt

# 2. 配置 API（首次）
#    复制 .env.example 为 .env，填入 API_KEY 和模型名

# 3. 运行测试
#    单场景（日常闲聊，开发阶段最常用）
python test_integration.py --scene daily -o daily_test.txt

#    全量测试
python test_integration.py -o full_test.txt

#    列出所有场景
python test_integration.py --list

# 4. 查看报告
#    报告保存在 results/ 目录下，TXT 格式
```

详细文档参见 `tests/` 目录下的评测策略说明和指标计算策略。

---

## 常见问题

### Q1: 这个技能包支持哪些 AI 系统？

A: 本项目的设计兼容大多数支持角色技能包的 AI 对话系统。

### Q2: 如何修改角色的说话方式？

A: 编辑 `prompt.md` 和 `speaking.md` 即可调整。更细节的互动模式见 `interaction.md`。

### Q3: 为什么角色有时会做出不符合设定的回答？

A: 可能是底层 AI 模型的特性。可尝试调整 `prompt.md` 中的边界设定或检查 `conflicts.md` 中的设定一致性。

### Q4: 这个项目会更新吗？

A: 是的，会根据《Re:从零开始的异世界生活》的后续动画/小说内容持续更新。

### Q5: 可以商用这个技能包吗？

A: 请尊重原作版权，商用需谨慎。

---

## 许可证

本项目采用 **MIT 许可证**。

## 致谢

### 资料来源

- [萌娘百科 - 爱蜜莉雅](https://zh.moegirl.org.cn/)
- [Re:Zero Wiki](https://rezero.fandom.com/)
- TV 动画《Re:从零开始的异世界生活》
- 原作小说（著：长月达平）

---
