"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" agent="agent_zero">
      <div
        style={{
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          background: "#0a0a0a",
        }}
      >
        <header
          style={{
            padding: "12px 20px",
            borderBottom: "1px solid #222",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <rect width="24" height="24" rx="6" fill="#6366f1" />
            <path
              d="M7 12h10M12 7v10"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
            />
            <circle cx="7" cy="12" r="1.5" fill="white" />
            <circle cx="17" cy="12" r="1.5" fill="white" />
            <circle cx="12" cy="7" r="1.5" fill="white" />
            <circle cx="12" cy="17" r="1.5" fill="white" />
          </svg>
          <span style={{ color: "#fff", fontWeight: 600, fontSize: "0.95em" }}>
            Agent Zero
          </span>
          <span style={{ color: "#666", fontSize: "0.8em" }}>via AG-UI</span>
        </header>
        <div style={{ flex: 1, overflow: "hidden" }}>
          <CopilotChat
            labels={{
              title: "Agent Zero",
              initial: "Connected to Agent Zero. How can I help?",
              placeholder: "Type a message...",
            }}
          />
        </div>
      </div>
    </CopilotKit>
  );
}
