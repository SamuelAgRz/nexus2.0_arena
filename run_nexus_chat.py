import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"C:\Users\SamuelAguilarRamirez\nexus2.0")
sys.path.insert(0, str(PROJECT_ROOT))

from src.llm_client import AzureAIFoundry
from src.agents.intent_clarifier import IntentClarifierAgent
from src.agents.dax_query_developer import DaxQueryDeveloperAgent
from src.agents.dax_validator import DaxValidatorAgent
from src.connections.nsr_conn import AdomdConnector
from src.agents.dax_executor import DaxExecutorAgent


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
- Do not use 'Ship To'[Country] because it does not exist.
"""


def is_dax_query(text: str) -> bool:
    cleaned = text.strip().upper()
    return cleaned.startswith("EVALUATE") or cleaned.startswith("DEFINE")


def get_fhb_instruction(intent: dict) -> str | None:
    for agent in intent.get("agents", []):
        if agent.get("name") == "FHB_dataset":
            return agent.get("instruction")
    return None


def validate_dax(validator, developer, instruction: str, dax_query: str, max_iterations: int = 3):
    for i in range(max_iterations):
        print(f"\n=== DAX VALIDATION ITERATION {i + 1} ===")

        validation_result = validator.run(
            business_question=instruction,
            dax_query=dax_query,
        )

        print(validation_result)

        if validation_result.strip().upper() == "APPROVED":
            return dax_query, validation_result, True

        if validation_result.strip().upper().startswith("NOT APPROVED"):
            revision_instruction = f"""
Original instruction:
{instruction}

Previous DAX:
{dax_query}

Validator feedback:
{validation_result}

Fix ONLY the required issues.
Preserve the original business intent.
Return ONLY the corrected DAX query.
"""
            dax_query = developer.run(revision_instruction)
            print("\n=== REVISED DAX ===")
            print(dax_query)
        else:
            return dax_query, validation_result, False

    return dax_query, "Max validation iterations reached.", False


def main():
    print("=== Nexus 2.0 Local Chat ===")
    print("Type 'exit' to quit.\n")

    llm = AzureAIFoundry()

    intent_agent = IntentClarifierAgent(
        llm,
        general_syn=GENERAL_SYN,
        dav=SEMANTIC_CONTEXT,
    )

    developer = DaxQueryDeveloperAgent(
        llm,
        general_syn=GENERAL_SYN,
        dav=SEMANTIC_CONTEXT,
    )

    validator = DaxValidatorAgent(
        llm_client=llm,
        semantic_context=SEMANTIC_CONTEXT,
    )

    nsr_conn = AdomdConnector(str(PATH_DLL), STR_CONN)
    executor = DaxExecutorAgent(nsr_conn)

    conversation_context = ""

    while True:
        user_query = input("\nUser: ").strip()

        if user_query.lower() in {"exit", "quit", "salir"}:
            print("Bye.")
            break

        if not user_query:
            continue

        enriched_query = f"""
Conversation context:
{conversation_context}

Current user message:
{user_query}
""".strip()

        print("\n=== INTENT CLARIFIER ===")
        intent = intent_agent.run(enriched_query)
        print(intent)
        if intent.get("intent") == "clarification":
                message = intent["agents"][0]["instruction"]
                print("\n=== CLARIFICATION REQUIRED ===")
                print(message)

                conversation_context += f"""
        User: {user_query}
        Assistant:
        {message}
        """
        continue

        fhb_instruction = get_fhb_instruction(intent)
        if not fhb_instruction:
            summarizer_instruction = None

            for agent in intent.get("agents", []):
                if agent.get("name") == "Summarizer":
                    summarizer_instruction = agent.get("instruction")
                    break
                
            if summarizer_instruction:
                print("\n=== SUMMARIZER ===")
                response = llm.chat(
                    system_prompt="You are the Summarizer agent. Respond concisely and in the user's language.",
                    user_prompt=summarizer_instruction,
                )
                print(response)

                conversation_context += f"""
        User: {user_query}
        Assistant:
        {response}
        """
                continue
            
            print("\nNo executable data action found.")
            continue
        if not fhb_instruction:
            print("\nNo FHB_dataset instruction found.")
            conversation_context += f"\nUser: {user_query}\nAssistant: No data action required."
            continue

        print("\n=== FHB INSTRUCTION ===")
        print(fhb_instruction)

        print("\n=== DAX QUERY DEVELOPER ===")
        dax_or_clarification = developer.run(fhb_instruction)
        print(dax_or_clarification)

        if not is_dax_query(dax_or_clarification):
            print("\n=== CLARIFICATION REQUIRED ===")
            print(dax_or_clarification)

            conversation_context += f"""
User: {user_query}
Assistant clarification:
{dax_or_clarification}
"""
            continue

        dax_query = dax_or_clarification

        dax_query, validation_result, approved = validate_dax(
            validator=validator,
            developer=developer,
            instruction=fhb_instruction,
            dax_query=dax_query,
        )

        if not approved:
            print("\n=== DAX NOT APPROVED ===")
            print(validation_result)
            conversation_context += f"""
User: {user_query}
Assistant: DAX validation failed.
Validator response:
{validation_result}
"""
            continue

        print("\n=== EXECUTING APPROVED DAX ===")
        print(dax_query)

        df = executor.run(dax_query)

        print("\n=== RESULT ===")
        print(df.head(30))

        conversation_context += f"""
User: {user_query}
Approved DAX:
{dax_query}
Result preview:
{df.head(10).to_string(index=False)}
"""


if __name__ == "__main__":
    main()