# AG-UI Provider — Example CopilotKit Frontend

Minimal Next.js app that connects to Agent Zero via the AG-UI protocol.

## Setup

```bash
cd example
npm install
cp .env.local.example .env.local
# Edit .env.local — set AGUI_URL to your AG-UI endpoint
npm run dev
```

Open http://localhost:3000 and start chatting with Agent Zero.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AGUI_URL` | `http://localhost:8401/` | AG-UI endpoint URL |

For remote Agent Zero instances, use the external URL (e.g. `https://your-host.example.com/agui/`).

## How It Works

```
Browser (CopilotKit)  →  Next.js API route  →  AG-UI endpoint (Agent Zero)
     React UI              /api/copilotkit        POST / → SSE stream
```

1. **CopilotKit** renders the chat UI and manages message state
2. **CopilotRuntime** (Next.js API route) bridges CopilotKit's protocol to AG-UI
3. **HttpAgent** sends `RunAgentInput` to your AG-UI endpoint and streams SSE events back
4. **Agent Zero** processes the message and streams thinking, text, and tool call events

## Dev-Only Direct Connection

For quick testing without the Next.js middleware, you can connect the browser directly to the AG-UI endpoint. Replace `page.tsx` with:

```tsx
"use client";

import { HttpAgent } from "@ag-ui/client";
import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

const agent = new HttpAgent({ url: "http://localhost:8401/" });

export default function Home() {
  return (
    <CopilotKit agents__unsafe_dev_only={{ agent_zero: agent }}>
      <CopilotChat />
    </CopilotKit>
  );
}
```

This requires CORS to be enabled on the AG-UI server (enabled by default).

## AG-UI Events

The AG-UI endpoint streams these SSE events:

| Event | When |
|-------|------|
| `RUN_STARTED` | Agent begins processing |
| `THINKING_START/CONTENT/END` | Agent reasoning (streamed) |
| `TEXT_MESSAGE_START/CONTENT/END` | Agent response (streamed) |
| `TOOL_CALL_START/ARGS/END/RESULT` | Agent tool usage |
| `STEP_STARTED/FINISHED` | Agent iteration boundaries |
| `RUN_FINISHED` | Agent done |
| `RUN_ERROR` | Agent error |
