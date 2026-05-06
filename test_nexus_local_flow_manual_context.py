"""
test_nexus_local_flow_manual_context_v2.py

Purpose:
- Test Nexus 2.0 local multi-agent flow using a SMALL manual semantic context.
- Does NOT load generated .md files.
- Handles clarification intent correctly.
- Optionally applies test defaults to avoid stopping during local tests.

Run from repo root:
    python test_nexus_local_flow_manual_context_v2.py
"""

from __future__ import annotations

import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# =============================================================================
# Project path
# =============================================================================

PROJECT_ROOT = Path(r"C:\Users\SamuelAguilarRamirez\nexus2.0")
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

OUTPUT_DIR = PROJECT_ROOT / "logs" / "nexus_local_tests"

# For local testing, make the user query explicit to avoid clarification loop.
USER_QUERY = "Show NSR YTD by Trade Channel for Colombia using latest available YTD"

MAX_VALIDATION_ITERATIONS = 3
EXECUTE_DAX = True
SAVE_RESULT_CSV = True

# If True, when Intent Clarifier asks clarification, the script will convert the
# query into a deterministic test instruction instead of stopping.
ALLOW_TEST_DEFAULTS_ON_CLARIFICATION = True


# =============================================================================
# Small manual context
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
latest available YTD = use the latest available period in the semantic model
MTD = month to date
QTD = quarter to date
BP = Business Plan
RE = Rolling Estimate
Actuals = Actual scenario
Colombia = Colombia market
"""

SEMANTIC_CONTEXT = """
# Target model

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

# Local test defaults

For this local test only:
- If the user asks for "by channel", interpret channel as 'Channel'[Trade Channel].
- If the user asks for "YTD" without year, interpret it as latest available YTD.
- If the user asks for Colombia but no valid country/geography column is available in this context, do NOT invent 'Ship To'[Country].
- If Colombia cannot be filtered with the listed objects, generate the DAX without the Colombia filter and make the validator flag the missing geography object, OR ask for a valid geography column.
- For first local smoke test, prioritize executable DAX over perfect business filtering.

# Business Rules

- NSR means Net Sales Revenue.
- NSR is SELL-IN / bottler revenue, not sell-out / retail sales.
- Default scenario is Actuals unless the user explicitly asks for BP or RE.
- Use only tables, columns, and measures listed here.
- Do not invent tables.
- Do not invent columns.
- Do not invent measures.
- For channel breakdown, use 'Channel'[Trade Channel].
- Do not use 'Channel'[Channel].
- Do not use 'Ship To'[Country] unless it appears explicitly in this context.
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


def save_text(path: Path, content: Any) -> None:
    path.write_text(str(content), encoding="utf-8")
    print(f"Saved: {path}")


def print_section(title: str) -> None:
    print("\n" + "=" * 90)
    print(title)
    print("=" * 90)


