---
name: sinapisai-integration
description: Integrate SinapisAI's OpenAI-compatible API into an application or backend service, configure Mio or an explicitly selected model, and diagnose authentication, model access, streaming, or quota errors. Use when the user asks to connect a project to SinapisAI. Installing this skill does not change the coding agent's own model provider.
---

# SinapisAI integration

Help the user connect their application to SinapisAI while preserving its existing architecture and the user's chosen model.

## Start with the project

1. Identify the runtime, existing API client, server boundary, configuration mechanism, and relevant project instructions. Inspect code and variable names; do not read secret files or print environment values.
2. Reuse an existing OpenAI-compatible client or provider adapter when possible. Keep an existing provider available unless the user requests replacing it. Add only the integration required by the task.
3. Clarify application integration versus configuring the coding tool itself if the request is ambiguous. For tool configuration, first check that tool's current official provider documentation; do not invent settings or assume every tool supports this API.

## Connection contract

- SDK Base URL: `https://api.sinapisai.com/v1`.
- Authentication: `Authorization: Bearer <API key>`, supplied by the user's server-side `SINAPISAI_API_KEY` environment variable or existing secret manager. Never request that the user paste a key into chat.
- Start with `POST /v1/chat/completions` for text chat; discover the key's available model IDs through authenticated `GET /v1/models`.
- Preserve the user's explicit model ID. If the user wants Mio, use `sinapisai/mio`; if they have not chosen, propose Mio and verify availability before a live request. Mio's routing is handled by the service; do not implement a second client-side router or promise a specific number of collaborating models.
- Do not append `/v1` twice. Do not assume OpenAI-specific model names, tools, reasoning options, or every OpenAI endpoint are supported.
- Credentials belong on the server. Browser or mobile UI should call the project's authenticated server endpoint, which applies its existing authorization, validation, and rate limits.

Read [the API reference](references/api.md) for request/response shapes, streaming, and current scope. Read [working examples](references/examples.md) only for the runtime and response mode being implemented.

## Implement and verify

1. Add server-side configuration and a secret-free example of required variable names. Tell the user to create an API key in the SinapisAI console and configure it locally if no key is available. Do not create credentials, log in, change budgets, or overwrite secret files as part of installation.
2. Build a minimal chat request using a model available to the user's key. Preserve existing conversation, cancellation, error, and authentication behavior. For streaming, use the SDK's SSE iterator and the project's stream transport; never assume one network chunk equals one event.
3. Run relevant local tests and syntax/type checks. Mock missing/invalid keys, unavailable models, empty or malformed responses, stream cancellation, and quota errors where applicable.
4. When the user authorizes an authenticated connectivity check and has configured a key, the optional [model check script](scripts/check_models.py) performs only one `GET /v1/models`. Run `python3 <skill-directory>/scripts/check_models.py --model sinapisai/mio`, substituting the installed skill's actual directory. It neither creates keys nor sends chat requests; a successful model listing is not proof of a successful generation.
5. Before a live generation, make its potential charge clear and obtain authorization unless the user already requested that specific live test. Use a short, non-sensitive prompt and no automatic retries. Missing authorization or credentials does not prevent completing code and mock validation.
6. Report files changed, model and response mode, checks passed, and what remains unverified. Distinguish offline tests, model access, and a live generation. Do not describe the installation alone as completed API integration.

## Failure handling

Read [troubleshooting](references/troubleshooting.md) when a request fails. Preserve HTTP status and public error codes for controlled diagnostics; do not expose raw server messages, headers, credentials, or private request content in user-facing errors. Stop repeated paid requests on an unknown result or disconnected stream rather than risking duplicate charges.

For image, video, audio, embeddings, Responses API, or tool-specific provider configuration, consult the current official SinapisAI documentation and the requested model's capabilities. This skill's bundled examples cover text Chat Completions only.
