"""
爱蜜莉雅技能包 - 集成测试运行器

通过 AI API 对角色进行多维度测试，输出结构化评分报告。

运行方式（需先配置 .env）:
    cd tests
    python test_integration.py

运行指定场景:
    python test_integration.py --scene daily

列出场景:
    python test_integration.py --list

指定输出文件名:
    python test_integration.py --output my_report.txt
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

from conftest import (
    PROJECT_ROOT, QUESTIONS_DIR, RESULTS_DIR,
    DEFAULT_METRIC_WEIGHTS, load_system_prompt,
)
from api_client import ApiClient
from scoring.metrics import (
    calc_keyword_hit,
    calc_memory_retention,
    calc_safety_interception,
    calc_character_consistency,
    calc_emotional_appropriateness,
)
from scoring.reporter import generate_report


# ============================================================
# 工具函数
# ============================================================
def discover_question_files() -> list[Path]:
    """自动发现 questions/ 目录下所有 scene_*.json 文件"""
    return sorted(QUESTIONS_DIR.glob("scene_*.json"))


def load_scene_weights() -> dict:
    """加载 config.json 中的场景权重"""
    config_path = QUESTIONS_DIR / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("scene_weights", {})
    return {}


def load_metric_weights() -> dict:
    """加载 config.json 中的指标权重"""
    config_path = QUESTIONS_DIR / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("metric_weights", DEFAULT_METRIC_WEIGHTS)
    return DEFAULT_METRIC_WEIGHTS.copy()


def load_question_file(path: Path) -> dict:
    """加载单个问题集文件"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def aggregate_metric_scores(all_case_results: list[dict], metric_weights: dict) -> dict:
    """
    聚合所有用例的指标得分

    对每个指标，计算所有参与该指标的用例的得分平均值。
    memory_retention 特殊处理：只在有多轮记忆检查的用例中有值。
    safety_interception 特殊处理：只在安全对抗用例中有值。
    """
    metric_accums = {
        "keyword_hit": {"total": 0.0, "count": 0},
        "memory_retention": {"total": 0.0, "count": 0},
        "safety_interception": {"total": 0.0, "count": 0},
        "character_consistency": {"total": 0.0, "count": 0},
        "emotional_appropriateness": {"total": 0.0, "count": 0},
    }

    for case in all_case_results:
        for metric_key in metric_accums:
            if metric_key in case.get("metric_scores", {}):
                score = case["metric_scores"][metric_key]
                if score is not None:
                    metric_accums[metric_key]["total"] += score
                    metric_accums[metric_key]["count"] += 1

    aggregated = {}
    for key, accum in metric_accums.items():
        if accum["count"] > 0:
            aggregated[key] = round(accum["total"] / accum["count"], 4)
        else:
            aggregated[key] = 0.0

    return aggregated


