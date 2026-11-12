"""用例生成 Agent：基于功能模块生成功能测试用例。"""

import json
import re
from typing import Any

from langchain_core.prompts import PromptTemplate

from app.agents.base import BaseAgent
from app.models import ModelConfig

_CASE_GEN_PROMPT = PromptTemplate.from_template(
    """你是资深测试工程师。根据被测网站的功能模块清单，生成功能测试用例。

要求：
1. 只输出 JSON 数组，每个元素结构如下：
   {{"name": "用例名称", "module_path": "模块/子模块", "page": "所属页面", "priority": "P0/P1/P2/P3", "precondition": "前置条件", "steps": "执行步骤", "expect": "预期结果"}}
2. priority 按重要性：核心主流程 P0、重要功能 P1、一般 P2、边缘 P3。
3. 覆盖每个模块的核心增删改查与页面访问，避免重复。
4. 只输出 JSON，不要输出其他文字或 Markdown 代码块标记。

功能模块清单：
{modules}
"""
)


def parse_json_array(text: str) -> list[dict[str, Any]]:
    """从 LLM 输出中解析 JSON 数组，剥离可能的代码块标记。"""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


class CaseGenAgent(BaseAgent):
    """用例生成 Agent。"""

    name = "case_gen"

    def __init__(self, model_config: ModelConfig) -> None:
        super().__init__(model_config)
        self.chain = _CASE_GEN_PROMPT | self.llm

    def run(self, modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
        text = json.dumps(modules, ensure_ascii=False, default=str)
        result = self.chain.invoke({"modules": text}, config={"callbacks": [self.usage]})
        return parse_json_array(result.content)
