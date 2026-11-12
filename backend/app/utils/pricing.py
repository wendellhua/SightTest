"""大模型 token 价格表（元/百万 token）。

依据需求附录 A-20，价格为 2026-11-12 外网查询结果。
计价口径（USAGE-03）：峰谷定价按高峰价、缓存命中按未命中计（保守上界）。
"""

MODEL_PRICING: dict[str, dict[str, float]] = {
    # DeepSeek
    "deepseek-flash": {"input": 2.0, "output": 8.0},
    "deepseek-v4-pro": {"input": 9.0, "output": 27.0},
    "deepseek-chat": {"input": 2.0, "output": 8.0},
    "deepseek-reasoner": {"input": 9.0, "output": 27.0},
    # 其他国内主流
    "glm-5.3": {"input": 8.0, "output": 28.0},
    "glm-5.3-flash": {"input": 0.8, "output": 2.8},
    "qwen3.7-max": {"input": 12.0, "output": 36.0},
    "doubao-2.1-pro": {"input": 6.0, "output": 30.0},
    "kimi-k2.6": {"input": 6.5, "output": 27.0},
    "kimi-k3": {"input": 20.0, "output": 100.0},
}


def get_pricing(model_name: str | None) -> dict[str, float] | None:
    """返回 {input, output}（元/百万 token），未匹配返回 None。"""
    if not model_name:
        return None
    name = model_name.lower().strip()
    if name in MODEL_PRICING:
        return MODEL_PRICING[name]
    best: tuple[int, dict[str, float]] | None = None
    for key, pricing in MODEL_PRICING.items():
        if key in name or name in key:
            if best is None or len(key) > best[0]:
                best = (len(key), pricing)
    return best[1] if best else None


def calc_cost(model_name: str | None, input_tokens: int, output_tokens: int) -> float | None:
    """计算成本（元，精确到分）；价格未匹配返回 None。"""
    pricing = get_pricing(model_name)
    if pricing is None:
        return None
    return round(
        input_tokens / 1_000_000 * pricing["input"]
        + output_tokens / 1_000_000 * pricing["output"],
        2,
    )
