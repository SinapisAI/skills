# Text API contract

Reviewed on 2026-10-12 against the production public OpenAPI and SinapisAI's Mio quickstart. This is a focused text integration reference, not an exhaustive compatibility claim.

## Address and authentication

Use `https://api.sinapisai.com/v1` as the SDK Base URL. For direct HTTP requests, append `/models` or `/chat/completions` to that base. Send the user's API key in the Bearer authorization header; use `Content-Type: application/json` for chat requests. API keys must remain server-side.

Use `SINAPISAI_API_KEY` for the key. Applications may use `SINAPISAI_MODEL` for their selected model ID. The examples default to `sinapisai/mio`; availability depends on the user's key and the current catalog. Copy another model's exact ID from the catalog or the authorized models endpoint, rather than deriving it from its display name.

## Discover accessible models

`GET https://api.sinapisai.com/v1/models` uses the same Bearer header. The expected shape is:

```json
{
  "object": "list",
  "data": [{ "id": "sinapisai/mio", "object": "model" }]
}
```

The example is illustrative. Inspect `data[].id` and do not assume a fixed model count, provider list, price, or permanent availability. The optional model-check script extracts only model IDs.

## Minimal chat

`POST https://api.sinapisai.com/v1/chat/completions`:

```json
{
  "model": "sinapisai/mio",
  "messages": [{ "role": "user", "content": "请用一句话介绍你能做什么。" }],
  "stream": false
}
```

For a text response, read `choices[0].message.content`; handle an absent choice or empty text explicitly. Preserve the response's model and usage when available. Do not log the full response or prompt by default. Optional generation parameters depend on the selected model; start without speculative parameters and add only supported ones the user needs.

## Streaming

The production public OpenAPI currently documents `stream: true` for Chat Completions, returning `text/event-stream`. Use the OpenAI-compatible SDK's stream iterator. Text arrives in `choices[0].delta.content`; some chunks contain only metadata or a finish reason, so missing text is normal. On completion close the local stream. On cancellation or disconnection terminate it and do not automatically restart a generation.

For a native HTTP implementation, use an SSE parser that buffers incomplete UTF-8 and event lines across reads, recognizes empty-line event boundaries, and handles the completion marker. Do not parse each transport chunk as a complete JSON object.

If a deployment returns `stream_not_supported`, explain the limitation. Offer an explicitly selected non-streaming request rather than silently issuing a second request. Re-check current documentation when a capability conflicts with this snapshot.

## Sources and scope

- Production public contract: https://api.sinapisai.com/v3/api-docs/openai-compatible
- Platform: https://sinapis.ai — use its documentation and console links for current guides, API key management, and the model catalog.

Only public Chat Completions and models access are covered here. Do not use internal/admin endpoints or infer account permissions from a successful website login. Support for other endpoints or a coding tool's provider format requires a separate compatibility check.
