import logging
from typing import Any

from app.models.schemas import LLMChatOutput
from app.llm.client import generate_structured
from app.agent.loop import AgentState

logger = logging.getLogger(__name__)


async def handle_message(
    session_id: str, text: str, agent_state: AgentState
) -> dict:
    """Process a user chat message and return a response + any commands."""
    # Build context about current state
    state_summary = _build_state_summary(agent_state)

    prompt = f"""You are an assistant helping a user with a churn prediction pipeline.

CURRENT PIPELINE STATE:
{state_summary}

USER MESSAGE:
{text}

Classify the user's message and respond.

Intent types:
- "command": User wants to modify the pipeline (remove feature, add feature, change model, change criteria, stop)
- "question": User has a question about the pipeline, features, or results
- "approval": User accepts the current champion model

For commands, set the "command" field to one of:
- "remove_feature" with command_params: {{"features": ["feature_name"]}}
- "add_feature" with command_params: {{"name": "feature_name", "operation": "aggregate", "params": {{...}}}}
- "change_criteria" with command_params: {{"min_auc": 0.8}} (or other criteria keys)
- "force_model" with command_params: {{"model": "xgboost" or "random_forest"}}
- "stop" with command_params: {{}}
- "skip_to_completion" with command_params: {{}}

Return JSON with:
- intent: "command" | "question" | "approval"
- response_text: text to show the user
- command: command name (null if not a command)
- command_params: command parameters (null if not a command)"""

    try:
        result = await generate_structured(prompt, LLMChatOutput)
    except Exception as e:
        logger.error(f"Chat LLM failed: {e}")
        return {
            "intent": "question",
            "response_text": f"Could not process your message. Try rephrasing.",
            "command": None,
            "command_params": None,
        }

    # Apply command to agent state if applicable
    if result.intent == "command" and result.command:
        _apply_command(agent_state, result.command, result.command_params or {})

    return {
        "intent": result.intent,
        "response_text": result.response_text,
        "command": result.command,
        "command_params": result.command_params,
    }


def _build_state_summary(state: AgentState) -> str:
    lines = [
        f"Status: {state.status}",
        f"Iteration: {state.iteration}/{state.max_iterations}",
        f"Excluded features: {state.excluded_features}",
    ]

    if state.history:
        last = state.history[-1]
        lines.append(f"Features in use: {last.features_used}")
        if last.model_results:
            for mr in last.model_results:
                lines.append(f"  {mr.name}: AUC={mr.metrics['auc']}, F1={mr.metrics['f1']}")
        lines.append(f"Leakage detected: {last.evaluation.leakage_detected}")
        lines.append(f"Quality acceptable: {last.evaluation.quality_acceptable}")

    if state.champion:
        lines.append(f"Champion: {state.champion.name} (AUC={state.champion.metrics['auc']})")

    lines.append(f"Success criteria: {state.success_criteria}")

    return "\n".join(lines)


def _apply_command(state: AgentState, command: str, params: dict):
    """Apply a parsed command to the agent state via user_overrides."""
    if command == "remove_feature":
        features = params.get("features", [])
        state.user_overrides["remove_features"] = features

    elif command == "add_feature":
        state.user_overrides["add_features"] = [params]

    elif command == "change_criteria":
        state.user_overrides["change_criteria"] = params

    elif command == "stop":
        state.user_overrides["stop"] = True

    elif command == "skip_to_completion":
        state.user_overrides["skip_to_completion"] = True

    elif command == "force_model":
        # Find the model in the latest iteration and set it as champion
        model_name = params.get("model")
        if state.history:
            for mr in state.history[-1].model_results:
                if mr.name == model_name:
                    state.champion = mr
                    break
