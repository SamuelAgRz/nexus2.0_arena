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

# Account 1 — NSR LATAM workspace (e.g. your @arena-analytics.com or client account)
STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
    "Persist Security Info=True;"
    "User ID=alandaverdenava@coca-cola.com;"  # Uncomment and set to force a specific account
)

# Account 2 — Ontology workspace (mf-pocai-eastus2-dev-01, likely a different tenant/account)
STR_CONN_ONTOLOGY = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/mf-pocai-eastus2-dev-01;"
    "Initial Catalog=ontology_nsr;"
    "Integrated Security=ClaimsToken;"
    "User ID=adrian@arena-analytics.com;"  # Uncomment and set to force a specific account
)

OUTPUT_DIR = PROJECT_ROOT / "logs" / "nexus_local_tests"


USER_QUERY = "What was the actual volume of unit cases in Colombia in year 2025, for all categories. Group by channel"

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


COLUMNS_CONTEXT = """
# Target Model

Target model: NSR LATAM Cube / NSR LATAM Semantic Model (Power BI).

# Tables and Columns Available

## Channel
- 'Channel'[Trade Channel]
- 'Channel'[Sub Trade Channel]
- 'Channel'[Sub Trade Channel Code]
- 'Channel'[BU Channel Code]
- 'Channel'[Consumer Activity Cluster]
- 'Channel'[LT1.0 - Sub Trade Channel]
- 'Channel'[LT1.1 - Trade Channel]
- 'Channel'[LT1.2 - Channel Group]
- 'Channel'[LT1.3 - Channel Macro Group]

## Product
- 'Product'[Beverage Category]
- 'Product'[Beverage Sub Category]
- 'Product'[Beverage Type]
- 'Product'[Beverage State]
- 'Product'[BPP]
- 'Product'[BPP Code]
- 'Product'[BU Product]
- 'Product'[BU Product Code]
- 'Product'[LT1.1 - Beverage Product]
- 'Product'[LT1.2 - Brand Group]
- 'Product'[LT1.3 - Trademark Category]
- 'Product'[LT1.4 - Sub-Category]
- 'Product'[LT1.5 - Category]
- 'Product'[LT1.6 - Category Group]
- 'Product'[LT1.7 - Segment]
- 'Product'[LT1.8 - Industry]
- 'Product'[Non-KO Product]

## Package
- 'Package'[Package]
- 'Package'[Container Type]
- 'Package'[Primary Container]
- 'Package'[Secondary Package]
- 'Package'[BPP]
- 'Package'[LT1.1 - Package]
- 'Package'[LT1.2 - Package Type]
- 'Package'[LT1.3 - Container]
- 'Package'[LT1.4 - Refillability]
- 'Package'[LT1.5 - MS-SS]
- 'Package'[LT1.6 - RTD-NRTD]

## Ship From (Bottler / Geography)
- 'Ship From'[Country]
- 'Ship From'[Country Code]
- 'Ship From'[Business Unit]
- 'Ship From'[Region]
- 'Ship From'[Operating Group]
- 'Ship From'[BU Ship From]
- 'Ship From'[L1.0 - Bottler Franchise or CEDI]
- 'Ship From'[L1.1 - Bottler SubZone]
- 'Ship From'[L1.2 - Bottler Zone]
- 'Ship From'[L1.3 - Bottler]
- 'Ship From'[L1.4 - Field Unit]
- 'Ship From'[L1.5 - Country]
- 'Ship From'[L1.6 - Franchise Sub Region]
- 'Ship From'[L1.7 - Franchise Region]
- 'Ship From'[L1.8 - Franchise Unit Operations]
- 'Ship From'[L1.9 - Zone Operations]
- 'Ship From'[L1.10 - Operating Unit]

## Ship To (Customer)
- 'Ship To'[LT1.1 - Tradename]
- 'Ship To'[LT1.2 - Customer]
- 'Ship To'[LT1.3 - Business Sub Type]
- 'Ship To'[LT1.4 - Business Type]
- 'Ship To'[LT1.5 - Consumption Type]
- 'Ship To'[LT1.6 - Customer Leadership]

## Period
- 'Period'[Day 445]
- 'Period'[Day 445 Code]
- 'Period'[Day Cal]
- 'Period'[Day Cal Code]
- 'Period'[Week 445]
- 'Period'[Week 445 Code]
- 'Period'[Week 445 #]
- 'Period'[Week 445 Begin – End]
- 'Period'[Month 445]
- 'Period'[Month 445 Code]
- 'Period'[Month 445 #]
- 'Period'[Month 445 Name]
- 'Period'[Month 445 Begin – End]
- 'Period'[Month Cal]
- 'Period'[Month Cal Code]
- 'Period'[Quarter 445]
- 'Period'[Quarter 445 Code]
- 'Period'[Quarter 445 Name]
- 'Period'[Quarter Cal]
- 'Period'[Quarter Cal Code]
- 'Period'[Half 445]
- 'Period'[Half 445 Code]
- 'Period'[Half 445 Name]
- 'Period'[Half Cal]
- 'Period'[Half Cal Code]
- 'Period'[Year 445]
- 'Period'[Year 445 Code]
- 'Period'[Year Cal]
- 'Period'[Year Cal Code]

## Sales Type
- 'Sales Type'[BU Sales Type]
- 'Sales Type'[BU Sales Type Code]
- 'Sales Type'[Primary Sales Indicator]
- 'Sales Type'[Source Sales Type]

## Reporting View
- 'Reporting View'[Reporting View]

## Record Type
- 'Record Type'[Record Type]

## Discount Dimensions
- 'On Standard Discount'[On Standard Discount Category]
- 'On Standard Discount'[On Standard Discount Code]
- 'On Standard Discount'[On Standard Discount Concept]
- 'On Standard Discount Classification'[Discount Group]
- 'On Standard Discount Classification'[Sales Group]
- 'On Standard Discount Classification'[Discount Applied Flag]
- 'On Bulk Discount'[On Bulk Discount Category]
- 'On Bulk Discount'[On Bulk Discount Code]
- 'Off Discount'[Off Discount Category]
- 'Off Discount'[Off Discount Code]
- 'Other Discount'[Other Discount Category]
- 'Other Discount'[Other Discount Code]

# Business Rules

- For country/geography filtering, use 'Ship From'[Country] or 'Ship From'[L1.5 - Country]. Do NOT use 'Ship To'[Country] — it does not exist in this model.
- For channel breakdown, prefer 'Channel'[Trade Channel] unless the user specifies a more granular level.
- For product breakdown, prefer 'Product'[Beverage Category] or 'Product'[BPP] unless the user specifies a hierarchy level.
- The model uses two calendar systems: 445 calendar and Gregorian calendar. Default to 445 unless the user specifies Gregorian.
- Use only tables and columns listed in this context.
- Do not invent tables or columns.
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


def build_columns_context() -> str:
    return COLUMNS_CONTEXT


def build_combined_context(ontology_ctx: str, columns_ctx: str) -> str:
    """
    Merges metric context from the OntologicAgent with filter/dimension column context.
    Used by DaxQueryDeveloper and DaxValidator so they have the full picture.
    """
    parts = []
    if ontology_ctx:
        parts.append("# Metric Context (from Ontology)\n\n" + ontology_ctx)
    if columns_ctx:
        parts.append("# Available Filter and Dimension Columns\n\n" + columns_ctx)
    return "\n\n---\n\n".join(parts)


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


def run_basic_connection_test(nsr_conn) -> None:
    print_section("BASIC CONNECTION TEST")
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

    columns_context = build_columns_context()

    save_text(run_dir / "columns_context_used.md", columns_context)
    save_text(run_dir / "general_syn_used.md", GENERAL_SYN)
    save_text(run_dir / "user_query.txt", USER_QUERY)

    if not PATH_DLL.exists():
        raise FileNotFoundError(f"ADOMD DLL not found: {PATH_DLL}")

    print(">>> [LOGIN 1/2] Connecting to NSR LATAM [Test] — use your NSR LATAM account")
    nsr_conn = AdomdConnector(str(PATH_DLL), STR_CONN)
    run_basic_connection_test(nsr_conn)

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

    print(">>> [LOGIN 2/2] Connecting to mf-pocai-eastus2-dev-01 (ontology) — use your ontology account")
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

    # Capture the ontology context from the last loop iteration for downstream agents.
    final_ontology_ctx = ontology_context
    combined_context = build_combined_context(final_ontology_ctx, columns_context)
    save_text(run_dir / "combined_context_used.md", combined_context)

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
        dav=combined_context,
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
        semantic_context=combined_context,
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
{combined_context}

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
