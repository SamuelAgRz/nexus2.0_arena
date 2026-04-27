from typing import Any, Dict, Optional

from src.agents.intent_clarifier import IntentClarifierAgent
from src.agents.dax_query_developer import DaxQueryDeveloperAgent
from src.agents.dax_validator import DaxValidatorAgent
from src.agents.dax_executor import DaxExecutorAgent
from src.agents.dax_result_summarizer import DaxResultSummarizerAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.final_summarizer import FinalSummarizerAgent
from src.utils.logger import get_logger


class NexusNotebookOrchestrator:
    """
    Nexus-like orchestrator.

    Flow:
    User Query
      -> Intent Clarifier
      -> DAX Query Developer
      -> DAX Validator
          - APPROVED -> DAX Executor
          - NOT APPROVED -> feedback back to DAX Query Developer
      -> DAX Result Summarizer
      -> VisualizationAgent if needed
      -> Final Summarizer
    """

    def __init__(
        self,
        llm_client,
        pbi_client,
        semantic_context: str,
        general_syn: str = "",
        dav: str = "",
        log_level: str = "INFO",
        max_validation_iterations: int = 3,
    ):
        self.logger = get_logger(self.__class__.__name__, log_level)
        self.max_validation_iterations = max_validation_iterations

        self.intent_agent = IntentClarifierAgent(
            llm_client,
            general_syn=general_syn,
            dav=dav,
        )

        self.developer_agent = DaxQueryDeveloperAgent(
            llm_client,
            general_syn=general_syn,
            dav=dav,
        )

        self.validator_agent = DaxValidatorAgent(
            llm_client=llm_client,
            semantic_context=semantic_context,
        )

        self.executor_agent = DaxExecutorAgent(pbi_client)
        self.result_summarizer = DaxResultSummarizerAgent(llm_client)
        self.visualizer = VisualizationAgent()
        self.final_summarizer = FinalSummarizerAgent(llm_client)

    def _has_agent(self, intent: Dict[str, Any], agent_name: str) -> bool:
        return any(agent.get("name") == agent_name for agent in intent.get("agents", []))

    def _get_instruction(self, intent: Dict[str, Any], agent_name: str) -> Optional[str]:
        for agent in intent.get("agents", []):
            if agent.get("name") == agent_name:
                return agent.get("instruction", "")
        return None

    def _is_approved(self, validation_result: str) -> bool:
        return validation_result.strip().upper() == "APPROVED"

    def _is_not_approved(self, validation_result: str) -> bool:
        return validation_result.strip().upper().startswith("NOT APPROVED")

    def _build_revision_instruction(
        self,
        original_instruction: str,
        previous_dax: str,
        validator_feedback: str,
    ) -> str:
        return f"""
You previously generated a DAX query that was not approved by the DAX Validator.

Original instruction:
{original_instruction}

Previous DAX query:
{previous_dax}

Validator feedback:
{validator_feedback}

Revise the DAX query according to the validator feedback.

Rules:
- Fix ONLY the issues listed by the validator.
- Preserve the original business intent.
- Do NOT introduce new filters, columns, measures, or business logic unless required by the validator.
- Return ONLY the corrected DAX query.
""".strip()

    def _generate_validated_dax(self, instruction: str) -> Dict[str, Any]:
        attempts = []
        current_instruction = instruction
        dax_query = None
        validation_result = None

        for iteration in range(1, self.max_validation_iterations + 1):
            self.logger.info(
                "Generating DAX",
                extra={"extra_payload": {"stage": "dax_developer", "iteration": iteration}},
            )

            dax_query = self.developer_agent.run(current_instruction)

            self.logger.info(
                "DAX generated",
                extra={
                    "extra_payload": {
                        "stage": "dax_developer",
                        "iteration": iteration,
                        "dax_query": dax_query,
                    }
                },
            )

            validation_result = self.validator_agent.run(
                business_question=instruction,
                dax_query=dax_query,
            )

            self.logger.info(
                "DAX validation completed",
                extra={
                    "extra_payload": {
                        "stage": "dax_validator",
                        "iteration": iteration,
                        "validation_result": validation_result,
                    }
                },
            )

            attempts.append(
                {
                    "iteration": iteration,
                    "dax_query": dax_query,
                    "validation_result": validation_result,
                }
            )

            if self._is_approved(validation_result):
                return {
                    "approved": True,
                    "dax_query": dax_query,
                    "validation_result": validation_result,
                    "attempts": attempts,
                }

            if self._is_not_approved(validation_result):
                current_instruction = self._build_revision_instruction(
                    original_instruction=instruction,
                    previous_dax=dax_query,
                    validator_feedback=validation_result,
                )
                continue

            return {
                "approved": False,
                "dax_query": dax_query,
                "validation_result": (
                    "Validator returned an unexpected response. "
                    f"Raw response: {validation_result}"
                ),
                "attempts": attempts,
            }

        return {
            "approved": False,
            "dax_query": dax_query,
            "validation_result": "Max validation iterations reached without APPROVED.",
            "attempts": attempts,
        }

    def run(self, user_query: str) -> Dict[str, Any]:
        self.logger.info(
            "Starting orchestration",
            extra={"extra_payload": {"stage": "start"}},
        )

        intent = self.intent_agent.run(user_query)

        self.logger.info(
            "Intent classified",
            extra={"extra_payload": {"stage": "intent", "intent": intent}},
        )

        intent_type = intent.get("intent", "unsupported")

        dax_query = None
        dax_result = None
        dax_summary = ""
        df = None
        viz_note = ""
        validation_payload = None

        if intent_type == "unsupported":
            final_answer = (
                "The request is too ambiguous or out of scope. "
                "Please clarify the metric, time period, geography, or output you need."
            )

            return {
                "intent": intent,
                "dax_query": None,
                "dax_result": None,
                "dataframe": None,
                "validation": None,
                "final_answer": final_answer,
            }

        if self._has_agent(intent, "FHB_dataset"):
            fhb_instruction = self._get_instruction(intent, "FHB_dataset") or user_query

            validation_payload = self._generate_validated_dax(fhb_instruction)

            if not validation_payload["approved"]:
                final_answer = (
                    "The DAX query could not be approved by the validator.\n\n"
                    f"Validation result:\n{validation_payload['validation_result']}"
                )

                return {
                    "intent": intent,
                    "dax_query": validation_payload.get("dax_query"),
                    "dax_result": None,
                    "dataframe": None,
                    "validation": validation_payload,
                    "final_answer": final_answer,
                }

            dax_query = validation_payload["dax_query"]

            self.logger.info(
                "Executing approved DAX",
                extra={"extra_payload": {"stage": "dax_executor"}},
            )

            dax_result = self.executor_agent.run(dax_query)

            self.logger.info(
                "DAX executed",
                extra={"extra_payload": {"stage": "dax_executor"}},
            )

            dax_summary = self.result_summarizer.run(
                business_question=fhb_instruction,
                dax_result=dax_result,
            )

            self.logger.info(
                "DAX result summarized",
                extra={"extra_payload": {"stage": "dax_result_summarizer"}},
            )

        if self._has_agent(intent, "VisualizationAgent"):
            viz_instruction = self._get_instruction(intent, "VisualizationAgent") or ""

            if dax_result is not None:
                df = self.visualizer.extract_table(dax_result)
                viz_note = (
                    f"Visualization requested. Instruction: {viz_instruction}. "
                    f"Dataframe generated with {len(df)} rows."
                )

                self.logger.info(
                    "Visualization dataframe ready",
                    extra={
                        "extra_payload": {
                            "stage": "visualization",
                            "rows": len(df),
                        }
                    },
                )
            else:
                viz_note = (
                    "Visualization was requested, but no executed data table was available. "
                    f"Instruction: {viz_instruction}"
                )

        final_answer = self.final_summarizer.run(
            user_query=user_query,
            dax_summary=dax_summary,
            viz_note=viz_note,
        )

        self.logger.info(
            "Final answer generated",
            extra={"extra_payload": {"stage": "final_summarizer"}},
        )

        return {
            "intent": intent,
            "dax_query": dax_query,
            "dax_result": dax_result,
            "dataframe": df,
            "validation": validation_payload,
            "final_answer": final_answer,
        }
