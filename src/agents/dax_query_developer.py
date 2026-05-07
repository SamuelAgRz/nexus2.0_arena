from src.prompts.dax_developer import DAX_DEVELOPER_TEMPLATE, DAX_REVISION_TEMPLATE


class DaxQueryDeveloperAgent:
    def __init__(self, llm_client, general_syn: str, dav: str):
        self.llm = llm_client
        self.general_syn = general_syn
        self.dav = dav

    def run(self, instruction: str) -> str:
        system_prompt = (
            DAX_DEVELOPER_TEMPLATE
            .replace("{general_syn}", self.general_syn)
            .replace("{dav}", self.dav)
        )

        return self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=instruction
        ).strip()

    def revise(self, previous_dax: str, validator_feedback: str, business_question: str) -> str:
        system_prompt = (
            DAX_REVISION_TEMPLATE
            .replace("{dav}", self.dav)
        )

        user_prompt = f"""Business question:
{business_question}

Previous DAX:
{previous_dax}

Validator feedback:
{validator_feedback}
"""

        return self.llm.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        ).strip()