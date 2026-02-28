"""
AG-UI event encoding helpers.

Produces SSE-formatted strings ready for streaming.
Follows the AG-UI protocol spec (github.com/ag-ui-protocol/ag-ui).
All field names are camelCase on the wire. None values are excluded.
"""

import json
import time
import uuid


def _sse(data: dict) -> str:
    """Encode a dict as an SSE data line. Excludes None values."""
    cleaned = {k: v for k, v in data.items() if v is not None}
    return f"data: {json.dumps(cleaned)}\n\n"


def _ts() -> int:
    """Current timestamp in milliseconds."""
    return int(time.time() * 1000)


def _uuid() -> str:
    return str(uuid.uuid4())


# ── Lifecycle Events ──

def encode_run_started(thread_id: str, run_id: str) -> str:
    return _sse({
        "type": "RUN_STARTED",
        "threadId": thread_id,
        "runId": run_id,
        "timestamp": _ts(),
    })


def encode_run_finished(thread_id: str, run_id: str, result: str = None) -> str:
    return _sse({
        "type": "RUN_FINISHED",
        "threadId": thread_id,
        "runId": run_id,
        "result": result,
        "timestamp": _ts(),
    })


def encode_run_error(message: str, code: str = "agent_error") -> str:
    return _sse({
        "type": "RUN_ERROR",
        "message": message,
        "code": code,
        "timestamp": _ts(),
    })


# ── Step Events ──

def encode_step_started(step_name: str) -> str:
    return _sse({
        "type": "STEP_STARTED",
        "stepName": step_name,
        "timestamp": _ts(),
    })


def encode_step_finished(step_name: str) -> str:
    return _sse({
        "type": "STEP_FINISHED",
        "stepName": step_name,
        "timestamp": _ts(),
    })


# ── Text Message Events ──

def encode_text_message_start(message_id: str = None, role: str = "assistant") -> str:
    return _sse({
        "type": "TEXT_MESSAGE_START",
        "messageId": message_id or _uuid(),
        "role": role,
        "timestamp": _ts(),
    })


def encode_text_message_content(message_id: str, delta: str) -> str:
    if not delta:  # spec requires min_length=1
        return ""
    return _sse({
        "type": "TEXT_MESSAGE_CONTENT",
        "messageId": message_id,
        "delta": delta,
        "timestamp": _ts(),
    })


def encode_text_message_end(message_id: str) -> str:
    return _sse({
        "type": "TEXT_MESSAGE_END",
        "messageId": message_id,
        "timestamp": _ts(),
    })


# ── Reasoning Events (replaces deprecated THINKING_*) ──

def encode_reasoning_start(message_id: str) -> str:
    return _sse({
        "type": "REASONING_START",
        "messageId": message_id,
        "timestamp": _ts(),
    })


def encode_reasoning_message_start(message_id: str) -> str:
    return _sse({
        "type": "REASONING_MESSAGE_START",
        "messageId": message_id,
        "role": "reasoning",
        "timestamp": _ts(),
    })


def encode_reasoning_message_content(message_id: str, delta: str) -> str:
    if not delta:  # spec requires min_length=1
        return ""
    return _sse({
        "type": "REASONING_MESSAGE_CONTENT",
        "messageId": message_id,
        "delta": delta,
        "timestamp": _ts(),
    })


def encode_reasoning_message_end(message_id: str) -> str:
    return _sse({
        "type": "REASONING_MESSAGE_END",
        "messageId": message_id,
        "timestamp": _ts(),
    })


def encode_reasoning_end(message_id: str) -> str:
    return _sse({
        "type": "REASONING_END",
        "messageId": message_id,
        "timestamp": _ts(),
    })


# ── Deprecated aliases (backward compat) ──

def encode_thinking_start(title: str = "Thinking...") -> str:
    """Deprecated: use encode_reasoning_start."""
    return encode_reasoning_start(_uuid())


def encode_thinking_end() -> str:
    """Deprecated: use encode_reasoning_end."""
    return encode_reasoning_end(_uuid())


def encode_thinking_content(delta: str) -> str:
    """Deprecated: use encode_reasoning_message_content."""
    return encode_reasoning_message_content(_uuid(), delta)


# ── Tool Call Events ──

def encode_tool_call_start(tool_call_id: str, tool_name: str,
                           parent_message_id: str = None) -> str:
    return _sse({
        "type": "TOOL_CALL_START",
        "toolCallId": tool_call_id,
        "toolCallName": tool_name,
        "parentMessageId": parent_message_id,
        "timestamp": _ts(),
    })


def encode_tool_call_args(tool_call_id: str, args_json: str) -> str:
    return _sse({
        "type": "TOOL_CALL_ARGS",
        "toolCallId": tool_call_id,
        "delta": args_json,
        "timestamp": _ts(),
    })


def encode_tool_call_end(tool_call_id: str) -> str:
    return _sse({
        "type": "TOOL_CALL_END",
        "toolCallId": tool_call_id,
        "timestamp": _ts(),
    })


def encode_tool_call_result(tool_call_id: str, content: str,
                            message_id: str = None) -> str:
    return _sse({
        "type": "TOOL_CALL_RESULT",
        "messageId": message_id or _uuid(),
        "toolCallId": tool_call_id,
        "content": content,
        "role": "tool",
        "timestamp": _ts(),
    })


# ── State Events ──

def encode_state_snapshot(snapshot: dict) -> str:
    return _sse({
        "type": "STATE_SNAPSHOT",
        "snapshot": snapshot,
        "timestamp": _ts(),
    })


def encode_messages_snapshot(messages: list) -> str:
    return _sse({
        "type": "MESSAGES_SNAPSHOT",
        "messages": messages,
        "timestamp": _ts(),
    })


# ── Custom Events ──

def encode_custom(name: str, value) -> str:
    return _sse({
        "type": "CUSTOM",
        "name": name,
        "value": value,
        "timestamp": _ts(),
    })
