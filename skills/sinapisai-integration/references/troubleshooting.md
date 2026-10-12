# Troubleshooting

Inspect HTTP status and the public `error.type` / `error.code` when present. Keep the raw error and request content out of user-facing messages. Never print Authorization headers, API keys, secret files, or full SDK exception objects.

| Symptom | Action |
| --- | --- |
| Missing key locally | Explain how to configure server-side `SINAPISAI_API_KEY`; finish code and mock tests without a live request. |
| 401 | Check the variable is available to the server process and the Bearer header is set once. Ask the user to check key validity; do not ask them to disclose it. |
| 403 / `model_not_allowed` | Verify the exact model ID is available to that key. Preserve the requested model and explain access requirements; do not silently switch to another model. |
| 400 / `invalid_model` | Copy the exact ID from the current authorized catalog. Do not use a display name or guess a provider prefix. |
| 400 / unsupported parameter or capability | Remove only unsupported options or select a compatible model with the user. Start from the minimal chat request. |
| `stream_not_supported` | Report the environment limitation and offer non-streaming. Do not automatically issue a fallback generation. |
| 404 | Check the public Base URL and ensure `/v1` occurs once; confirm the endpoint and model rather than trying private endpoints. |
| 429 / `insufficient_quota` | Stop retries. Ask the user to check balance, key budget, or limits in the console. |
| 429 / `rate_limit_exceeded` | Lower concurrency. Add bounded backoff only if appropriate to the application's explicit retry policy and duplicate-charge risk. |
| 5xx, timeout, or interrupted SSE | Surface a recoverable failure and preserve the draft. An unknown request outcome can have incurred usage; do not replay it automatically. |
| Empty text or missing choice | Handle it explicitly rather than rendering `undefined` or marking a successful generation. Check the response mode and supported model output. |

The starter SDK examples disable retries. If a product needs retries, design a bounded policy for its request semantics; do not treat a timeout, half-read stream, or cancellation as proof that no request ran. Use only documented request identifiers for support, without private prompts or credentials.

Check current official documentation for endpoints beyond text Chat Completions, model-specific parameters, and coding tool configuration. The installed skill adds knowledge; it does not grant account permissions or guarantee every coding tool can use SinapisAI as its own provider.
