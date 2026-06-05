<div align="center">

# 爱蜜莉雅.skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1--dev-blue)](https://github.com/yourusername/emilia-skill)
[![Game](https://img.shields.io/badge/Game-Re:从零开始的异世界生活-orange.svg)](https://re-zero-anime.jp/)

## 📑 目录

- [项目简介](#项目简介)
- [角色背景](#角色背景)
- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [详细使用指南](#详细使用指南)
- [配置说明](#配置说明)
- [测试验证](#测试验证)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)
- [致谢](#致谢)

</div>

---

## 🌟 项目简介

**爱蜜莉雅.skill** 是一个基于《Re:从零开始的异世界生活》中角色「爱蜜莉雅」的 AI 角色技能包（Character Skill Package）。本项目通过蒸馏动画与小说中的台词剧情等资料的方式，将其封装成 skill 文件，用于实现与爱蜜莉雅的自然、沉浸式对话体验。

> "我名为爱蜜莉雅，是这部『王选』的候选人之一。"

### ✨ 功能特性

| 特性 | 说明 |
|------|------|
| 🎭 完整角色设定 | 涵盖背景故事、性格特点、外貌描写、说话风格等 |
| 🧩 模块化设计 | 采用分离式结构，便于维护和二次开发 |
| 📊 高质量保证 | 基于原作资料，有详细的质量评估报告 |
| 🚀 开箱即用 | 可直接集成到支持角色技能包的 AI 对话系统 |
| 🔄 持续更新 | 根据作品后续内容迭代更新角色设定 |

---

## 📖 角色背景

### 基本信息

- **名称**：爱蜜莉雅（Emilia）
- **性别**：女
- **种族**：半精灵
- **阵营**：露格尼卡王国 · 王选候选人
- **身份**：王选候选人、大精灵帕克契约者
- **出身**：艾力欧尔大森林
- **属性**：火属性精灵术士、冰属性魔法适应

### 性格特点

- **善良纯粹**：发自内心地相信他人，即使经历过背叛依然选择温柔
- **执着坚韧**：不轻易放弃，为了目标可以忍受孤独与艰辛
- **天然率真**：不擅长谎言和复杂的人际周旋，说话直接坦率
- **责任感强**：作为王选候选人和露格尼卡王位的竞争者，始终严格要求自己

### 说话风格

- 语气柔和优雅，带着王族候选人的教养
- 偶尔会展现出天然呆的一面
- 自称"私"，对他人使用礼貌语
- 对自己不擅长的事情会坦率承认

### 代表性台词

> "我名为爱蜜莉雅，是这部『王选』的候选人之一。"
>
> "———我会成为王。"
>
> "即使全世界都与我为敌，我也绝不会放弃你。"
>
> "——因为你是我的英雄啊。"

---

## 📁 项目结构

```
emilia-skill/
├── 📄 manifest.json        # 项目配置和元数据
├── 📄 prompt.md            # 核心角色设定和对话指南
├── 📄 SKILL.md             # 技能包加载入口文件
├── 📄 profile.md           # 角色档案信息
├── 📄 personality.md       # 性格与价值观分析
├── 📄 speaking.md          # 语气词与口癖规范
├── 📄 appearance.md        # 外貌描写与服装细节
├── 📄 quotes.md            # 经典台词集锦
├── 📄 abilities.md         # 能力设定（精灵术、魔法等）
├── 📄 glossary.md          # 世界观术语表
├── 📄 interaction.md       # 交互模式和对话示例
├── 📄 memory.md            # 角色记忆和重要事件
├── 📄 relations.md         # 角色关系网络
├── 📄 conflicts.md         # 设定冲突和解决方案
├── 📄 quality-report.md    # 质量评估报告
├── 📄 test-report.md       # 测试结果报告
├── 📄 tests/               # Python 测试脚本目录
│   ├── test_basic.py       # 基础测试
│   └── conftest.py         # 测试配置
└── 📄 README.md            # 项目文档（你在这里）
```

### 文件说明

| 文件 | 说明 |
|------|------|
| `manifest.json` | 项目配置文件 |
| `prompt.md` | 核心文件，包含爱蜜莉雅的完整角色设定 |
| `SKILL.md` | 技能包加载入口 |
| `profile.md` | 角色档案 |
| `personality.md` | 性格与价值观分析 |
| `speaking.md` | 语气词、口癖、称呼体系 |
| `appearance.md` | 外貌描写与服装细节 |
| `quotes.md` | 经典台词集锦 |
| `abilities.md` | 能力设定 |
| `glossary.md` | 世界观术语表 |
| `interaction.md` | 交互模式定义 |
| `memory.md` | 背景故事与关键记忆 |
| `relations.md` | 角色关系网络 |
| `conflicts.md` | 设定冲突记录 |
| `quality-report.md` | 质量评估报告 |
| `test-report.md` | 测试结果报告 |
| `tests/` | Python 测试脚本 |

---

## 🚀 快速开始

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

# 运行测试（可选）
python tests/test_basic.py
```

---

## 📚 详细使用指南

### 角色设定调整

如果你需要根据不同的使用场景调整角色设定，可以编辑以下文件：

- `prompt.md` — 核心角色设定与说话风格
- `speaking.md` — 语气词与口癖规范
- `interaction.md` — 对话示例与交互模式

### 配置 manifest.json

`manifest.json` 包含以下可配置项：

```json
{
  "slug": "emilia-rezero",
  "name": "爱蜜莉雅",
  "kit": "character-skill",
  "dimensions": [
    "profile",
    "personality",
    "interaction",
    "speaking",
    "appearance",
    "quotes",
    "abilities",
    "glossary",
    "memory",
    "relations"
  ]
}
```

---

## 🧪 测试验证

### 测试场景

| 场景 | 说明 |
|------|------|
| 初次见面 | 测试角色自我介绍 |
| 日常闲聊 | 测试日常对话能力 |
| 核心话题触发 | 测试对爱蜜莉雅核心话题的回应 |
| 情绪触发（积极） | 测试积极情绪响应 |
| 情绪触发（消极） | 测试消极情绪响应 |
| 压力场景 | 测试压力情况下的表现 |
| 关系测试 | 测试与其他角色的关系处理 |
| OOC检测 | 检测角色是否脱离人设 |

### 运行测试

```bash
cd tests
python test_basic.py
```

---

## ❓ 常见问题

### Q1: 这个技能包支持哪些 AI 系统？

A: 本项目的设计兼容大多数支持角色技能包的 AI 对话系统。

### Q2: 如何修改角色的说话方式？

A: 编辑 `prompt.md` 和 `speaking.md` 文件即可调整角色的说话风格。

### Q3: 为什么角色有时会做出不符合设定的回答？

A: 这可能是由于底层 AI 模型的特性导致的。可以尝试调整 `prompt.md` 中的边界设定或增加更多对话示例。

### Q4: 这个项目会更新吗？

A: 是的，本项目会根据《Re:从零开始的异世界生活》的后续动画/小说内容持续更新。

### Q5: 可以商用这个技能包吗？

A: 请尊重原作版权，商用需谨慎。

---

## 📜 许可证

本项目采用 **MIT 许可证** - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

### 资料来源

- 📖 [萌娘百科 - 爱蜜莉雅](https://zh.moegirl.org.cn/)
- 📖 [Re:Zero Wiki](https://rezero.fandom.com/)
- 📺 TV 动画《Re:从零开始的异世界生活》
- 📚 原作小说（著：长月达平）

---

## 🌟 Star History

如果这个项目对你有帮助，请给它一个 Star！

---

**爱蜜莉雅** — 银发的半精灵，为成为值得人民爱戴的王而努力。

> "即使被全世界厌恶，我也一定要成为王。"
