"""UI 判定 Agent：基于页面快照判定用例执行结果。"""

import json
import re
from typing import Any

from langchain_core.prompts import PromptTemplate

from app.agents.base import BaseAgent
from app.models import ModelConfig

_JUDGE_PROMPT = PromptTemplate.from_template(
    """你是资深测试判定员。根据被测网站的页面快照，判定给定用例的执行结果。

要求：
1. 只输出一个 JSON 对象：{{"result": "pass/fail/blocked", "reason": "判定理由（一句话）"}}
2. result 取值：pass 通过、fail 不通过（页面与预期不符或存在错误）、blocked 无法执行（页面缺少用例所需入口/功能）。
3. 只输出 JSON，不要输出其他文字或 Markdown 代码块标记。

页面快照：
{snapshot}

待判定用例：
- 名称：{name}
- 执行步骤：{steps}
- 预期结果：{expect}
"""
)


def parse_json_object(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class JudgeAgent(BaseAgent):
    """UI 判定 Agent。"""

    name = "judge"

    def __init__(self, model_config: ModelConfig) -> None:
        super().__init__(model_config)
        self.chain = _JUDGE_PROMPT | self.llm

    def run(self, snapshot: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
        result = self.chain.invoke(
            {
                "snapshot": json.dumps(snapshot, ensure_ascii=False, default=str),
                "name": case.get("name", ""),
                "steps": case.get("steps", ""),
                "expect": case.get("expect", ""),
            },
            config={"callbacks": [self.usage]},
        )
        return parse_json_object(result.content)
