import os
import sys
from pathlib import Path

# --------------------------------------------------
# Project path
# --------------------------------------------------
PROJECT_ROOT = Path(r"C:\Users\SamuelAguilarRamirez\nexus2.0")
sys.path.insert(0, str(PROJECT_ROOT))

# --------------------------------------------------
# Imports
# --------------------------------------------------
from src.llm_client import AzureAIFoundry
from src.agents.intent_clarifier import IntentClarifierAgent
from src.agents.dax_query_developer import DaxQueryDeveloperAgent
from src.agents.dax_validator import DaxValidatorAgent
from src.connections.nsr_conn import AdomdConnector
from src.agents.dax_executor import DaxExecutorAgent


# --------------------------------------------------
# Config
# --------------------------------------------------
PATH_DLL = PROJECT_ROOT / "lib" / "Microsoft.AnalysisServices.AdomdClient.dll"

STR_CONN = (
    "Provider=MSOLAP;"
    "Data Source=powerbi://api.powerbi.com/v1.0/myorg/NSR LATAM [Test];"
    "Initial Catalog=NSR LATAM Cube;"
    "Integrated Security=ClaimsToken;"
)

GENERAL_SYN = """
NSR = Net Sales Revenue
market = Ship To
channel = Trade Channel
"""

SEMANTIC_CONTEXT = """
Target model: NSR LATAM semantic model

Tables and columns available:

Channel:
- 'Channel'[Trade Channel]
- 'Channel'[Sub Trade Channel]

Ship To:
- 'Ship To'[Source Ship To Code]
- 'Ship To'[LT1.1 - Tradename]
- 'Ship To'[LT1.2 - Customer]

Period:
- 'Period'[Date]
- 'Period'[Year]
- 'Period'[Month]
- 'Period'[Week]

Measures:
- [NSR]
- [NSR YTD]

Business Rules:
- NSR is Net Sales Revenue (SELL-IN).
- Use only tables, columns, and measures listed here.
- Do not invent columns or measures.
- For channel breakdown, use 'Channel'[Trade Channel].
- Do not use 'Channel'[Channel].
- Do not use 'Ship To'[Country] unless it appears explicitly in this context.
"""


# --------------------------------------------------
# Main flow
# --------------------------------------------------
def main():
    print("=== Nexus 2.0 Local Agent Flow ===")

    user_query = "Show NSR YTD by channel for Colombia"

    # 1. LLM Client
    llm = AzureAIFoundry()

    # 2. Intent Clarifier
    intent_agent = IntentClarifierAgent(
        llm,
        general_syn=GENERAL_SYN,
        dav=SEMANTIC_CONTEXT,
    )

    intent = intent_agent.run(user_query)

    print("\n=== INTENT ===")
    print(intent)

    fhb_instruction = None

    for agent in intent.get("agents", []):
        if agent.get("name") == "FHB_dataset":
            fhb_instruction = agent.get("instruction")
            break

    if not fhb_instruction:
        raise RuntimeError("No FHB_dataset instruction found in intent.")

    print("\n=== FHB INSTRUCTION ===")
    print(fhb_instruction)

    # 3. DAX Developer
    developer = DaxQueryDeveloperAgent(
        llm,
        general_syn=GENERAL_SYN,
        dav=SEMANTIC_CONTEXT,
    )

    dax_query = developer.run(fhb_instruction)

    print("\n=== DAX GENERATED ===")
    print(dax_query)

    # 4. DAX Validator
    validator = DaxValidatorAgent(
        llm_client=llm,
        semantic_context=SEMANTIC_CONTEXT,
    )

    max_iterations = 3
    validation_result = None

    for i in range(max_iterations):
        print(f"\n=== VALIDATION ITERATION {i + 1} ===")

        validation_result = validator.run(
            business_question=fhb_instruction,
            dax_query=dax_query,
        )

        print(validation_result)

        if validation_result.strip().upper() == "APPROVED":
            break

        if validation_result.strip().upper().startswith("NOT APPROVED"):
            revision_instruction = f"""
Original instruction:
{fhb_instruction}

Previous DAX:
{dax_query}

Validator feedback:
{validation_result}

Fix ONLY the required issues.
Return ONLY the corrected DAX query.
"""
            dax_query = developer.run(revision_instruction)

            print("\n=== REVISED DAX ===")
            print(dax_query)
        else:
            raise RuntimeError(f"Unexpected validator response: {validation_result}")

    if validation_result.strip().upper() != "APPROVED":
        raise RuntimeError("DAX was not approved after validation loop.")

    # 5. DAX Executor
    print("\n=== EXECUTING APPROVED DAX ===")
    print("DLL:", PATH_DLL)
    print("DLL exists:", PATH_DLL.exists())

    nsr_conn = AdomdConnector(str(PATH_DLL), STR_CONN)
    executor = DaxExecutorAgent(nsr_conn)

    df_result = executor.run(dax_query)

    print("\n=== RESULT ===")
    print(df_result.head(20))


if __name__ == "__main__":
    main()