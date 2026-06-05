"""
艾米莉娅技能包 - 测试配置
"""

import json
import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 文件存在性检查清单
REQUIRED_FILES = [
    "SKILL.md",
    "prompt.md",
    "profile.md",
    "personality.md",
    "speaking.md",
    "appearance.md",
    "quotes.md",
    "abilities.md",
    "glossary.md",
    "interaction.md",
    "memory.md",
    "relations.md",
    "conflicts.md",
    "quality-report.md",
    "test-report.md",
    "manifest.json",
    "README.md",
    "LICENSE",
]

REQUIRED_DIMENSIONS_IN_MANIFEST = [
    "profile",
    "personality",
    "interaction",
    "speaking",
    "appearance",
    "quotes",
    "abilities",
    "glossary",
    "memory",
    "relations",
]


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
