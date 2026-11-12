"""模型调用计量回调。

在 LangChain 调用链上挂载本回调，累积单次 Agent 执行的 token 用量，
用于成本控制与主动发现开关判断（R97）。
"""

from typing import Any

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult


def _extract_tokens(usage: Any) -> tuple[int, int]:
    """从 usage 中解析 (input_tokens, output_tokens)，兼容对象与字典两种形态。"""
    if usage is None:
        return 0, 0
    if isinstance(usage, dict):
        return usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
    prompt = getattr(usage, "prompt_tokens", 0)
    completion = getattr(usage, "completion_tokens", 0)
    return prompt or 0, completion or 0


class TokenUsageCallback(BaseCallbackHandler):
    """累积单次 Agent 调用的 token 用量。"""

    def __init__(self, agent: str) -> None:
        super().__init__()
        self.agent = agent
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        usage = response.llm_output.get("token_usage") if response.llm_output else None
        prompt, completion = _extract_tokens(usage)
        self.input_tokens += prompt
        self.output_tokens += completion
