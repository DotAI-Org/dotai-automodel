"""WebSocket chat endpoint for agent communication."""
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.session_store import store
from app.agent.loop import (
    get_agent_state,
    register_broadcast_callback,
    unregister_broadcast_callback,
)
from app.chat.handler import handle_message
from app.auth.dependencies import get_ws_user
from app.persistence import save_chat_message, load_chat_history
from app.db.engine import AsyncSessionLocal
from app.notifications import fire_and_forget as notify

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/sessions/{session_id}/chat")
async def chat_websocket(websocket: WebSocket, session_id: str, token: str = Query(default="")):
    """Handle WebSocket connection for chat with the agent."""
    # Authenticate via JWT query param
    user = None
    if token:
        try:
            user = get_ws_user(token)
        except Exception:
            notify("WebSocket auth failed", f"session {session_id}, invalid token")
            await websocket.close(code=4001, reason="Invalid token")
            return

    session = store.get(session_id)
    if session is None:
        session = await store.get_or_load(session_id)
    if not session:
        notify("WebSocket session not found", f"session {session_id}")
        await websocket.close(code=4004, reason="Session not found")
        return

    # Verify ownership if authenticated
    if user:
        owner = session.get("user_id") or await store.get_owner(session_id)
        if owner and str(owner) != str(user["id"]):
            await websocket.close(code=4003, reason="Not authorized")
            return

    await websocket.accept()

    # Send chat history
    try:
        async with AsyncSessionLocal() as db:
            history = await load_chat_history(db, session_id)
        for msg in history:
            await websocket.send_json({
                "type": "chat_history",
                "role": msg["role"],
                "text": msg["content"],
            })
    except Exception as e:
        logger.warning(f"Failed to load chat history: {e}")

    # Register broadcast callback for this WebSocket
    async def on_broadcast(msg_type: str, data: dict):
        try:
            await websocket.send_json({"type": msg_type, **data})
        except Exception as e:
            notify("WebSocket broadcast failed", f"session {session_id}, error={e}")

    register_broadcast_callback(session_id, on_broadcast)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                message = {"text": raw}

            text = message.get("text", "")
            if not text:
                continue

            # Persist user message
            try:
                async with AsyncSessionLocal() as db:
                    await save_chat_message(db, session_id, "user", text)
            except Exception as e:
                logger.warning(f"Failed to persist user message: {e}")

            agent_state = get_agent_state(session_id)
            if agent_state is None:
                resp_text = "Agent has not been started. Start the agent first."
                await websocket.send_json({
                    "type": "agent_response",
                    "text": resp_text,
                })
                continue

            response = await handle_message(session_id, text, agent_state)

            resp_text = response["response_text"]

            # Persist system response
            try:
                async with AsyncSessionLocal() as db:
                    await save_chat_message(db, session_id, "system", resp_text)
            except Exception as e:
                logger.warning(f"Failed to persist system message: {e}")

            await websocket.send_json({
                "type": "agent_response",
                "text": resp_text,
                "intent": response["intent"],
                "command": response.get("command"),
            })

    except WebSocketDisconnect:
        agent_state = get_agent_state(session_id)
        if agent_state and agent_state.status == "running":
            notify("WebSocket disconnected during agent run", f"session {session_id}")
        logger.info(f"WebSocket disconnected for session {session_id}")
    finally:
        unregister_broadcast_callback(session_id, on_broadcast)
