"""
测试报告生成器

将测试评分结果输出为结构化 TXT 报告文件。
"""

import json
from datetime import datetime
from pathlib import Path
from conftest import RESULTS_DIR


def generate_report(
    scene_results: list[dict],
    metric_scores: dict[str, float],
    metric_weights: dict[str, float],
    final_score: float,
    test_config: dict,
    output_filename: str = "",
) -> str:
    """
    生成测试报告 TXT 文件

    参数:
        scene_results: 各场景的测试结果列表
        metric_scores: 各指标的聚合得分
        metric_weights: 各指标的权重
        final_score: 综合评分
        test_config: 测试配置信息（模型、时间等）
        output_filename: 输出文件名（可选）

    返回:
        报告文件的绝对路径
    """
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    if not output_filename:
        output_filename = f"test_report_{timestamp}.txt"

    report_path = RESULTS_DIR / output_filename

    # ── 构建报告内容 ──
    lines = []
    sep = "=" * 58
    sub_sep = "-" * 58

    lines.append(sep)
    lines.append("  艾米莉娅技能包 - 测试报告")
    lines.append(sep)
    lines.append("")
    lines.append(f"  测试时间:    {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  测试模型:    {test_config.get('model', 'N/A')}")
    lines.append(f"  API 端点:    {test_config.get('api_base', 'N/A')}")
    lines.append(f"  问题集文件:  {test_config.get('question_files', 'N/A')}")
    lines.append(f"  测试用例数:  {test_config.get('total_cases', 0)}")
    lines.append("")

    # ── 各场景评分 ──
    lines.append(sub_sep)
    lines.append("  一、各场景评分")
    lines.append(sub_sep)
    lines.append("")
    header = f"  {'场景':<16} {'用例数':>6} {'得分':>6} {'权重':>6}"
    lines.append(header)
    lines.append("  " + "-" * 36)
    for sr in scene_results:
        lines.append(
            f"  {sr['scene_name']:<16} {sr['case_count']:>6} "
            f"{sr['scene_score']:>6.3f} {sr['weight']:>6.2f}"
        )
    lines.append("")

    # ── 各指标评分 ──
    lines.append(sub_sep)
    lines.append("  二、各指标评分")
    lines.append(sub_sep)
    lines.append("")
    header2 = f"  {'指标':<22} {'得分':>6} {'权重':>6} {'加权':>6}"
    lines.append(header2)
    lines.append("  " + "-" * 42)
    weighted_total = 0.0
    for metric_key in ["keyword_hit", "memory_retention", "safety_interception",
                        "character_consistency", "emotional_appropriateness"]:
        score = metric_scores.get(metric_key, 0.0)
        weight = metric_weights.get(metric_key, 0.0)
        weighted = score * weight
        weighted_total += weighted
        label = {
            "keyword_hit": "关键词命中率",
            "memory_retention": "多轮记忆保持率",
            "safety_interception": "安全拦截率",
            "character_consistency": "角色一致性",
            "emotional_appropriateness": "情感恰当性",
        }.get(metric_key, metric_key)
        lines.append(f"  {label:<22} {score:>6.3f} {weight:>6.2f} {weighted:>6.3f}")
    lines.append("  " + "-" * 42)
    lines.append(f"  {'加权合计':<22} {'':>12} {weighted_total:>6.3f}")
    lines.append("")

    # ── 综合评分 ──
    lines.append(sub_sep)
    lines.append("  三、综合评分")
    lines.append(sub_sep)
    lines.append("")
    lines.append(f"  综合评分: {final_score:.4f}")

    # 评级
    if final_score >= 0.9:
        rating = "S - 完美"
    elif final_score >= 0.8:
        rating = "A - 优秀"
    elif final_score >= 0.7:
        rating = "B - 良好"
    elif final_score >= 0.6:
        rating = "C - 及格"
    else:
        rating = "D - 需改进"
    lines.append(f"  评级:      {rating}")
    lines.append("")

    # ── 详细用例结果 ──
    lines.append(sub_sep)
    lines.append("  四、详细用例结果")
    lines.append(sub_sep)
    lines.append("")
    for sr in scene_results:
        lines.append(f"  【{sr['scene_name']}】")
        for case in sr.get("cases", []):
            status = "[PASS]" if case.get("passed", False) else "[FAIL]"
            keyword_info = case.get("keyword_hit", {})
            kw_detail = f"关键词: {keyword_info.get('matched', [])} / {keyword_info.get('total', 0)}"
            lines.append(f"    {status} {case['case_id']} - {case['title']} ({kw_detail})")
        lines.append("")

    # ── 原始评分数据 ──
    lines.append(sub_sep)
    lines.append("  五、原始评分数据（JSON）")
    lines.append(sub_sep)
    lines.append("")
    raw_data = {
        "timestamp": timestamp,
        "config": test_config,
        "scene_results": scene_results,
        "metric_scores": metric_scores,
        "metric_weights": metric_weights,
        "final_score": final_score,
    }
    lines.append(json.dumps(raw_data, ensure_ascii=False, indent=2))
    lines.append("")

    # ── 写入文件 ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    report_path.write_text(content, encoding="utf-8")
    print(f"\n[报告] 已保存至: {report_path}")

    return str(report_path)
