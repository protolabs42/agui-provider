# AG-UI Provider — Agent Zero Plugin

Expose Agent Zero as an [AG-UI](https://docs.ag-ui.com) compatible agent server. Any CopilotKit, React, or AG-UI-compatible frontend can connect and interact with your Agent Zero instance via streaming SSE.

## What It Does

- Starts an AG-UI SSE server (default port `8401`)
- Accepts `RunAgentInput` POST requests from AG-UI clients
- Creates a background Agent Zero context per run
- Streams AG-UI events in real-time: reasoning, text, tool calls, steps

## AG-UI Events Mapped

| A0 Extension Hook | AG-UI Event |
|---|---|
| `monologue_start` | `STEP_STARTED` |
| `reasoning_stream_chunk` | `REASONING_START`, `REASONING_MESSAGE_START`, `REASONING_MESSAGE_CONTENT` |
| `response_stream_chunk` | `REASONING_MESSAGE_END`, `REASONING_END`, `TEXT_MESSAGE_START`, `TEXT_MESSAGE_CONTENT` |
| `response_stream_end` | `TEXT_MESSAGE_END` |
| `tool_execute_before` | `TOOL_CALL_START`, `TOOL_CALL_ARGS` |
| `tool_execute_after` | `TOOL_CALL_END`, `TOOL_CALL_RESULT` |
| `message_loop_end` | `STEP_FINISHED` |
| `process_chain_end` | cleanup |

Plus `RUN_STARTED`, `RUN_FINISHED`, `RUN_ERROR` lifecycle events.

## Installation

Requires Agent Zero **development branch** (plugin system).

```bash
cd /path/to/agent-zero
git clone https://github.com/protolabs42/agui-provider.git usr/plugins/agui-provider
```

Or inside a Docker container:

```bash
docker exec agent-zero git clone https://github.com/protolabs42/agui-provider.git /a0/usr/plugins/agui-provider
```

Restart Agent Zero. The plugin auto-starts on first message.

## Configuration

Default settings in `default_config.yaml`:

| Setting | Default | Description |
|---|---|---|
| `port` | `8401` | SSE server listen port |
| `auto_start` | `true` | Start server on first agent message |
| `auth_token` | *auto-generated* | Bearer token for API authentication |
| `cors_origins` | `""` | CORS allowed origins (empty = same-origin only) |
| `max_concurrent_runs` | `5` | Max simultaneous agent runs (429 when exceeded) |
| `max_body_size` | `1048576` | Request body size limit in bytes (1 MB) |

Configure via the Agent Zero plugin settings UI, or create `config.json` in the plugin directory.

### CORS Origins

- Empty string `""` — same-origin only (default, most secure)
- `"*"` — allow any origin
- Comma-separated list — `"https://app.example.com, https://dev.example.com"`

### Authentication

A secure auth token is **automatically generated** on first run using `secrets.token_urlsafe(32)` and persisted to `config.json`. All requests must include it:

```bash
curl -N -X POST http://localhost:8401/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "hello"}]}'
```

Find your token in the plugin dashboard (click "Open" on AG-UI Provider) or in `config.json`. You can also set a custom token in the plugin settings.

## Usage

### Health Check

```bash
curl http://localhost:8401/health
```

### Send a Message (AG-UI protocol)

```bash
curl -N -X POST http://localhost:8401/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "threadId": "thread-1",
    "runId": "run-1",
    "messages": [
      {"role": "user", "content": "Hello, what can you do?"}
    ]
  }'
```

The response is an SSE stream of AG-UI events.

### CopilotKit Integration

See the `example/` directory for a complete Next.js + CopilotKit frontend.

```typescript
import { CopilotRuntime, ExperimentalEmptyAdapter } from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";

const agent = new HttpAgent({ url: "http://your-a0-host:8401/" });

const runtime = new CopilotRuntime({
  agents: { agent },
});
```

## Architecture

```
AG-UI Client (CopilotKit/React)
    │
    ▼ POST / (SSE)
┌──────────────────────┐
│  aiohttp SSE Server  │  ← agui_server.py (port 8401)
│  (dedicated thread)  │
└──────┬───────────────┘
       │ subscribe(run_id)
┌──────▼───────────────┐
│  Thread-safe Queue   │  ← event_bus.py (stdlib queue.Queue)
│  (per run_id)        │
└──────▲───────────────┘
       │ emit(run_id, event)
┌──────┴───────────────┐
│  A0 Extensions       │  ← 9 hook points (DeferredTask thread)
│  (agent processing)  │
└──────────────────────┘
```

The event bus uses `queue.Queue` (thread-safe) because Agent Zero processes messages in `DeferredTask` threads with separate event loops, while the SSE server runs in a dedicated aiohttp event loop on its own daemon thread.

## Security

- **Auth**: Secure token auto-generated on first run, constant-time comparison (`hmac.compare_digest`)
- **CORS**: Origin allowlist validation (default: same-origin only)
- **Rate limiting**: Concurrent run cap with 429 rejection (default: 5)
- **Body size**: Configurable request size limit (default 1 MB, rejects with 413)
- **Error sanitization**: Only exception class names are sent to clients, never stack traces

## File Structure

```
agui-provider/
├── plugin.yaml              # Plugin manifest
├── default_config.yaml      # Default settings
├── api/
│   └── status.py            # Status/start/stop API
├── agui_helpers/
│   ├── __init__.py
│   ├── agui_server.py       # Core SSE server + context management
│   ├── agui_events.py       # AG-UI event encoding (16 event types)
│   └── event_bus.py         # Thread-safe pub/sub queue
├── webui/
│   ├── main.html            # Plugin dashboard (status, controls)
│   ├── config.html          # Settings panel
│   └── agui-store.js        # Alpine.js store
├── example/                 # CopilotKit + Next.js frontend example
└── extensions/python/
    ├── monologue_start/      → StepStarted
    ├── reasoning_stream_chunk/ → ReasoningStart/MessageStart/Content
    ├── response_stream_chunk/  → ReasoningEnd/TextMessageStart/Content
    ├── response_stream_end/    → TextMessageEnd
    ├── tool_execute_before/    → ToolCallStart/Args
    ├── tool_execute_after/     → ToolCallEnd/Result
    ├── message_loop_start/     → Auto-start server
    ├── message_loop_end/       → StepFinished
    └── process_chain_end/      → Cleanup
```

## License

MIT
