
from prompts.result_summarizer import DAX_RESULT_SUMMARIZER_PROMPT

class DaxResultSummarizerAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, business_question: str, dax_result: dict) -> str:
        user_prompt = f"Question:\n{business_question}\n\nResult:\n{dax_result}"
        return self.llm.chat(DAX_RESULT_SUMMARIZER_PROMPT, user_prompt)
