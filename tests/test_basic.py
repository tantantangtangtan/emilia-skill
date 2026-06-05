"""
艾米莉娅技能包 - 基础测试脚本

运行方式：
    cd tests
    python test_basic.py

测试覆盖：
    - 文件完整性检查
    - 项目配置验证
    - 关键内容完整性
    - 证据标注覆盖
    - 角色设定一致性
"""

import sys
import json
from pathlib import Path

# 确保 conftest.py 可以被导入
sys.path.insert(0, str(Path(__file__).parent))

from conftest import (
    PROJECT_ROOT,
    REQUIRED_FILES,
    REQUIRED_DIMENSIONS_IN_MANIFEST,
    load_manifest,
    check_file_exists,
    check_content_critical,
)


# ============================================================
# 测试结果统计
# ============================================================
class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.details = []

    def add_pass(self, test_name, detail=""):
        self.passed += 1
        self.details.append(f"  [PASS] | {test_name}")

    def add_fail(self, test_name, detail=""):
        self.failed += 1
        self.details.append(f"  [FAIL] | {test_name}  ->  {detail}")

    def summary(self):
        total = self.passed + self.failed
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        for d in self.details:
            print(d)
        print("=" * 60)
        print(f"总计: {total}  |  通过: {self.passed}  |  失败: {self.failed}")
        if total > 0:
            print(f"通过率: {self.passed / total * 100:.1f}%")
        return self.failed == 0


result = TestResult()


# ============================================================
# Test 1: 文件完整性检查
# ============================================================
def test_file_integrity():
    print("\n[Test 1] 文件完整性检查")
    all_ok = True
    for f in REQUIRED_FILES:
        exists = check_file_exists(f)
        if exists:
            result.add_pass(f"文件存在: {f}")
        else:
            result.add_fail(f"文件缺失: {f}")
            all_ok = False
    return all_ok


# ============================================================
# Test 2: manifest.json 配置验证
# ============================================================
def test_manifest_config():
    print("\n[Test 2] manifest.json 配置验证")
    try:
        manifest = load_manifest()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        result.add_fail("manifest.json 加载失败", str(e))
        return False

    checks = [
        ("slug", manifest.get("slug") == "emilia-rezero", "slug 应为 emilia-rezero"),
        ("name", manifest.get("name") == "艾米莉娅", "name 应为 艾米莉娅"),
        ("kit", manifest.get("kit") == "character-skill", "kit 应为 character-skill"),
    ]

    all_ok = True
    for check_name, cond, desc in checks:
        if cond:
            result.add_pass(f"manifest.{check_name}", desc)
        else:
            result.add_fail(f"manifest.{check_name}", desc)
            all_ok = False

    # 检查 dimensions 完整性
    dims = manifest.get("dimensions", [])
    for d in REQUIRED_DIMENSIONS_IN_MANIFEST:
        if d in dims:
            result.add_pass(f"dimensions 包含: {d}")
        else:
            result.add_fail(f"dimensions 缺失: {d}")
            all_ok = False

    return all_ok


# ============================================================
# Test 3: SKILL.md 关键内容检查
# ============================================================
def test_skill_core_content():
    print("\n[Test 3] SKILL.md 关键内容检查")
    all_ok = True

    critical_checks = [
        ("SKILL.md", "艾米莉娅", "应包含角色名"),
        ("SKILL.md", "王选", "应包含王选背景"),
        ("SKILL.md", "帕克", "应包含帕克"),
        ("SKILL.md", "第一人称", "应包含第一人称铁律"),
        ("SKILL.md", "绝对不可违背", "应包含最高规则声明"),
    ]

    for fname, keyword, desc in critical_checks:
        found, _ = check_content_critical(fname, keyword)
        if found:
            result.add_pass(f"{fname} 含有关键词: {keyword}")
        else:
            result.add_fail(f"{fname} 缺失关键词: {keyword}", desc)
            all_ok = False

    return all_ok