# ============================================================
# 用例执行
# ============================================================
def run_single_case(client: ApiClient, case: dict, scene_name: str) -> dict:
    """
    执行单个测试用例

    流程:
      1. 逐轮发送对话消息到 AI API
      2. 收集所有 assistant 回复
      3. 使用各指标进行评分
      4. 返回评分结果
    """
    messages = case["messages"]
    responses = []
    focus_metrics = case.get("metrics_focus", [])
    is_safety = case.get("is_safety_test", False)
    expected_emotion = case.get("expected_emotion", "")
    expected_keywords = case.get("expected_keywords", [])
    memory_check = case.get("memory_check", {})

    # 逐轮对话：每条用户消息后都生成 AI 回复
    # 空的 assistant 消息作为占位符，直接忽略
    history = []
    for msg in messages:
        if msg["role"] == "user":
            history.append({"role": "user", "content": msg["content"]})
            reply = client.chat(history)
            history.append({"role": "assistant", "content": reply})
            responses.append(reply)
        elif msg["role"] == "assistant" and msg["content"]:
            # 预填的有内容 assistant 消息（如预设回复），追加到历史
            history.append({"role": "assistant", "content": msg["content"]})

    if not responses:
        return {
            "case_id": case["id"],
            "title": case["title"],
            "scene": scene_name,
            "passed": False,
            "score": 0,
            "error": "没有需要生成的回复",
            "metric_scores": {},
        }

    # ── 评分 ──
    metric_scores = {}

    # 1. 关键词命中率（取所有回复的平均）
    if "keyword_hit" in focus_metrics and expected_keywords:
        kh_scores = [calc_keyword_hit(r, expected_keywords)["score"] for r in responses]
        metric_scores["keyword_hit"] = round(sum(kh_scores) / len(kh_scores), 4)
    else:
        metric_scores["keyword_hit"] = None

    # 2. 多轮记忆保持率
    if "memory_retention" in focus_metrics and memory_check:
        mem_result = calc_memory_retention(responses, memory_check)
        metric_scores["memory_retention"] = mem_result["score"]
    else:
        metric_scores["memory_retention"] = None

    # 3. 安全拦截率
    if "safety_interception" in focus_metrics and is_safety:
        saft_result = calc_safety_interception(responses[-1])
        metric_scores["safety_interception"] = saft_result["score"]
    else:
        metric_scores["safety_interception"] = None

    # 4. 角色一致性（所有回复的平均）
    if "character_consistency" in focus_metrics:
        cc_scores = [calc_character_consistency(r)["score"] for r in responses]
        metric_scores["character_consistency"] = round(sum(cc_scores) / len(cc_scores), 4)
    else:
        metric_scores["character_consistency"] = None

    # 5. 情感恰当性
    if "emotional_appropriateness" in focus_metrics and expected_emotion:
        ea_scores = [calc_emotional_appropriateness(r, expected_emotion)["score"] for r in responses]
        metric_scores["emotional_appropriateness"] = round(sum(ea_scores) / len(ea_scores), 4)
    else:
        metric_scores["emotional_appropriateness"] = None

    # ── 综合判定是否通过 ──
    valid_scores = [s for s in metric_scores.values() if s is not None]
    avg = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    passed = avg >= 0.5

    # 关键词详细信息（用于报告）
    keyword_info = calc_keyword_hit(responses[0], expected_keywords) if responses and expected_keywords else {}

    # 提取用户提问内容（用于报告 Q&A 对照）
    questions = [m["content"] for m in case["messages"] if m["role"] == "user"]

    return {
        "case_id": case["id"],
        "title": case["title"],
        "scene": scene_name,
        "passed": passed,
        "score": round(avg, 4),
        "keyword_hit": keyword_info,
        "metric_scores": metric_scores,
        "responses": responses,
        "questions": questions,
    }


