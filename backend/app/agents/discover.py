"""主动发现 Agent：基于页面快照与执行结果，发现额外问题（R97）。"""

import json
import re
from typing import Any

from langchain_core.prompts import PromptTemplate

from app.agents.base import BaseAgent
from app.models import ModelConfig

_DISCOVER_PROMPT = PromptTemplate.from_template(
    """你是资深测试分析师。根据被测网站的页面快照与用例执行结果，主动发现用例断言之外的问题。

关注点：页面交互隐患、明显缺失的功能入口、文案/链接异常、可能影响体验的一致性问题。

要求：
1. 只输出 JSON 数组，每个元素为 {{"page": "问题所在页面或路径", "severity": "high/medium/low", "description": "问题描述"}}
2. 没有发现问题时输出空数组 []。
3. 只输出 JSON，不要输出其他文字或 Markdown 代码块标记。

页面快照：
{snapshot}

用例执行结果摘要：
{summary}
"""
)


def parse_json_array(text: str) -> list[dict[str, Any]]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return []


class DiscoverAgent(BaseAgent):
    """主动发现 Agent。"""

    name = "discover"

    def __init__(self, model_config: ModelConfig) -> None:
        super().__init__(model_config)
        self.chain = _DISCOVER_PROMPT | self.llm

    def run(self, snapshot: dict[str, Any], summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
        result = self.chain.invoke(
            {
                "snapshot": json.dumps(snapshot, ensure_ascii=False, default=str),
                "summary": json.dumps(summary, ensure_ascii=False, default=str),
            },
            config={"callbacks": [self.usage]},
        )
        return parse_json_array(result.content)
