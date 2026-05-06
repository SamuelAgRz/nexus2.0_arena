from typing import Any, Dict, Optional

from src.agents.intent_clarifier import IntentClarifierAgent
from src.agents.dax_query_developer import DaxQueryDeveloperAgent
from src.agents.dax_validator import DaxValidatorAgent
from src.agents.dax_executor import DaxExecutorAgent
from src.agents.dax_result_summarizer import DaxResultSummarizerAgent
from src.agents.visualization_agent import VisualizationAgent
from src.agents.final_summarizer import FinalSummarizerAgent

from src.utils.logger import get_logger
from src.utils.config_loader import load_yaml
from src.utils.synonym_selector import (
    select_relevant_synonyms,
    format_synonyms_for_prompt,
)


class NexusNotebookOrchestrator:
    """
    Nexus-like orchestrator.

    Flow:
        User Query
          -> Runtime synonym selection
          -> Intent Clarifier
          -> DAX Query Developer
          -> DAX Validator
              - APPROVED -> DAX Executor
              - NOT APPROVED -> feedback back to DAX Query Developer
          -> DAX Result Summarizer
          -> VisualizationAgent if needed
          -> Final Summarizer

    Important architecture rules:
        - Intent Clarifier is the only agent that uses general_syn.
        - DAX Developer receives structured intent/instruction + dav, but no general_syn.
        - DAX Developer must not ask clarification questions.
        - Validator validates query against semantic context/model rules.
    """

    def __init__(
        self,
        llm_client,
        pbi_client,
        semantic_context: str,
        dav: str = "",
        synonyms_path: str = "src/config/synonyms/general_syn_full.yml",
        log_level: str = "INFO",
        max_validation_iterations: int = 3,
        max_synonym_keys: int = 40,
    ):
        self.logger = get_logger(self.__class__.__name__, log_level)
        self.max_validation_iterations = max_validation_iterations
        self.max_synonym_keys = max_synonym_keys
        self.dav = dav
        self.semantic_context = semantic_context

        # Load the full synonym dictionary once.
        # Runtime query-specific subset is selected inside run().
        try:
            self.full_synonyms = load_yaml(synonyms_path)
        except FileNotFoundError:
            self.logger.warning(
                "Synonym file not found. Continuing with empty synonyms.",
                extra={
                    "extra_payload": {
                        "stage": "init",
                        "synonyms_path": synonyms_path,
                    }
                },
            )
            self.full_synonyms = {}

        # Intent Clarifier receives dav at init.
        # Runtime general_syn is passed during run().
        self.intent_agent = IntentClarifierAgent(
            llm_client,
            dav=dav,
        )

        # DAX Developer should NOT use general_syn.
        # It should compile valid intent/instruction into executable DAX.
        self.developer_agent = DaxQueryDeveloperAgent(
            llm_client,
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

    def _build_runtime_synonyms(self, user_query: str) -> str:
        """
        Select only relevant synonyms for the current user query.
        This avoids injecting the full synonym dictionary into the prompt.
        """
        selected_synonyms = select_relevant_synonyms(
            user_query=user_query,
            raw_synonyms=self.full_synonyms,
            max_keys=self.max_synonym_keys,
        )

        runtime_synonyms = format_synonyms_for_prompt(selected_synonyms)

        self.logger.info(
            "Runtime synonyms selected",
            extra={
                "extra_payload": {
                    "stage": "synonym_selector",
                    "selected_keys": list(selected_synonyms.keys()),
                    "selected_count": len(selected_synonyms),
                }
            },
        )

        return runtime_synonyms

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
        normalized = validation_result.strip().upper()
        return normalized.startswith("NOT APPROVED") or '"STATUS": "NOT_APPROVED"' in normalized

    def _is_intent_invalid(self, dax_query: str) -> bool:
        return dax_query.strip().upper() == "INTENT_INVALID"

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
- If the intent is not executable, return exactly: INTENT_INVALID
""".strip()

    def _generate_validated_dax(self, instruction: str) -> Dict[str, Any]:
        attempts = []
        current_instruction = instruction
        dax_query = None
        validation_result = None

        for iteration in range(1, self.max_validation_iterations + 1):
            self.logger.info(
                "Generating DAX",
                extra={
                    "extra_payload": {
                        "stage": "dax_developer",
                        "iteration": iteration,
                    }
                },
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

            if self._is_intent_invalid(dax_query):
                validation_result = (
                    "INTENT_INVALID returned by DAX Developer. "
                    "The structured intent/instruction was incomplete, ambiguous, "
                    "or not executable against the provided semantic model context."
                )

                attempts.append(
                    {
                        "iteration": iteration,
                        "dax_query": dax_query,
                        "validation_result": validation_result,
                    }
                )

                return {
                    "approved": False,
                    "dax_query": dax_query,
                    "validation_result": validation_result,
                    "attempts": attempts,
                }

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
            extra={"extra_payload": {"stage": "start", "user_query": user_query}},
        )

        general_syn_runtime = self._build_runtime_synonyms(user_query)

        # Intent Clarifier is the only agent that receives general_syn.
        intent = self.intent_agent.run(
            user_query=user_query,
            general_syn=general_syn_runtime,
        )

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
                "runtime_synonyms": general_syn_runtime,
                "dax_query": None,
                "dax_result": None,
                "dataframe": None,
                "validation": None,
                "final_answer": final_answer,
            }

        # Backward compatibility with your current routing name.
        # If you rename the agent to "Dax Developer", add it here too.
        has_dax_agent = self._has_agent(intent, "FHB_dataset") or self._has_agent(intent, "Dax Developer")

        if has_dax_agent:
            fhb_instruction = (
                self._get_instruction(intent, "FHB_dataset")
                or self._get_instruction(intent, "Dax Developer")
                or user_query
            )

            validation_payload = self._generate_validated_dax(fhb_instruction)

            if not validation_payload["approved"]:
                final_answer = (
                    "The DAX query could not be approved by the validator.\n\n"
                    f"Validation result:\n{validation_payload['validation_result']}"
                )

                return {
                    "intent": intent,
                    "runtime_synonyms": general_syn_runtime,
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
            "runtime_synonyms": general_syn_runtime,
            "dax_query": dax_query,
            "dax_result": dax_result,
            "dataframe": df,
            "validation": validation_payload,
            "final_answer": final_answer,
        }
