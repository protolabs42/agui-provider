"""
AG-UI event bus — thread-safe queue connecting A0 extensions to SSE clients.

Extensions emit AG-UI events via emit(). The SSE server subscribes per run_id
and streams events to connected AG-UI clients.

Thread-safety: A0 runs agent processing in DeferredTask threads (separate event
loops). The SSE server runs in the main aiohttp event loop. We use stdlib
queue.Queue + threading.Lock so emit() works from any thread.
"""

import logging
import threading
import queue as stdlib_queue
from collections import defaultdict

logger = logging.getLogger("agui-provider")

# run_id → list of queue.Queue (one per connected client)
_subscribers: dict[str, list[stdlib_queue.Queue]] = defaultdict(list)
_lock = threading.Lock()


def subscribe(run_id: str) -> stdlib_queue.Queue:
    """Subscribe to events for a run. Returns a thread-safe queue."""
    q: stdlib_queue.Queue = stdlib_queue.Queue(maxsize=10000)
    with _lock:
        _subscribers[run_id].append(q)
    logger.debug(f"Client subscribed to run {run_id} ({len(_subscribers[run_id])} clients)")
    return q


def unsubscribe(run_id: str, q: stdlib_queue.Queue):
    """Remove a subscriber."""
    with _lock:
        subs = _subscribers.get(run_id, [])
        if q in subs:
            subs.remove(q)
        if not subs:
            _subscribers.pop(run_id, None)


def emit(run_id: str, encoded_event: str):
    """Push an encoded SSE event string to all subscribers of a run.

    Thread-safe — can be called from any thread (extensions run in
    DeferredTask threads, not the main aiohttp event loop).
    """
    with _lock:
        subs = list(_subscribers.get(run_id, []))
    for q in subs:
        try:
            q.put_nowait(encoded_event)
        except stdlib_queue.Full:
            logger.warning(f"Queue full for run {run_id}, dropping event")


def emit_finish(run_id: str):
    """Signal that a run has finished — sends None sentinel to close SSE streams."""
    with _lock:
        subs = list(_subscribers.get(run_id, []))
    for q in subs:
        q.put_nowait(None)  # None = sentinel for stream end


def get_active_runs() -> list[str]:
    """Return list of run_ids with active subscribers."""
    with _lock:
        return list(_subscribers.keys())


def get_subscriber_count(run_id: str) -> int:
    """Return number of subscribers for a run."""
    with _lock:
        return len(_subscribers.get(run_id, []))
