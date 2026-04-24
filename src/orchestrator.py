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
    def __init__(
        self,
        llm_client,
        pbi_client,
        semantic_context: str,
        general_syn: str = "",
        dav: str = "",
        log_level: str = "INFO",
    ):
        self.logger = get_logger(self.__class__.__name__, log_level)

        # 🔥 NUEVO: pasar syn + dav al intent clarifier
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

        self.validator_agent = DaxValidatorAgent(llm_client, semantic_context)
        self.executor_agent = DaxExecutorAgent(pbi_client)
        self.result_summarizer = DaxResultSummarizerAgent(llm_client)
        self.visualizer = VisualizationAgent()
        self.final_summarizer = FinalSummarizerAgent(llm_client)

    # -----------------------------
    # helpers
    # -----------------------------
    def _has_agent(self, intent: Dict[str, Any], agent_name: str) -> bool:
        return any(a.get("name") == agent_name for a in intent.get("agents", []))

    def _get_instruction(self, intent: Dict[str, Any], agent_name: str) -> Optional[str]:
        for a in intent.get("agents", []):
            if a.get("name") == agent_name:
                return a.get("instruction", "")
        return None

    # -----------------------------
    # main
    # -----------------------------
    def run(self, user_query: str) -> Dict[str, Any]:
        self.logger.info("Starting orchestration", extra={"extra_payload": {"stage": "start"}})

        intent = self.intent_agent.run(user_query)
        self.logger.info("Intent classified", extra={"extra_payload": {"stage": "intent", "intent": intent}})

        intent_type = intent.get("intent", "unsupported")

        dax_draft = None
        dax_final = None
        dax_result = None
        dax_summary = ""
        df = None
        viz_note = ""

        # -----------------------------
        # Unsupported
        # -----------------------------
        if intent_type == "unsupported":
            return {
                "intent": intent,
                "dax_draft": None,
                "dax_final": None,
                "dax_result": None,
                "dataframe": None,
                "final_answer": "The request is too ambiguous or out of scope.",
            }

        # -----------------------------
        # FHB_dataset (core data path)
        # -----------------------------
        if self._has_agent(intent, "FHB_dataset"):
            instruction = self._get_instruction(intent, "FHB_dataset") or user_query

            dax_draft = self.developer_agent.run(instruction)
            self.logger.info("DAX plan generated", extra={"extra_payload": {"stage": "developer"}})

            dax_final = self.validator_agent.run(instruction, dax_draft)
            self.logger.info("DAX validated", extra={"extra_payload": {"stage": "validator"}})

            dax_result = self.executor_agent.run(dax_final)
            self.logger.info("DAX executed", extra={"extra_payload": {"stage": "executor"}})

            dax_summary = self.result_summarizer.run(instruction, dax_result)
            self.logger.info("Result summarized", extra={"extra_payload": {"stage": "result_summarizer"}})

        # -----------------------------
        # Visualization
        # -----------------------------
        if self._has_agent(intent, "VisualizationAgent"):
            viz_instruction = self._get_instruction(intent, "VisualizationAgent") or ""

            if dax_result:
                df = self.visualizer.extract_table(dax_result)
                viz_note = f"{viz_instruction} | rows: {len(df)}"
                self.logger.info("Visualization ready", extra={"extra_payload": {"rows": len(df)}})
            else:
                viz_note = f"Visualization requested but no data available. Instruction: {viz_instruction}"

        # -----------------------------
        # Final response
        # -----------------------------
        final_answer = self.final_summarizer.run(
            user_query=user_query,
            dax_summary=dax_summary,
            viz_note=viz_note,
        )

        self.logger.info("Final answer generated", extra={"extra_payload": {"stage": "final"}})

        return {
            "intent": intent,
            "dax_draft": dax_draft,
            "dax_final": dax_final,
            "dax_result": dax_result,
            "dataframe": df,
            "final_answer": final_answer,
        }