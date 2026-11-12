"""能力层：LLM 客户端、Agent 编排、调用计量。

- `llm_client`：统一构建 LangChain ChatOpenAI 实例；
- `callbacks`：token 用量计量回调；
- `metrics`：调用计量落库；
- `base`：Agent 抽象基类。
"""

from app.agents.base import BaseAgent
from app.agents.llm_client import build_chat_model

__all__ = ["BaseAgent", "build_chat_model"]
