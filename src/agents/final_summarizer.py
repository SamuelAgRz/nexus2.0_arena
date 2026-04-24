
from prompts.result_summarizer import FINAL_SUMMARIZER_PROMPT

class FinalSummarizerAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

    def run(self, user_query: str, dax_summary: str = "", viz_note: str = "") -> str:
        user_prompt = f"""
User query:
{user_query}

DAX summary:
{dax_summary}

Visualization note:
{viz_note}
"""
        return self.llm.chat(FINAL_SUMMARIZER_PROMPT, user_prompt)
