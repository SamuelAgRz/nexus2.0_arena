from prompts.dax_developer import DAX_DEVELOPER_TEMPLATE


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