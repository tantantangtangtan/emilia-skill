"""
测试报告生成器

将测试评分结果输出为结构化 TXT 报告文件。
"""

import json
from datetime import datetime
from pathlib import Path
from conftest import RESULTS_DIR

# 指标中文标签
METRIC_LABELS = {
    "keyword_hit": "关键词命中率",
    "memory_retention": "多轮记忆保持率",
    "safety_interception": "安全拦截率",
    "character_consistency": "角色一致性",
    "emotional_appropriateness": "情感恰当性",
}


def _collect_participated_metrics(scene_results: list[dict]) -> set:
    """汇总所有场景中参与了计算的指标"""
    all_participated = set()
    for sr in scene_results:
        all_participated.update(sr.get("participated_metrics", []))
    return all_participated


def generate_report(
    scene_results: list[dict],
    metric_scores: dict[str, float],
    metric_weights: dict[str, float],
    final_score: float,
    test_config: dict,
    output_filename: str = "",
) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    if not output_filename:
        output_filename = f"test_report_{timestamp}.txt"

    report_path = RESULTS_DIR / output_filename
    num_scenes = len(scene_results)
    participated_metrics = _collect_participated_metrics(scene_results)

    lines = []
    sep = "=" * 58
    sub_sep = "-" * 58

    # ── 标题 ──
    lines.append(sep)
    lines.append("  爱蜜莉雅技能包 - 测试报告")
    lines.append(sep)
    lines.append("")
    lines.append(f"  测试时间:    {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  测试模型:    {test_config.get('model', 'N/A')}")
    lines.append(f"  API 端点:    {test_config.get('api_base', 'N/A')}")
    lines.append(f"  测试场景数:  {num_scenes}")
    lines.append(f"  问题集文件:  {test_config.get('question_files', 'N/A')}")
    lines.append(f"  测试用例数:  {test_config.get('total_cases', 0)}")
    lines.append("")

    # ── 一、各场景评分 ──
    lines.append(sub_sep)
    lines.append("  一、各场景评分（得分比例 = 参与指标加权得分 / 参与指标权重和）")
    lines.append(sub_sep)
    lines.append("")
    header = f"  {'场景':<16} {'用例':>4} {'得分比例':>8} {'参与的指标':>36}"
    lines.append(header)
    lines.append("  " + "-" * 56)
    for sr in scene_results:
        ratio = sr.get("scene_ratio", 0.0)
        p_metrics = sr.get("participated_metrics", [])
        p_labels = ", ".join(METRIC_LABELS.get(m, m) for m in p_metrics)
        lines.append(
            f"  {sr['scene_name']:<16} {sr['case_count']:>4} "
            f"{ratio:>8.3f}  {p_labels:<36}"
        )
    lines.append("")

    # ── 二、问题与回答对照 ──
    lines.append(sub_sep)
    lines.append("  二、问题与回答对照")
    lines.append(sub_sep)
    lines.append("")
    for sr in scene_results:
        lines.append(f"  【{sr['scene_name']}】")
        for case in sr.get("cases", []):
            questions = case.get("questions", [])
            responses = case.get("responses", [])
            for i, q in enumerate(questions):
                lines.append(f"    Q{i+1}: {q}")
            for i, a in enumerate(responses):
                lines.append(f"    A{i+1}: {a}")
            lines.append("")
        lines.append("")

    # ── 三、各指标评分 ──
    lines.append(sub_sep)
    lines.append("  三、各指标评分")
    lines.append(sub_sep)
    lines.append("")
    header2 = f"  {'指标':<22} {'得分':>8} {'权重':>6} {'加权':>6}"
    lines.append(header2)
    lines.append("  " + "-" * 44)
    weighted_total = 0.0
    metric_order = ["keyword_hit", "memory_retention", "safety_interception",
                    "character_consistency", "emotional_appropriateness"]
    for metric_key in metric_order:
        label = METRIC_LABELS.get(metric_key, metric_key)
        weight = metric_weights.get(metric_key, 0.0)

        if metric_key in participated_metrics:
            score = metric_scores.get(metric_key, 0.0)
            weighted = score * weight
            weighted_total += weighted
            lines.append(f"  {label:<22} {score:>8.3f} {weight:>6.2f} {weighted:>6.3f}")
        else:
            lines.append(f"  {label:<22} {'N/A':>8} {weight:>6.2f} {'-':>6}")
    lines.append("  " + "-" * 44)
    lines.append(f"  {'加权合计':<22} {'':>14} {weighted_total:>6.3f}")
    lines.append("")

    # ── 四、综合评分 ──
    lines.append(sub_sep)
    lines.append("  四、综合评分")
    lines.append(sub_sep)
    lines.append("")
    lines.append(f"  综合评分: {final_score:.4f}")

    if num_scenes == 1:
        # 单场景：只参与部分指标，综合评分反映该场景的加权得分
        lines.append(f"  （注意: 仅测试了 1 个场景，综合评分仅反映该场景参与的指标）")
        lines.append(f"  该场景参与指标: {', '.join(METRIC_LABELS.get(m, m) for m in participated_metrics)}")

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

    # ── 五、详细用例结果 ──
    lines.append(sub_sep)
    lines.append("  五、详细用例结果")
    lines.append(sub_sep)
    lines.append("")
    for sr in scene_results:
        lines.append(f"  【{sr['scene_name']}】")
        for case in sr.get("cases", []):
            status = "[PASS]" if case.get("passed", False) else "[FAIL]"
            keyword_info = case.get("keyword_hit", {})
            matched = keyword_info.get("matched", [])
            total = keyword_info.get("total", 0)
            if matched or total:
                kw_detail = f"关键词: {matched} / {total}"
            else:
                kw_detail = ""
            lines.append(f"    {status} {case['case_id']} - {case['title']}  {kw_detail}")
        lines.append("")

    # ── 六、原始评分数据 ──
    lines.append(sub_sep)
    lines.append("  六、原始评分数据（JSON）")
    lines.append(sub_sep)
    lines.append("")
    raw_data = {
        "timestamp": timestamp,
        "config": test_config,
        "scene_results": scene_results,
        "metric_scores": metric_scores,
        "metric_weights": metric_weights,
        "final_score": final_score,
        "participated_metrics": sorted(participated_metrics),
    }
    lines.append(json.dumps(raw_data, ensure_ascii=False, indent=2))
    lines.append("")

    # ── 写入文件 ──
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines)
    report_path.write_text(content, encoding="utf-8")
    print(f"\n[报告] 已保存至: {report_path}")

    return str(report_path)
