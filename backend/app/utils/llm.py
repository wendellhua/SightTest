"""模型连通性与图片识别检测。

用于模型配置保存前的校验（需求 LLM-05）。检测按指定模型名称直接探测，
后续阶段 3 的完整 LLM 客户端（LangChain 编排）在此基础上扩展。
"""

from dataclasses import dataclass

import httpx

# 1x1 透明 PNG，用作图片识别能力探测
_PROBE_IMAGE = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
)


@dataclass
class ModelCheckResult:
    ok: bool
    supports_vision: bool
    message: str


async def check_model(base_url: str, api_key: str, model: str) -> ModelCheckResult:
    """检测指定模型的连通性与图片识别能力。"""
    headers = {"Authorization": f"Bearer {api_key}"}
    base = base_url.rstrip("/")

    async with httpx.AsyncClient(timeout=20.0) as client:
        if not await _ping_chat(client, base, headers, model):
            return ModelCheckResult(False, False, "无法连接模型服务，请检查 Base URL、API Key 与模型名称")
        supports_vision = await _probe_vision(client, base, headers, model)

    message = "ok" if supports_vision else "模型可连接，但不支持图片识别"
    return ModelCheckResult(True, supports_vision, message)


async def _ping_chat(client: httpx.AsyncClient, base: str, headers: dict, model: str) -> bool:
    """发送最小文本对话请求，检测连通性。"""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 5,
    }
    try:
        resp = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
        return resp.status_code == 200
    except httpx.HTTPError:
        return False


async def _probe_vision(client: httpx.AsyncClient, base: str, headers: dict, model: str) -> bool:
    """发送带图片的对话请求，探测是否支持图片识别。"""
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "这张图片是什么颜色？"},
                    {"type": "image_url", "image_url": {"url": _PROBE_IMAGE}},
                ],
            }
        ],
        "max_tokens": 10,
    }
    try:
        resp = await client.post(f"{base}/chat/completions", headers=headers, json=payload)
        return resp.status_code == 200
    except httpx.HTTPError:
        return False
