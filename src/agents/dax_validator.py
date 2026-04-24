
from prompts.dax_validator import DAX_VALIDATOR_TEMPLATE

class DaxValidatorAgent:
    def __init__(self, llm_client, semantic_context: str):
        self.llm = llm_client
        self.semantic_context = semantic_context

    def run(self, business_question: str, dax_query: str) -> str:
        system_prompt = DAX_VALIDATOR_TEMPLATE.format(semantic_context=self.semantic_context)
        user_prompt = f"Business question:\n{business_question}\n\nCandidate DAX:\n{dax_query}"
        return self.llm.chat(system_prompt, user_prompt).strip()
