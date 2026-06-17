"""
测试报告生成器

将测试评分结果输出为结构化 TXT 报告文件。
所有得分均为整数（满分 100 分制）。
"""

import json
from datetime import datetime
from pathlib import Path
from conftest import RESULTS_DIR

METRIC_LABELS = {
    "keyword_hit": "关键词命中率",
    "memory_retention": "多轮记忆保持率",
    "safety_interception": "安全拦截率",
    "character_consistency": "角色一致性",
    "emotional_appropriateness": "情感恰当性",
}

METRIC_ORDER = ["keyword_hit", "memory_retention", "safety_interception",
                "character_consistency", "emotional_appropriateness"]


def _collect_participated_metrics(scene_results: list[dict]) -> set:
    all_p = set()
    for sr in scene_results:
        all_p.update(sr.get("participated_metrics", []))
    return all_p


def generate_report(
    scene_results: list[dict],
    metric_scores: dict[str, int],
    metric_weights: dict[str, float],
    metric_max: dict[str, int],
    final_score: int,
    total_score: int,
    test_config: dict,
    output_filename: str = "",
) -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    if not output_filename:
        output_filename = f"test_report_{timestamp}.txt"

    report_path = RESULTS_DIR / output_filename
    num_scenes = len(scene_results)
    participated = _collect_participated_metrics(scene_results)

    # 计算测试序号
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    existing_reports = sorted(RESULTS_DIR.glob("*.txt"))
    test_seq = len(existing_reports) + 1

    # ── 计算有效满分（仅参与指标） ──
    effective_max = sum(metric_max.get(m, 0) for m in participated)

    lines = []
    sep = "=" * 62
    sub_sep = "-" * 62

    # ── 标题 ──
    lines.append(sep)
    lines.append("  爱蜜莉雅技能包 - 测试报告  (满分 {total_score} 分)".format(total_score=total_score))
    lines.append(sep)
    lines.append("")
    lines.append(f"  测试序号:    第 {test_seq} 次")
    lines.append(f"  测试时间:    {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"  测试模型:    {test_config.get('model', 'N/A')}")
    lines.append(f"  API 端点:    {test_config.get('api_base', 'N/A')}")
    lines.append(f"  测试场景数:  {num_scenes}")
    lines.append(f"  问题集文件:  {test_config.get('question_files', 'N/A')}")
    lines.append(f"  测试用例数:  {test_config.get('total_cases', 0)}")
    lines.append(f"  PASS 标准:   用例指标均分 >= 0.5")
    lines.append("")

    # ── 一、各场景评分 ──
    lines.append(sub_sep)
    lines.append("  一、各场景评分")
    lines.append(sub_sep)
    lines.append("")
    header = f"  {'场景':<18} {'用例':>4} {'得分':>8} {'参与的指标'}"
    lines.append(header)
    lines.append("  " + "-" * 60)
    for sr in scene_results:
        sc = sr["scene_score"]
        sm = sr["scene_max"]
        p_metrics = sr.get("participated_metrics", [])
        p_labels = ", ".join(METRIC_LABELS.get(m, m) for m in p_metrics)
        lines.append(
            f"  {sr['scene_name']:<18} {sr['case_count']:>4}  "
            f"{sc:>3} / {sm:<3}  {p_labels}"
        )
    lines.append("")

    # ── 二、用例详情（问题与回答 + 关键词命中） ──
    lines.append(sub_sep)
    lines.append("  二、用例详情")
    lines.append(sub_sep)
    lines.append("")
    for sr in scene_results:
        lines.append(f"  【{sr['scene_name']}】")
        lines.append("")
        for case in sr.get("cases", []):
            status = "[PASS]" if case.get("passed", False) else "[FAIL]"
            questions = case.get("questions", [])
            responses = case.get("responses", [])

            lines.append(f"    {status} {case['case_id']} - {case['title']}")

            # Q&A（先输出问题和回答）
            for i, q in enumerate(questions):
                lines.append(f"")
                lines.append(f"    Q{i+1}: {q}")
                if i < len(responses):
                    answer = responses[i].strip()
                    lines.append(f"    A{i+1}: {answer}")

            # 关键词命中详情（放在 Q&A 下方）
            kd = case.get("keyword_detail", {})
            if kd:
                matched = kd.get("matched", [])
                missed = kd.get("missed", [])
                total = kd.get("total", 0)
                if total > 0:
                    lines.append(f"           → 关键词 ({len(matched)}/{total})")
                    if matched:
                        lines.append(f"              命中: {', '.join(matched)}")
                    else:
                        lines.append(f"              命中：无")
                    if missed:
                        lines.append(f"              未命中: {', '.join(missed)}")
                    else:
                        lines.append(f"              未命中：无")
            lines.append("")
        lines.append("")

    # ── 三、各指标评分 ──
    lines.append(sub_sep)
    lines.append("  三、各指标评分")
    lines.append(sub_sep)
    lines.append("")
    header2 = f"  {'指标':<22} {'得分':>8} {'满分':>6}"
    lines.append(header2)
    lines.append("  " + "-" * 38)
    for mkey in METRIC_ORDER:
        label = METRIC_LABELS.get(mkey, mkey)
        mx = metric_max.get(mkey, 0)
        if mkey in participated:
            score = metric_scores.get(mkey, 0)
            lines.append(f"  {label:<22} {score:>5} 分 {mx:>5} 分")
        else:
            lines.append(f"  {label:<22} {'--':>5}    {mx:>5} 分")
    lines.append("  " + "-" * 38)
    lines.append(f"  {'合计':<22} {final_score:>5} 分 {total_score:>5} 分")
    lines.append("")

    # ── 四、综合评分 ──
    lines.append(sub_sep)
    lines.append("  四、综合评分")
    lines.append(sub_sep)
    lines.append("")
    lines.append(f"  综合评分: {final_score} / {total_score}")

    if num_scenes == 1:
        lines.append(f"  (注意: 仅测试了 1 个场景，得分仅反映该场景参与的指标)")
        lines.append(f"  该场景参与指标: {', '.join(METRIC_LABELS.get(m, m) for m in participated)}")
        if effective_max > 0 and effective_max < total_score:
            rate = final_score / effective_max if effective_max > 0 else 0
            lines.append(f"  本场有效满分: {effective_max} 分  |  有效得分率: {rate:.0%}  ({final_score}/{effective_max})")
    lines.append("")

    # ── 五、原始评分数据 ──
    lines.append(sub_sep)
    lines.append("  五、原始评分数据")
    lines.append(sub_sep)
    lines.append("")
    raw_data = {
        "timestamp": timestamp,
        "config": test_config,
        "scene_results": scene_results,
        "metric_scores": metric_scores,
        "metric_max": metric_max,
        "final_score": final_score,
        "total_score": total_score,
        "participated_metrics": sorted(participated),
    }

    # JSON 写入独立文件
    json_filename = output_filename.replace(".txt", ".json") if output_filename.endswith(".txt") else output_filename + ".json"
    json_path = RESULTS_DIR / json_filename
    json_path.write_text(json.dumps(raw_data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines.append(f"  详细评分数据已保存至: {json_filename}")
    lines.append(f"  (JSON 格式，包含所有指标的原始分数和用例级详情)")
    lines.append("")

    content = "\n".join(lines)
    report_path = RESULTS_DIR / output_filename  # 注意: 此处 RESULTS_DIR 已在前方 mkdir
    report_path.write_text(content, encoding="utf-8")
    print(f"\n[报告] 已保存至: {report_path}")
    print(f"[数据] 已保存至: {json_path}")
    return str(report_path)