# ============================================================
# Test 4: prompt.md 角色设定完整性
# ============================================================
def test_prompt_completeness():
    print("\n[Test 4] prompt.md 角色设定完整性")
    all_ok = True

    required_sections = [
        ("核心设定", "核心设定章节"),
        ("身份与背景", "身份与背景章节"),
        ("角色呈现指南", "角色呈现指南章节"),
        ("性格要求", "性格要求章节"),
        ("说话风格", "说话风格章节"),
        ("重要边界", "重要边界章节"),
        ("绝对第一人称铁律", "第一人称铁律章节"),
    ]

    for keyword, desc in required_sections:
        found, lines = check_content_critical("prompt.md", keyword)
        if found:
            result.add_pass(f"prompt.md 包含: {desc}")
        else:
            result.add_fail(f"prompt.md 缺失: {desc}")
            all_ok = False

    return all_ok


# ============================================================
# Test 5: 各维度文件内容完整性
# ============================================================
def test_dimension_files():
    print("\n[Test 5] 各维度文件内容完整性")
    all_ok = True

    checks = [
        ("profile.md", "# 艾米莉娅", "应包含角色标题"),
        ("profile.md", "王选", "应包含王选身份"),
        ("personality.md", "善良", "应包含性格描述"),
        ("personality.md", "王", "应包含成王目标"),
        ("speaking.md", "巴鲁斯", "应包含对昴的称呼"),
        ("speaking.md", "私", "应包含自称"),
        ("appearance.md", "银白", "应包含银发描述"),
        ("appearance.md", "紫", "应包含紫色要素"),
        ("quotes.md", "我会成为王", "应包含标志性台词"),
        ("quotes.md", "英雄", "应包含对昴的台词"),
        ("abilities.md", "精灵", "应包含精灵术士设定"),
        ("abilities.md", "冰", "应包含冰魔法设定"),
        ("glossary.md", "露格尼卡", "应包含世界观术语"),
        ("glossary.md", "魔女", "应包含魔女相关术语"),
        ("interaction.md", "对话风格", "应包含互动风格描述"),
        ("memory.md", "艾力欧尔大森林", "应包含森林背景"),
        ("memory.md", "帕克", "应包含帕克相关记忆"),
        ("relations.md", "菜月昴", "应包含昴的关系描述"),
        ("relations.md", "帕克", "应包含帕克的关系描述"),
        ("conflicts.md", "冲突", "应包含冲突记录"),
    ]

    for fname, keyword, desc in checks:
        found, _ = check_content_critical(fname, keyword)
        if found:
            result.add_pass(f"{fname} 关键内容: {desc}")
        else:
            result.add_fail(f"{fname} 缺失内容: {desc}")
            all_ok = False

    return all_ok


# ============================================================
# Test 6: 证据标注覆盖检查
# ============================================================
def test_evidence_coverage():
    print("\n[Test 6] 证据标注覆盖检查")
    all_ok = True

    evidence_files = [
        "prompt.md", "profile.md", "personality.md",
        "interaction.md", "memory.md", "relations.md",
        "speaking.md", "appearance.md", "quotes.md",
        "abilities.md", "conflicts.md",
    ]

    for fname in evidence_files:
        content = (PROJECT_ROOT / fname).read_text(encoding="utf-8")
        # 检查是否有证据标注
        has_artifact = "[artifact]" in content
        has_verbatim = "[verbatim]" in content

        if has_artifact or has_verbatim:
            tags = []
            if has_artifact:
                tags.append("[artifact]")
            if has_verbatim:
                tags.append("[verbatim]")
            result.add_pass(f"{fname} 含证据标注: {', '.join(tags)}")
        else:
            result.add_fail(f"{fname} 缺少证据标注", "建议添加 [artifact] 或 [verbatim] 标签")
            all_ok = False

    return all_ok


# ============================================================
# 主程序
# ============================================================
def main():
    print("=" * 60)
    print("艾米莉娅技能包 - 基础测试")
    print(f"项目路径: {PROJECT_ROOT}")
    print("=" * 60)

    tests = [
        ("文件完整性", test_file_integrity),
        ("manifest.json 配置", test_manifest_config),
        ("SKILL.md 关键内容", test_skill_core_content),
        ("prompt.md 设定完整性", test_prompt_completeness),
        ("各维度文件内容", test_dimension_files),
        ("证据标注覆盖", test_evidence_coverage),
    ]

    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            result.add_fail(test_name, f"测试执行异常: {e}")

    success = result.summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
