"""日志配置。

统一日志格式，禁止打印 token、密码、API Key 等敏感信息；内部失败原因只进日志。
"""

import logging
import sys


def setup_logging(debug: bool = False) -> None:
    """初始化根日志器。"""
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    )
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)

    # 降低第三方库噪音
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
