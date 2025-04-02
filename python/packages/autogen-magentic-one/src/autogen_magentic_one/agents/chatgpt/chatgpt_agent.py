from typing import List, Tuple

from autogen_core.base import CancellationToken
from autogen_core.components import default_subscription
from autogen_core.components.models import (
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from ..base_worker import BaseWorker

@default_subscription
class ChatGPTAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "A general-purpose AI assistant to be consulted only when specialized agents cannot handle a specific task or when additional analysis is required."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage("""
        You are ChatGPT, a large language model trained by OpenAI. 
        Your knowledge cutoff is 2022, and you're able to assist with a wide range of tasks including but not limited to:
        - Answering questions on various topics
        - Providing explanations and clarifications
        - Offering creative writing assistance
        - Helping with problem-solving and brainstorming
        - Summarizing text
        - Creating TODO lists and organizing information
        - Providing coding assistance and explanations

        Limitations:
        You do not perform external actions such as sending messages or executing tasks on third-party platforms like Slack.
        Your role is strictly limited to providing information and well-structured outputs based on user input.

        Always strive to be helpful, harmless, and honest in your responses.
        
        Important: Provide direct and complete answers without ending with follow-up questions. Focus on delivering comprehensive information that fully addresses the users query."""),
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
    ) -> None:
        super().__init__(description)
        self._model_client = model_client
        self._system_messages = system_messages

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, str]:
        history = self._chat_history[0:-1]
        last_message = self._chat_history[-1]
        assert isinstance(last_message, UserMessage)

        create_result = await self._model_client.create(
            messages=self._system_messages + history + [last_message],
            cancellation_token=cancellation_token
        )

        response = create_result.content

        if isinstance(response, str):
            return False, response
        else:
            return False, "An error occurred while generating the response."
