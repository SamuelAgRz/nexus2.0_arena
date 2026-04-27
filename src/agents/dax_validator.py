from src.prompts.dax_validator import DAX_VALIDATOR_PROMPT

class DaxValidatorAgent:
    def __init__(self, llm_client, semantic_context: str):
        self.llm = llm_client
        self.semantic_context = semantic_context

    def run(self, business_question: str, dax_query: str) -> str:
        system_prompt = (
            DAX_VALIDATOR_PROMPT
            .replace("{semantic_context}", self.semantic_context)
        )

        user_prompt = f"""
Business question:
{business_question}

Candidate DAX:
{dax_query}
"""

        return self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        ).strip()