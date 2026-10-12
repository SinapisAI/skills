#!/usr/bin/env python3
"""Check model access with one GET; never create a key or start a generation."""

import argparse
import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

MODELS_URL = "https://api.sinapisai.com/v1/models"
MAX_RESPONSE_BYTES = 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    """Do not forward the Bearer header to a redirected destination."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def model_ids(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise ValueError("Invalid model list")
    ids = []
    for row in payload["data"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("Invalid model ID")
        model_id = row["id"]
        if not model_id or any(ord(char) < 32 or ord(char) == 127 for char in model_id):
            raise ValueError("Invalid model ID")
        ids.append(model_id)
    return sorted(set(ids))


def main(argv=None, environ=None, opener=None):
    parser = argparse.ArgumentParser(description="检查 SinapisAI 密钥可访问的模型，不发送对话。")
    parser.add_argument("--model", default="sinapisai/mio", help="检查的完整模型 ID")
    parser.add_argument("--list", action="store_true", help="仅列出可访问模型 ID")
    args = parser.parse_args(argv)
    env = os.environ if environ is None else environ
    api_key = env.get("SINAPISAI_API_KEY", "")
    if not api_key or any(ord(char) < 33 or ord(char) > 126 for char in api_key):
        print("请在服务端环境中配置有效的 SINAPISAI_API_KEY，不要把密钥粘贴到聊天中。", file=sys.stderr)
        return 1

    request = Request(MODELS_URL, headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"}, method="GET")
    http = build_opener(NoRedirect()) if opener is None else opener
    try:
        with http.open(request, timeout=20) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("Response too large")
        ids = model_ids(json.loads(body))
    except HTTPError as error:
        status = error.code
        error.close()
        actions = {401: "请检查密钥是否有效。", 403: "请检查密钥权限。", 429: "请检查调用频率、余额或密钥限额。"}
        print(f"模型检查失败（HTTP {status}）。" + actions.get(status, "请检查接口地址或稍后重试。"), file=sys.stderr)
        return 1
    except (URLError, TimeoutError, OSError):
        print("模型检查未完成，请检查网络连接。", file=sys.stderr)
        return 1
    except (ValueError, TypeError):
        print("模型列表返回内容无法识别，请检查当前接口文档。", file=sys.stderr)
        return 1

    if args.list:
        for model_id in ids:
            print(model_id)
        return 0
    if args.model not in ids:
        print("当前密钥未返回所选模型，请核对模型 ID 和访问权限。", file=sys.stderr)
        return 2
    print("模型访问检查通过；尚未发送对话或验证生成结果。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
