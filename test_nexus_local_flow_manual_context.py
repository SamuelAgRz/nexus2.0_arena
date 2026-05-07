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
USER_QUERY = "Show NSR including all channels and categories for Colombia"

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

# Raw Metric Columns (use only if no measure exists for the metric)

## Volume (from Metrics-Actuals-Vol)
- 'Metrics-Actuals-Vol'[unit_case_amt]
- 'Metrics-Actuals-Vol'[liter_amt]
- 'Metrics-Actuals-Vol'[phys_case_amt]
- 'Metrics-Actuals-Vol'[indv_unit_amt]
- 'Metrics-Actuals-Vol'[btlr_unit_case_amt]
- 'Metrics-Actuals-Vol'[purch_trx_amt]

## Revenue (from Metrics-Actuals-Rev)
- 'Metrics-Actuals-Rev'[btlr_gross_rev_amt]
- 'Metrics-Actuals-Rev'[btlr_net_sls_rev_amt]
- 'Metrics-Actuals-Rev'[btlr_wholesale_price]

## Plan / Estimate Revenue & Volume (Metrics-BP, Metrics-RE, Metrics-WE)
- 'Metrics-BP'[btlr_gross_rev_amt]
- 'Metrics-BP'[btlr_net_sls_rev_amt]
- 'Metrics-BP'[unit_case_amt]
- 'Metrics-RE'[btlr_gross_rev_amt]
- 'Metrics-RE'[btlr_net_sls_rev_amt]
- 'Metrics-RE'[unit_case_amt]
- 'Metrics-WE'[btlr_gross_rev_amt]
- 'Metrics-WE'[unit_case_amt]

## Discounts (raw)
- 'Metrics-Std-Discount'[dscnt_amt]
- 'Metrics-Bulk-Discount'[dscnt_amt]
- 'Metrics-Inv-Discount'[dscnt_amt]
- 'Metrics-Other-Discount'[dscnt_amt]

# Business Rules

- NSR means Net Sales Revenue. It is SELL-IN / bottler revenue, not sell-out / retail sales.
- Volume default unit is unit cases (unit_case_amt) unless the user specifies liters or physical cases.
- Default scenario is Actuals (Metrics-Actuals-Vol / Metrics-Actuals-Rev) unless the user explicitly asks for BP (Business Plan), RE (Rolling Estimate), or WE (Weekly Estimate).
- The model uses two calendar systems: 445 calendar and Gregorian calendar. Default to 445 unless the user specifies Gregorian.
- For country/geography filtering, use 'Ship From'[Country] or 'Ship From'[L1.5 - Country]. Do NOT use 'Ship To'[Country] — it does not exist in this model.
- For channel breakdown, prefer 'Channel'[Trade Channel] unless the user specifies a more granular level.
- For product breakdown, prefer 'Product'[Beverage Category] or 'Product'[BPP] unless the user specifies a hierarchy level.
- Use only tables and columns listed in this context.
- Do not invent tables, columns, or measures.
- IMPORTANT: This model has NO semantic measures. Do NOT use bracket measure syntax like [NSR], [NSR YTD], or any [Measure Name]. Always use raw column aggregations (e.g. SUM('Metrics-Actuals-Rev'[btlr_net_sls_rev_amt])).
- Return executable DAX only.

# Local Test Defaults

- If the user asks for "by channel" without further detail, use 'Channel'[Trade Channel].
- If the user asks for "YTD" without specifying a year, interpret it as the latest available YTD in the 445 calendar.
- If a requested filter dimension (e.g., a specific geography level) is not listed in this context, do NOT invent a column. Instead, generate the DAX without that filter and flag the missing object, OR ask the user for the correct column name.
- Prioritize executable DAX over perfect business filtering when columns are ambiguous.
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

- Scenario: Actuals.
- Channel granularity: 'Channel'[Trade Channel].
- Time: Latest year
- Geography: Colombia only if a valid Colombia/market/geography column is explicitly available in semantic context.
- If no valid Colombia column is available, do not invent one.

DAX generation task:
Generate an executable DAX query using SUMMARIZECOLUMNS that returns NSR by 'Channel'[Trade Channel].
NSR = SUM('Metrics-Actuals-Rev'[btlr_net_sls_rev_amt]). Do NOT use any measure like [NSR] — no measures exist in this model.
Return only executable DAX.
"""


def normalize_validator_response(response: Any) -> str:
    return str(response or "").strip()


def is_approved(validation_result: str) -> bool:
    text = validation_result.strip()
    if text.upper() == "APPROVED":
        return True
    try:
        import json
        parsed = json.loads(text)
        return str(parsed.get("status", "")).upper() == "APPROVED"
    except (json.JSONDecodeError, AttributeError):
        return False


def is_not_approved(validation_result: str) -> bool:
    text = validation_result.strip()
    if text.upper().startswith("NOT APPROVED"):
        return True
    try:
        import json
        parsed = json.loads(text)
        return str(parsed.get("status", "")).upper() in {"NOT_APPROVED", "NOT APPROVED"}
    except (json.JSONDecodeError, AttributeError):
        return False


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
            revised_dax = developer.revise(
                previous_dax=dax_query,
                validator_feedback=validation_result,
                business_question=fhb_instruction,
            )
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
