# Server-side examples

These are application integration examples. Running a chat example sends a real request and may incur usage charges. Configure `SINAPISAI_API_KEY` privately in the server environment; do not paste it into a prompt or commit it. `SINAPISAI_MODEL` is optional and defaults to `sinapisai/mio`; verify it is available to the key first.

Prefer a project's existing compatible SDK. For a new Node.js project the example uses the `openai` package; for Python it uses the `openai` package. Install a version compatible with the project's runtime and lockfile. These dependencies are not installed by this skill.

## Node.js (ES module)

Save as `sinapisai-chat.mjs` in a server project that has the SDK installed. Supply a short non-sensitive test prompt. Set `SINAPISAI_STREAM=1` only when streaming is desired.

```javascript
import OpenAI from 'openai';

const apiKey = process.env.SINAPISAI_API_KEY;
const prompt = process.argv[2];
if (!apiKey || !prompt) {
  console.error('请在服务端配置 SINAPISAI_API_KEY，并提供测试问题。');
  process.exit(1);
}

const client = new OpenAI({
  apiKey,
  baseURL: 'https://api.sinapisai.com/v1',
  maxRetries: 0,
  timeout: 30_000,
});
const model = process.env.SINAPISAI_MODEL || 'sinapisai/mio';
const messages = [{ role: 'user', content: prompt }];
const controller = new AbortController();
process.once('SIGINT', () => controller.abort());

try {
  if (process.env.SINAPISAI_STREAM === '1') {
    const stream = await client.chat.completions.create(
      { model, messages, stream: true },
      { signal: controller.signal },
    );
    let receivedText = false;
    for await (const chunk of stream) {
      const text = chunk.choices?.[0]?.delta?.content;
      if (typeof text === 'string' && text) {
        receivedText = true;
        process.stdout.write(text);
      }
    }
    if (!receivedText) throw new Error('No text returned');
    process.stdout.write('\n');
  } else {
    const result = await client.chat.completions.create(
      { model, messages, stream: false },
      { signal: controller.signal },
    );
    const text = result.choices?.[0]?.message?.content;
    if (typeof text !== 'string' || !text) throw new Error('No text returned');
    console.log(text);
  }
} catch (error) {
  const status = error instanceof OpenAI.APIError ? error.status : undefined;
  console.error(status ? `调用失败（HTTP ${status}），请检查接入配置。` : '调用未完成，请检查网络或返回内容。');
  process.exitCode = 1;
}
```

The example writes the requested model text to the terminal, but never prints the key, raw errors, request headers, or automatic retries. In an application, return text through its existing authenticated response path and bind request cancellation to the controller.

## Python

Save as `sinapisai_chat.py` in a server project that has the SDK installed. The SDK context manager closes the HTTP client; the stream context manager closes the response even if iteration is interrupted.

```python
import os
import sys

from openai import APIError, OpenAI

api_key = os.environ.get("SINAPISAI_API_KEY")
if not api_key or len(sys.argv) < 2:
    sys.exit("请在服务端配置 SINAPISAI_API_KEY，并提供测试问题。")

model = os.environ.get("SINAPISAI_MODEL") or "sinapisai/mio"
messages = [{"role": "user", "content": sys.argv[1]}]

try:
    with OpenAI(
        api_key=api_key,
        base_url="https://api.sinapisai.com/v1",
        max_retries=0,
        timeout=30.0,
    ) as client:
        if os.environ.get("SINAPISAI_STREAM") == "1":
            received_text = False
            with client.chat.completions.create(
                model=model, messages=messages, stream=True
            ) as stream:
                for chunk in stream:
                    text = chunk.choices[0].delta.content if chunk.choices else None
                    if text:
                        received_text = True
                        print(text, end="", flush=True)
            if not received_text:
                raise ValueError("No text returned")
            print()
        else:
            result = client.chat.completions.create(
                model=model, messages=messages, stream=False
            )
            text = result.choices[0].message.content if result.choices else None
            if not text:
                raise ValueError("No text returned")
            print(text)
except APIError as error:
    status = getattr(error, "status_code", None)
    sys.exit(f"调用失败（HTTP {status}），请检查接入配置。" if status else "调用未完成，请检查网络。")
except (ValueError, KeyboardInterrupt):
    sys.exit("调用未完成或未返回文字，请检查返回内容。")
```

## Verification without a chat generation

The bundled `scripts/check_models.py` uses Python's standard library. It sends only one authorized model-list request and can check an exact model ID:

```bash
python3 <skill-directory>/scripts/check_models.py --model sinapisai/mio
```

Replace `<skill-directory>` with the installed skill's real path. Use `--list` to print only accessible model IDs. A model-list success validates authentication and catalog access, not text generation, tool capabilities, billing, or streaming.
