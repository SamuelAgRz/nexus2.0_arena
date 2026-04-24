import json
from typing import Any, Dict

from src.prompts.intent_clarifier import INTENT_SYSTEM_PROMPT


class IntentClarifierAgent:
    """
    Intent Clarifier Agent

    Responsibilities:
    - Build the system prompt with business context placeholders
    - Route user requests to downstream agents
    - Return a structured JSON payload
    """

    def __init__(self, llm_client, general_syn: str = "", dav: str = ""):
        self.llm = llm_client
        self.general_syn = general_syn
        self.dav = dav

    def _build_system_prompt(self) -> str:
        return (
        INTENT_SYSTEM_PROMPT
        .replace("{general_syn}", self.general_syn)
        .replace("{dav}", self.dav)
    )

    def _safe_parse_json(self, raw: str) -> Dict[str, Any]:
        raw = raw.strip()

        if raw.startswith("```json"):
            raw = raw.replace("```json", "", 1).strip()
        if raw.startswith("```"):
            raw = raw.replace("```", "", 1).strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"IntentClarifierAgent returned invalid JSON. Raw output:\n{raw}"
            ) from exc

        if not isinstance(payload, dict):
            raise ValueError("IntentClarifierAgent output must be a JSON object.")

        return payload

    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        allowed_intents = {
            "semantic_query",
            "general_chat",
            "visualization_only",
            "summarization_only",
            "unsupported",
        }
        allowed_agent_names = {"FHB_dataset", "VisualizationAgent", "Summarizer"}
        allowed_output_formats = {"table", "chart", "text"}
        allowed_languages = {"es", "en"}

        payload["intent"] = payload.get("intent", "unsupported")
        if payload["intent"] not in allowed_intents:
            payload["intent"] = "unsupported"

        agents = payload.get("agents", [])
        if not isinstance(agents, list):
            agents = []

        normalized_agents = []
        for agent in agents:
            if not isinstance(agent, dict):
                continue

            name = agent.get("name", "")
            instruction = str(agent.get("instruction", "")).strip()

            if name in allowed_agent_names and instruction:
                normalized_agents.append(
                    {
                        "name": name,
                        "instruction": instruction,
                    }
                )

        payload["agents"] = normalized_agents
        payload["needs_visualization"] = bool(payload.get("needs_visualization", False))

        output_format = payload.get("output_format", "text")
        if output_format not in allowed_output_formats:
            output_format = "text"
        payload["output_format"] = output_format

        payload["business_question"] = str(payload.get("business_question", "")).strip()

        user_language = payload.get("user_language", "en")
        if user_language not in allowed_languages:
            user_language = "en"
        payload["user_language"] = user_language

        reason = str(payload.get("reason", "")).strip()
        payload["reason"] = reason

        confidence = payload.get("confidence", 0.0)
        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        payload["confidence"] = confidence

        return payload

    def run(self, user_query: str) -> Dict[str, Any]:
        system_prompt = self._build_system_prompt()
        raw = self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_query,
        )

        payload = self._safe_parse_json(raw)
        payload = self._validate_payload(payload)
        return payload