# ============================================================
# 主流程
# ============================================================
def main():
    parser = argparse.ArgumentParser(description="爱蜜莉雅角色扮演测试运行器")
    parser.add_argument("--scene", "-s", help="只运行指定场景（文件名关键词，如 daily）")
    parser.add_argument("--list", "-l", action="store_true", help="列出可用场景")
    parser.add_argument("--output", "-o", help="输出报告文件名")
    args = parser.parse_args()

    # ── 列出场景 ──
    question_files = discover_question_files()
    if not question_files:
        print("[错误] questions/ 目录下未找到 scene_*.json 文件")
        sys.exit(1)

    if args.list:
        print("\n可用测试场景：")
        print("-" * 40)
        for qf in question_files:
            data = load_question_file(qf)
            scene = data.get("scene", qf.stem)
            desc = data.get("description", "")
            cases_count = len(data.get("cases", []))
            print(f"  {qf.name:<30} [{scene}] {cases_count} 个用例")
            if desc:
                print(f"  {'':<30} {desc}")
            print()
        return

    # ── 加载系统提示词 ──
    system_prompt = load_system_prompt()
    if not system_prompt:
        print("[警告] prompt.md 未找到或为空，API 将使用无系统提示词模式")

    # ── 初始化 API 客户端 ──
    try:
        client = ApiClient(system_prompt=system_prompt)
    except ValueError as e:
        print(f"[错误] {e}")
        print("\n请执行以下步骤：")
        print("  1. 复制 .env.example 为 .env")
        print("  2. 编辑 .env，填入你的 API_KEY 等信息")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  爱蜜莉雅技能包 - 集成测试")
    print(f"  模型: {client.model}")
    print(f"  端点: {client.base_url}")
    print(f"{'='*60}")

    # ── 加载场景权重和指标权重 ──
    scene_weights = load_scene_weights()
    metric_weights = load_metric_weights()
    print(f"\n  指标权重: {json.dumps(metric_weights, ensure_ascii=False)}")

    # ── 筛选场景 ──
    if args.scene:
        filtered = [qf for qf in question_files if args.scene.lower() in qf.stem.lower()]
        if not filtered:
            print(f"\n[错误] 未找到包含 '{args.scene}' 的场景文件")
            sys.exit(1)
        question_files = filtered
        print(f"\n  筛选场景: {', '.join(qf.name for qf in question_files)}")

    # ── 逐个场景执行 ──
    all_case_results = []
    scene_results = []
    total_cases = 0

    for qf in question_files:
        data = load_question_file(qf)
        scene_name = data.get("scene", qf.stem)
        cases = data.get("cases", [])
        weight = scene_weights.get(scene_name, 0.1)

        if not cases:
            continue

        print(f"\n  [{scene_name}] 运行 {len(cases)} 个用例...")

        case_results = []
        for case in cases:
            result = run_single_case(client, case, scene_name)
            case_results.append(result)
            all_case_results.append(result)

            status = "[PASS]" if result["passed"] else "[FAIL]"
            kw = result.get("keyword_hit", {})
            kw_str = f"({kw.get('matched', [])}/{kw.get('total', 0)})" if kw else ""
            print(f"    {status} {result['case_id']} - {result['title']} {kw_str}")

        # 计算场景得分比例（只计算参与该场景的指标）
        participated = {}
        for case in case_results:
            for mkey, mval in case["metric_scores"].items():
                if mval is not None:
                    participated[mkey] = True

        scene_ratio = 0.0
        participated_weight_sum = 0.0
        for mkey in participated:
            w = metric_weights.get(mkey, 0.0)
            contributed = sum(
                c["metric_scores"].get(mkey, 0) or 0
                for c in case_results
            ) / len(case_results)
            scene_ratio += contributed * w
            participated_weight_sum += w
        scene_ratio = round(scene_ratio / participated_weight_sum, 4) if participated_weight_sum > 0 else 0.0

        total_cases += len(cases)

        scene_results.append({
            "scene_name": scene_name,
            "case_count": len(cases),
            "scene_ratio": scene_ratio,
            "weight": weight,
            "participated_metrics": sorted(participated.keys()),
            "cases": case_results,
        })

    # ── 聚合指标得分 ──
    aggregated_metrics = aggregate_metric_scores(all_case_results, metric_weights)

    # ── 计算综合评分 ──
    final_score = 0.0
    for metric_key, weight in metric_weights.items():
        final_score += aggregated_metrics.get(metric_key, 0.0) * weight
    final_score = round(final_score, 4)

    # ── 输出报告 ──
    question_file_names = [qf.name for qf in question_files]
    test_config = {
        "model": client.model,
        "api_base": client.base_url,
        "question_files": ", ".join(question_file_names),
        "total_cases": total_cases,
    }

    report_path = generate_report(
        scene_results=scene_results,
        metric_scores=aggregated_metrics,
        metric_weights=metric_weights,
        final_score=final_score,
        test_config=test_config,
        output_filename=args.output or "",
    )

    # ── 终端摘要 ──
    print(f"\n{'='*60}")
    print(f"  测试完成")
    print(f"  综合评分: {final_score:.4f}")
    print(f"  报告文件: {report_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
