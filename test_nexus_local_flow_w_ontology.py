"""
test_nexus_local_flow.py

Purpose:
- Test Nexus 2.0 local multi-agent flow end to end:
  1. Intent Clarifier
  2. DAX Query Developer
  3. DAX Validator
  4. DAX Executor

Recommended run from repo root:
    python test_nexus_local_flow.py

Notes:
- This script assumes your local Nexus repo has:
    src.llm_client.AzureAIFoundry
    src.agents.intent_clarifier.IntentClarifierAgent
    src.agents.dax_query_developer.DaxQueryDeveloperAgent
    src.agents.dax_validator.DaxValidatorAgent
    src.connections.nsr_conn.AdomdConnector
    src.agents.dax_executor.DaxExecutorAgent

- It will try to load semantic context from:
    docs/semantic_model_measures/measures_nexus_context_latest.md
    docs/semantic_model_minimal/minimal_nexus_context_latest.md

  If those files do not exist, it will use the fallback SEMANTIC_CONTEXT inside this script.
"""

from __future__ import annotations

import os
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd


# =============================================================================
# Project path
# =============================================================================

PROJECT_ROOT = Path(r"c:\\Users\\AdrianLandaverde\\Documents\\nexus2.0_arena")
sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# Imports
# =============================================================================

from src.llm_client import AzureAIFoundry
from src.agents.intent_clarifier import IntentClarifierAgent
from src.agents.dax_query_developer import DaxQueryDeveloperAgent
from src.agents.dax_validator import DaxValidatorAgent
from src.connections.nsr_conn import AdomdConnector
from src.agents.dax_executor import DaxExecutorAgent
from src.agents.ontologic_agent import OntologicAgent
from src.connections.ontology import AdomdConnector as OntologyConnector


# =============================================================================
# Config
# =============================================================================

PATH_DLL = PROJECT_ROOT / "lib" / "Microsoft.AnalysisServices.AdomdClient.dll"

STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
    "Persist Security Info=True;"
)

STR_CONN_ONTOLOGY = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/mf-pocai-eastus2-dev-01;"
    "Initial Catalog=ontology_nsr;"
    "Integrated Security=ClaimsToken;"
)

OUTPUT_DIR = PROJECT_ROOT / "logs" / "nexus_local_tests"

SEMANTIC_MEASURES_CONTEXT_PATH = (
    PROJECT_ROOT / "docs" / "semantic_model_measures" / "measures_nexus_context_latest.md"
)

SEMANTIC_COLUMNS_CONTEXT_PATH = (
    PROJECT_ROOT / "docs" / "semantic_model_minimal" / "minimal_nexus_context_latest.md"
)

USER_QUERY = "Show NSR YTD by channel for Colombia"

MAX_VALIDATION_ITERATIONS = 3
MAX_CLARIFICATION_ROUNDS = 3
EXECUTE_DAX = True
SAVE_RESULT_CSV = True


# =============================================================================
# Context
# =============================================================================

GENERAL_SYN = """
NSR = Net Sales Revenue
Net Sales Revenue = NSR
sell-in = bottler revenue
market = Ship To
country = Ship To geography
customer = Ship To customer
channel = Trade Channel
trade channel = Channel dimension
YTD = year to date
MTD = month to date
QTD = quarter to date
BP = Business Plan
RE = Rolling Estimate
Actuals = Actual scenario
Colombia = Colombia market
"""


FALLBACK_SEMANTIC_CONTEXT = """
# Target Model

Target model: NSR LATAM Cube UAT / NSR LATAM semantic model.

# Tables and columns available

## Channel
- 'Channel'[Trade Channel]
- 'Channel'[Sub Trade Channel]

## Ship To
- 'Ship To'[Source Ship To Code]
- 'Ship To'[LT1.1 - Tradename]
- 'Ship To'[LT1.2 - Customer]

## Period
- 'Period'[Date]
- 'Period'[Year]
- 'Period'[Month]
- 'Period'[Week]

# Measures available

- [NSR]
- [NSR YTD]

# Business Rules

- NSR means Net Sales Revenue.
- NSR is SELL-IN / bottler revenue, not sell-out / retail sales.
- Use only tables, columns, and measures listed in this context.
- Do not invent columns.
- Do not invent measures.
- For channel breakdown, use 'Channel'[Trade Channel].
- Never use 'Channel'[Channel] unless it appears explicitly in the semantic context.
- Never use 'Ship To'[Country] unless it appears explicitly in the semantic context.
- Prefer exposed model measures over raw metric columns.
- If a metric exists as a measure, use the measure.
- Return executable DAX only.
"""


