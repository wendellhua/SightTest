"""评分与风险等级计算（需求附录 A-1 固定规则）。"""

from typing import Any

PRIORITY_WEIGHT = {"P0": 8, "P1": 4, "P2": 2, "P3": 1}
TYPE_WEIGHT = {"func": 0.4, "api": 0.3, "perf": 0.2, "mech": 0.1}


def calculate_score(case_results: list[dict[str, Any]], issues: list[dict[str, Any]]) -> dict[str, Any]:
    """计算综合评分、风险等级与覆盖率。

    Args:
        case_results: 每条用例结果，含 case_type/priority/result。
        issues: 主动发现的问题，含 severity（high/medium/low）。
    """
    judged = [c for c in case_results if c.get("result") in ("pass", "fail")]

    type_weights: dict[str, int] = {}
    type_passed: dict[str, int] = {}
    for c in judged:
        ct = c.get("case_type", "func")
        w = PRIORITY_WEIGHT.get(c.get("priority", "P2"), 2)
        type_weights[ct] = type_weights.get(ct, 0) + w
        if c.get("result") == "pass":
            type_passed[ct] = type_passed.get(ct, 0) + w

    type_scores = {
        ct: (type_passed.get(ct, 0) / type_weights[ct] * 100 if type_weights[ct] > 0 else 100.0)
        for ct in type_weights
    }

    present = {ct: TYPE_WEIGHT.get(ct, 0) for ct in type_scores}
    total_present = sum(present.values())
    if total_present > 0:
        score = sum(type_scores[ct] * w / total_present for ct, w in present.items())
    else:
        score = 100.0

    deduction = 0
    for issue in issues:
        severity = issue.get("severity", "low")
        if severity == "high":
            deduction += 3
        elif severity == "medium":
            deduction += 1
    deduction = min(deduction, 20)
    score = max(0, round(score - deduction))

    has_fail_p0 = any(c.get("result") == "fail" and c.get("priority") == "P0" for c in case_results)
    has_fail_p1 = any(c.get("result") == "fail" and c.get("priority") == "P1" for c in case_results)
    has_severe = any(i.get("severity") == "high" for i in issues)

    if has_fail_p0 or has_severe or score < 60:
        risk = "high"
    elif has_fail_p1 or score < 85:
        risk = "medium"
    else:
        risk = "low"

    total = len(case_results)
    coverage = (len(judged) / total) if total else 1.0

    return {"score": score, "risk_level": risk, "coverage": round(coverage, 4)}
