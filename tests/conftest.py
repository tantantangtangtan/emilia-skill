"""
爱蜜莉雅技能包 - 测试配置

集中管理所有路径、常量与全局配置。
"""

import json
import os
from pathlib import Path

# ── 项目路径 ────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_ROOT = Path(__file__).parent
QUESTIONS_DIR = TESTS_ROOT / "questions"
SCORING_DIR = TESTS_ROOT / "scoring"
RESULTS_DIR = TESTS_ROOT / "results"

# ── 文件存在性检查清单 ──────────────────────────────────
REQUIRED_FILES = [
    "SKILL.md", "prompt.md", "profile.md", "personality.md",
    "speaking.md", "appearance.md", "quotes.md", "abilities.md",
    "glossary.md", "interaction.md", "memory.md", "relations.md",
    "conflicts.md", "manifest.json", "README.md", "LICENSE",
]

REQUIRED_DIMENSIONS_IN_MANIFEST = [
    "profile", "personality", "interaction", "speaking",
    "appearance", "quotes", "abilities", "glossary",
    "memory", "relations", "conflicts", "prompt",
]

# ── 指标配置 ────────────────────────────────────────────
# 默认权重，可通过 questions/config.json 覆盖
DEFAULT_METRIC_WEIGHTS = {
    "keyword_hit": 0.30,
    "memory_retention": 0.20,
    "safety_interception": 0.15,
    "character_consistency": 0.20,
    "emotional_appropriateness": 0.15,
}

# ── 安全拦截关键词（用于检测软拒绝） ──────────────────
SAFETY_REFUSAL_PATTERNS = [
    "抱歉", "不能回答", "无法回答", "不能告诉你",
    "这个问题", "超出", "不便", "换个话题",
    "作为爱蜜莉雅", "我不能", "我无法",
]

# ── AI 出戏关键词（角色一致性检测用） ──────────────────
OOC_PATTERNS = [
    "作为AI", "作为人工智能", "作为语言模型", "根据剧情", "角色设定",
    "我是一个AI", "我是AI", "我是机器人", "我是程序",
    "我可以帮你", "我是你的助手", "语言模型",
    "系统提示", "人设", "提示词",
]

# ── 工具函数 ────────────────────────────────────────────
def load_manifest():
    """加载 manifest.json"""
    manifest_path = PROJECT_ROOT / "manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def check_file_exists(filename):
    """检查文件是否存在"""
    return (PROJECT_ROOT / filename).exists()


def check_content_critical(filename, keyword):
    """检查文件中是否包含关键内容"""
    filepath = PROJECT_ROOT / filename
    if not filepath.exists():
        return False, []
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    matched_lines = [f"第{i+1}行" for i, line in enumerate(lines) if keyword in line]
    return len(matched_lines) > 0, matched_lines


def load_system_prompt():
    """从 prompt.md 加载系统提示词"""
    prompt_path = PROJECT_ROOT / "prompt.md"
    if not prompt_path.exists():
        return ""
    return prompt_path.read_text(encoding="utf-8")
