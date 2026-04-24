import os
from copy import deepcopy
from typing import Any

from dotenv import load_dotenv
from openai import AzureOpenAI


class AzureAIFoundry:
    """Manage Azure OpenAI client setup and notebook-friendly chat calls."""

    def __init__(
        self,
        *,
        endpoint: str | None = None,
        api_key: str | None = None,
        deployment: str = "gpt-5-mini",
        api_version: str = "2024-12-01-preview",
        system_prompt: str = "You are a helpful assistant.",
        load_environment: bool = True,
    ) -> None:
        if load_environment:
            load_dotenv()

        self.endpoint = endpoint or os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_AI_FOUNDRY_API_KEY")
        self.deployment = deployment
        self.api_version = api_version
        self.system_prompt = system_prompt

        self._validate_configuration()

        self.client = AzureOpenAI(
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
        )

        self._messages: list[dict[str, str]] = []
        self.reset_messages()

    def _validate_configuration(self) -> None:
        missing_settings = []
        if not self.endpoint:
            missing_settings.append("AZURE_AI_FOUNDRY_ENDPOINT")
        if not self.api_key:
            missing_settings.append("AZURE_AI_FOUNDRY_API_KEY")

        if missing_settings:
            names = ", ".join(missing_settings)
            raise ValueError(f"Missing required Azure AI Foundry settings: {names}")

    def reset_messages(self, system_prompt: str | None = None) -> None:
        if system_prompt is not None:
            self.system_prompt = system_prompt

        self._messages = [
            {
                "role": "system",
                "content": self.system_prompt,
            }
        ]

    def set_system_prompt(self, system_prompt: str, *, reset_messages: bool = True) -> None:
        self.system_prompt = system_prompt
        if reset_messages:
            self.reset_messages()

    def add_message(self, role: str, content: str) -> None:
        self._messages.append({"role": role, "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        return deepcopy(self._messages)

    def chat(
        self,
        user_message: str | None = None,
        *,
        system_prompt: str | None = None,
        user_prompt: str | None = None,
        use_memory: bool = False,
        **request_options: Any,
    ) -> str:
        """
        Supported modes:

        1) Stateless agent mode:
           chat(system_prompt="...", user_prompt="...", temperature=0.0)

        2) Stateful notebook mode:
           chat("Hello", temperature=0.0)

        If use_memory=True, the call mutates the stored conversation.
        """
        if user_prompt is not None:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            response = self.client.chat.completions.create(
                messages=messages,
                model=self.deployment,
                **request_options,
            )
            return response.choices[0].message.content or ""

        if user_message is None:
            raise ValueError("Provide either user_message or user_prompt.")

        if use_memory:
            self.add_message("user", user_message)
            response = self.client.chat.completions.create(
                messages=self._messages,
                model=self.deployment,
                **request_options,
            )
            assistant_message = response.choices[0].message.content or ""
            self.add_message("assistant", assistant_message)
            return assistant_message

        messages = [{"role": "system", "content": self.system_prompt}]
        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            messages=messages,
            model=self.deployment,
            **request_options,
        )
        return response.choices[0].message.content or ""

    def complete(self, messages: list[dict[str, str]], **request_options: Any) -> Any:
        return self.client.chat.completions.create(
            messages=messages,
            model=self.deployment,
            **request_options,
        )