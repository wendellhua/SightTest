"""产品分析 Agent：从探索快照梳理被测网站的功能模块。"""

import json
import re
from typing import Any, cast

from langchain_core.prompts import PromptTemplate

from app.agents.base import BaseAgent
from app.models import ModelConfig

_ANALYZE_PROMPT = PromptTemplate.from_template(
    """你是资深测试产品分析师。根据被测网站首页的探索快照，梳理该网站的功能模块。

要求：
1. 只输出 JSON 数组，每个元素为 {{"name": "模块名", "description": "模块职责", "pages": ["相关页面路径或入口"]}}
2. 不要输出 JSON 以外的任何文字或 Markdown 代码块标记。

探索快照：
{snapshot}
"""
)


def parse_json_array(text: str) -> list[dict[str, Any]]:
    """从 LLM 输出中解析 JSON 数组，剥离可能的代码块标记。"""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return cast(list[dict[str, Any]], json.loads(cleaned))
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if match:
            return cast(list[dict[str, Any]], json.loads(match.group(0)))
        raise


class AnalyzeAgent(BaseAgent):
    """产品分析 Agent。"""

    name = "analyze"

    def __init__(self, model_config: ModelConfig) -> None:
        super().__init__(model_config)
        self.chain = _ANALYZE_PROMPT | self.llm

    def run(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        text = json.dumps(snapshot, ensure_ascii=False, default=str)
        result = self.chain.invoke({"snapshot": text}, config={"callbacks": [self.usage]})
        return parse_json_array(self._text_content(result))