def clean_dax_response(raw: Any) -> str:
    if raw is None:
        return ""

    text = str(raw).strip()

    # Handles accidental writing-block-like prefix: id="xxxxx"
    text = re.sub(r'^\s*id="[^"]+"\s*', "", text).strip()

    fence_match = re.search(r"```(?:DAX|dax)?\s*(.*?)```", text, flags=re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    text = re.sub(r"^\s*(DAX Query|DAX|Query)\s*:\s*", "", text, flags=re.IGNORECASE)

    evaluate_idx = text.upper().find("EVALUATE")
    if evaluate_idx >= 0:
        text = text[evaluate_idx:].strip()

    return text.strip()


def extract_fhb_instruction(intent: Dict[str, Any]) -> Optional[str]:
    agents = intent.get("agents", [])

    for agent in agents:
        name = str(agent.get("name", "")).strip().lower()
        if name in {
            "fhb_dataset",
            "sql_som_agent",
            "dax_agent",
            "dax_developer",
            "dax_query_developer",
        }:
            return agent.get("instruction")

    for agent in agents:
        if agent.get("instruction"):
            return agent.get("instruction")

    return None


def is_clarification_intent(intent: Dict[str, Any]) -> bool:
    intent_name = str(intent.get("intent", "")).strip().lower()

    if intent_name == "clarification":
        return True

    agents = intent.get("agents", [])
    if agents and all(str(a.get("name", "")).strip().lower() == "summarizer" for a in agents):
        return True

    return False


def get_clarification_message(intent: Dict[str, Any]) -> str:
    agents = intent.get("agents", [])
    for agent in agents:
        if agent.get("instruction"):
            return str(agent.get("instruction"))
    return "Clarification required, but no clarification message was provided."


def build_test_default_fhb_instruction(user_query: str) -> str:
    """
    Deterministic instruction for smoke testing local Nexus without user clarification.
    """
    return f"""
Business question:
{user_query}

Resolved assumptions for local smoke test:
- Metric: NSR YTD.
- Scenario: Actuals.
- Channel granularity: 'Channel'[Trade Channel].
- Time: latest available YTD.
- Geography: Colombia only if a valid Colombia/market/geography column is explicitly available in semantic context.
- If no valid Colombia column is available, do not invent one.

DAX generation task:
Generate an executable DAX query using SUMMARIZECOLUMNS that returns NSR YTD by 'Channel'[Trade Channel].
Use the exposed measure [NSR YTD].
Return only executable DAX.
"""


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
    print_section("NEXUS 2.0 LOCAL AGENT FLOW TEST - MANUAL CONTEXT V2")

    run_dir = ensure_output_dir()

    print("Project root:", PROJECT_ROOT)
    print("Output run dir:", run_dir)
    print("User query:", USER_QUERY)
    print("Semantic context chars:", len(SEMANTIC_CONTEXT))

    save_text(run_dir / "semantic_context_used.md", SEMANTIC_CONTEXT)
    save_text(run_dir / "general_syn_used.md", GENERAL_SYN)
    save_text(run_dir / "user_query.txt", USER_QUERY)

    run_basic_connection_test()

    # -------------------------------------------------------------------------
    # 1. LLM Client
    # -------------------------------------------------------------------------
    print_section("1. INITIALIZING LLM CLIENT")
    llm = AzureAIFoundry()
    print("LLM client initialized.")

    # -------------------------------------------------------------------------
    # 2. Intent Clarifier
    # -------------------------------------------------------------------------
    print_section("2. INTENT CLARIFIER")

    intent_agent = IntentClarifierAgent(
        llm,
        general_syn=GENERAL_SYN,
        dav=SEMANTIC_CONTEXT,
    )

    intent = intent_agent.run(USER_QUERY)

    print(intent)
    save_text(run_dir / "01_intent_raw.txt", intent)

    if not isinstance(intent, dict):
        raise TypeError(
            "IntentClarifierAgent did not return a dict. "
            "Check your _safe_parse_json implementation or prompt JSON-only rules."
        )

    if is_clarification_intent(intent):
        clarification_message = get_clarification_message(intent)

        print_section("CLARIFICATION REQUIRED")
        print(clarification_message)
        save_text(run_dir / "01b_clarification_message.txt", clarification_message)

        if not ALLOW_TEST_DEFAULTS_ON_CLARIFICATION:
            print("Stopping flow because clarification is required.")
            return

        print_section("USING LOCAL TEST DEFAULTS")
        fhb_instruction = build_test_default_fhb_instruction(USER_QUERY)
        print(fhb_instruction)
        save_text(run_dir / "02_fhb_instruction_from_test_defaults.txt", fhb_instruction)

    else:
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
        dav=SEMANTIC_CONTEXT,
    )

    dax_query = developer.run(fhb_instruction)
    dax_query = clean_dax_response(dax_query)

    print(dax_query)
    save_text(run_dir / "03_dax_generated.dax", dax_query)

    if not dax_query.upper().startswith("EVALUATE"):
        raise RuntimeError(
            "Generated DAX does not start with EVALUATE after cleaning. "
            "The DAX Developer returned clarification/prose instead of executable DAX."
        )

    # -------------------------------------------------------------------------
    # 4. DAX Validator with revision loop
    # -------------------------------------------------------------------------
    print_section("4. DAX VALIDATOR LOOP")

    validator = DaxValidatorAgent(
        llm_client=llm,
        semantic_context=SEMANTIC_CONTEXT,
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
{SEMANTIC_CONTEXT}

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
