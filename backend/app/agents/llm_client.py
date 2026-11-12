"""LLM 客户端：基于 LangChain ChatOpenAI 的统一工厂。

所有 Agent 通过此工厂构建模型实例，统一走项目绑定的模型配置（OpenAI 兼容），
并固定 `temperature=0` 以保证结果可复现（R30、R70）。
"""

from langchain_openai import ChatOpenAI

from app.core.security import decrypt_secret
from app.models import ModelConfig


def build_chat_model(model_config: ModelConfig) -> ChatOpenAI:
    """从模型配置构建 ChatOpenAI 实例（支持图片识别）。"""
    return ChatOpenAI(
        model=model_config.model,
        base_url=model_config.base_url,
        api_key=decrypt_secret(model_config.api_key_encrypted),
        temperature=0,
    )
