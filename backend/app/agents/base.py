"""Agent 抽象基类。

所有 Agent（登录/探索/分析/用例生成/UI 判定/报告摘要等）继承本类，
统一通过 `self.llm` 调用项目绑定的模型，并挂载 token 计量回调。
子类在 Celery Worker 内同步执行（规范 A3）。
"""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseChatModel

from app.agents.callbacks import TokenUsageCallback
from app.agents.llm_client import build_chat_model
from app.models import ModelConfig


class BaseAgent(ABC):
    """Agent 基类。

    属性：
        model_config：项目绑定的模型配置；
        llm：LangChain ChatOpenAI 实例（temperature=0 可复现）；
        usage：token 用量计量回调，执行结束后读取其 input_tokens/output_tokens。
    """

    name: str = "base"

    def __init__(self, model_config: ModelConfig) -> None:
        self.model_config = model_config
        self.llm: BaseChatModel = build_chat_model(model_config)
        self.usage = TokenUsageCallback(self.name)

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """执行 Agent 逻辑，返回业务结果。"""
        raise NotImplementedError