# =============================================================================
# Helpers
# =============================================================================

def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_output_dir() -> Path:
    run_dir = OUTPUT_DIR / f"run_{now_stamp()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def save_text(path: Path, content: str) -> None:
    path.write_text(str(content), encoding="utf-8")
    print(f"Saved: {path}")


def load_optional_file(path: Path) -> str:
    if path.exists():
        print(f"Loaded semantic context file: {path}")
        return path.read_text(encoding="utf-8")
    print(f"Context file not found, skipping: {path}")
    return ""


def build_semantic_context() -> str:
    """
    Build semantic context from latest generated metadata files.

    Priority:
    1. Measures context from INFO.MEASURES()
    2. Tables/columns context from INFO.TABLES() and INFO.COLUMNS()
    3. Fallback context
    """
    measures_context = load_optional_file(SEMANTIC_MEASURES_CONTEXT_PATH)
    columns_context = load_optional_file(SEMANTIC_COLUMNS_CONTEXT_PATH)

    parts = []

    if measures_context:
        parts.append("# Measures Context From Semantic Model\n")
        parts.append(measures_context)

    if columns_context:
        parts.append("\n# Tables And Columns Context From Semantic Model\n")
        parts.append(columns_context)

    if not parts:
        print("Using fallback semantic context.")
        parts.append(FALLBACK_SEMANTIC_CONTEXT)

    parts.append(
        """
# Mandatory Nexus DAX Rules

- The DAX query must be executable against the NSR LATAM Power BI semantic model.
- Use only exact table, column, and measure names from the semantic context.
- Do not create calculated measures inside the query unless explicitly required.
- Prefer SUMMARIZECOLUMNS for grouped analytical queries.
- Do not use SQL syntax.
- Do not use SELECT *.
- Do not use unavailable tables such as 'Scenario' unless they exist in the context.
- Do not use unavailable columns such as 'Channel'[Channel] unless they exist in the context.
- If filtering Colombia, only use a geography column that exists in the context.
- If a required geography column does not exist in the context, the agent should ask for clarification instead of inventing a column.
"""
    )

    return "\n\n".join(parts)


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def clean_dax_response(raw: Any) -> str:
    """
    Cleans common LLM formatting issues:
    - markdown fences
    - leading labels
    - extra commentary before/after query
    """
    if raw is None:
        return ""

    text = str(raw).strip()

    # Extract code block if present.
    fence_match = re.search(r"```(?:DAX|dax)?\s*(.*?)```", text, flags=re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    # Remove common labels.
    text = re.sub(r"^\s*(DAX Query|DAX|Query)\s*:\s*", "", text, flags=re.IGNORECASE)

    # Keep from EVALUATE onward if the model added prose above.
    evaluate_idx = text.upper().find("EVALUATE")
    if evaluate_idx >= 0:
        text = text[evaluate_idx:].strip()

    return text.strip()


def extract_fhb_instruction(intent: Dict[str, Any]) -> Optional[str]:
    """
    Expected intent shape:
    {
        "agents": [
            {"name": "FHB_dataset", "instruction": "..."}
        ]
    }

    This function is defensive in case your Intent Clarifier changes naming.
    """
    agents = intent.get("agents", [])

    for agent in agents:
        name = str(agent.get("name", "")).strip().lower()
        if name in {"fhb_dataset", "sql_som_agent", "dax_agent", "dax_developer", "dax_query_developer"}:
            return agent.get("instruction")

    # Fallback: first agent with instruction.
    for agent in agents:
        if agent.get("instruction"):
            return agent.get("instruction")

    return None


def normalize_validator_response(response: Any) -> str:
    return str(response or "").strip()


def is_approved(validation_result: str) -> bool:
    return validation_result.strip().upper() == "APPROVED"


def is_not_approved(validation_result: str) -> bool:
    return validation_result.strip().upper().startswith("NOT APPROVED")


def run_basic_connection_test() -> None:
    print_section("BASIC CONNECTION TEST")
    print("DLL:", PATH_DLL)
    print("DLL exists:", PATH_DLL.exists())

    if not PATH_DLL.exists():
        raise FileNotFoundError(f"ADOMD DLL not found: {PATH_DLL}")

    nsr_conn = AdomdConnector(str(PATH_DLL), STR_CONN)
    executor = DaxExecutorAgent(nsr_conn)

    test_query = """
EVALUATE
ROW("ConnectionTest", 1)
"""
    df = executor.run(test_query)
    print(df.head())


# =============================================================================
# Main flow
# =============================================================================

def main() -> None:
    print_section("NEXUS 2.0 LOCAL AGENT FLOW TEST")

    run_dir = ensure_output_dir()

    print("Project root:", PROJECT_ROOT)
    print("Output run dir:", run_dir)
    print("User query:", USER_QUERY)

    semantic_context = build_semantic_context()

    save_text(run_dir / "semantic_context_used.md", semantic_context)
    save_text(run_dir / "general_syn_used.md", GENERAL_SYN)
    save_text(run_dir / "user_query.txt", USER_QUERY)

    # Optional quick connection test before spending LLM calls.
    run_basic_connection_test()

    # -------------------------------------------------------------------------
    # 1. LLM Client
    # -------------------------------------------------------------------------
    print_section("1. INITIALIZING LLM CLIENT")
    llm = AzureAIFoundry()
    print("LLM client initialized.")

    # -------------------------------------------------------------------------
    # 2. Ontologic Agent + Intent Clarifier loop
    # -------------------------------------------------------------------------
    print_section("2. INITIALIZING ONTOLOGIC AGENT")

    ontology_conn = OntologyConnector(str(PATH_DLL), STR_CONN_ONTOLOGY)
    ontologic_agent = OntologicAgent(llm, ontology_conn)

    print_section("2. ONTOLOGIC AGENT + INTENT CLARIFIER LOOP")

    combined_query = USER_QUERY
    intent = None

    for round_n in range(MAX_CLARIFICATION_ROUNDS):
        print_section(f"OA → IC ROUND {round_n + 1}")

        ontology_context = ontologic_agent.run(combined_query)
        save_text(run_dir / f"ontology_context_round_{round_n + 1}.md", ontology_context)
        print(f"Ontology context (round {round_n + 1}):\n{ontology_context or '(empty)'}")

        intent_agent = IntentClarifierAgent(
            llm,
            general_syn=GENERAL_SYN,
            dav=semantic_context,
            ontology_context=ontology_context,
        )

        intent = intent_agent.run(combined_query)
        save_text(run_dir / f"01_intent_round_{round_n + 1}.txt", str(intent))
        print(intent)

        if not isinstance(intent, dict):
            raise TypeError(
                "IntentClarifierAgent did not return a dict. "
                "Check your _safe_parse_json implementation or prompt JSON-only rules."
            )

        if intent.get("intent") != "clarification":
            break

        if round_n == MAX_CLARIFICATION_ROUNDS - 1:
            raise RuntimeError(
                f"Intent could not be resolved after {MAX_CLARIFICATION_ROUNDS} clarification rounds."
            )

        agents = intent.get("agents", [])
        clarification_msg = (
            agents[0].get("instruction", "Please clarify your query.")
            if agents else "Please clarify your query."
        )

        print_section("CLARIFICATION NEEDED")
        print(clarification_msg)
        user_response = input("\nYour response: ").strip()
        combined_query = f"{USER_QUERY}\n\nUser clarification: {user_response}"

    fhb_instruction = extract_fhb_instruction(intent)

    if not fhb_instruction:
        raise RuntimeError(
            "No downstream DAX/FHB instruction found in intent. "
            "Expected an agent instruction under intent['agents']."
        )

    print_section("FHB / DAX INSTRUCTION")
    print(fhb_instruction)
    save_text(run_dir / "02_fhb_instruction.txt", fhb_instruction)

    # -------------------------------------------------------------------------
    # 3. DAX Developer
    # -------------------------------------------------------------------------
    print_section("3. DAX QUERY DEVELOPER")

    developer = DaxQueryDeveloperAgent(
        llm,
        general_syn=GENERAL_SYN,
        dav=semantic_context,
    )

    dax_query = developer.run(fhb_instruction)
    dax_query = clean_dax_response(dax_query)

    print(dax_query)
    save_text(run_dir / "03_dax_generated.dax", dax_query)

    if not dax_query.upper().startswith("EVALUATE"):
        raise RuntimeError(
            "Generated DAX does not start with EVALUATE after cleaning. "
            "Check DAX developer prompt."
        )

    # -------------------------------------------------------------------------
    # 4. DAX Validator with revision loop
    # -------------------------------------------------------------------------
    print_section("4. DAX VALIDATOR LOOP")

    validator = DaxValidatorAgent(
        llm_client=llm,
        semantic_context=semantic_context,
    )

    validation_result = None

    for i in range(MAX_VALIDATION_ITERATIONS):
        print_section(f"VALIDATION ITERATION {i + 1}")

        validation_result = validator.run(
            business_question=fhb_instruction,
            dax_query=dax_query,
        )

        validation_result = normalize_validator_response(validation_result)

        print(validation_result)
        save_text(run_dir / f"04_validation_iteration_{i + 1}.txt", validation_result)

        if is_approved(validation_result):
            print("DAX approved.")
            break

        if is_not_approved(validation_result):
            revision_instruction = f"""
You are revising a DAX query for the NSR LATAM semantic model.

Original user question:
{USER_QUERY}

Business/DAX instruction:
{fhb_instruction}

Previous DAX:
{dax_query}

Validator feedback:
{validation_result}

Semantic context:
{semantic_context}

Revision rules:
- Fix ONLY the issues identified by the validator.
- Do NOT invent tables.
- Do NOT invent columns.
- Do NOT invent measures.
- Use only exact semantic model objects available in the context.
- Return ONLY the corrected executable DAX query.
"""

            revised_dax = developer.run(revision_instruction)
            dax_query = clean_dax_response(revised_dax)

            print_section("REVISED DAX")
            print(dax_query)
            save_text(run_dir / f"05_dax_revised_iteration_{i + 1}.dax", dax_query)

            if not dax_query.upper().startswith("EVALUATE"):
                raise RuntimeError(
                    "Revised DAX does not start with EVALUATE after cleaning."
                )

            continue

        raise RuntimeError(f"Unexpected validator response: {validation_result}")

    if not is_approved(str(validation_result)):
        raise RuntimeError(
            f"DAX was not approved after {MAX_VALIDATION_ITERATIONS} validation iterations."
        )

    save_text(run_dir / "06_dax_approved.dax", dax_query)

    # -------------------------------------------------------------------------
    # 5. DAX Executor
    # -------------------------------------------------------------------------
    if not EXECUTE_DAX:
        print_section("5. EXECUTION SKIPPED")
        print("EXECUTE_DAX is False. Approved DAX saved.")
        return

    print_section("5. EXECUTING APPROVED DAX")

    nsr_conn = AdomdConnector(str(PATH_DLL), STR_CONN)
    executor = DaxExecutorAgent(nsr_conn)

    df_result = executor.run(dax_query)

    print_section("RESULT PREVIEW")
    print(df_result.head(20))

    if SAVE_RESULT_CSV:
        result_path = run_dir / "07_result.csv"
        df_result.to_csv(result_path, index=False, encoding="utf-8-sig")
        print(f"Saved result CSV: {result_path}")

    print_section("DONE")
    print("Run folder:", run_dir)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print_section("ERROR")
        print(type(exc).__name__, str(exc))
        traceback.print_exc()
        raise
