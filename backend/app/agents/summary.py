"""报告摘要 Agent：撰写结论摘要（RPT-04 结论先行）。"""

import json
from typing import Any

from langchain_core.prompts import PromptTemplate

from app.agents.base import BaseAgent
from app.models import ModelConfig

_SUMMARY_PROMPT = PromptTemplate.from_template(
    """你是资深测试负责人。根据以下测试结果，撰写一份结论摘要。

要求：
1. 结论先行：先给出整体结论，再概括主要风险与建议。
2. 150 字以内，中文，直接输出摘要正文，不要输出 JSON 或任何标记。

综合评分：{score} 分
风险等级：{risk_level}
主要问题：
{top_issues}
"""
)


class SummaryAgent(BaseAgent):
    """报告摘要 Agent。"""

    name = "summary"

    def __init__(self, model_config: ModelConfig) -> None:
        super().__init__(model_config)
        self.chain = _SUMMARY_PROMPT | self.llm

    def run(self, score: int, risk_level: str, top_issues: list[dict[str, Any]]) -> str:
        result = self.chain.invoke(
            {
                "score": score,
                "risk_level": risk_level,
                "top_issues": json.dumps(top_issues, ensure_ascii=False, default=str),
            },
            config={"callbacks": [self.usage]},
        )
        return result.content.strip()
