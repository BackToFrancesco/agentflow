import json
from typing import List, Tuple, Optional

from autogen_core.base import CancellationToken
from autogen_core.components import FunctionCall, default_subscription
from autogen_core.components.models import ChatCompletionClient, SystemMessage, UserMessage

from ..base_worker import BaseWorker

@default_subscription
class GenericAgent(BaseWorker):
    """An LLM-powered agent that processes tasks via function calls and text generation."""

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = "A general-purpose LLM-powered agent.",
        system_messages: List[SystemMessage] = None,
        tools: Optional[List] = None,
    ) -> None:
        super().__init__(description)
        self._model_client = model_client
        self._system_messages = system_messages or [SystemMessage("Define agent behavior here.")]
        self._tools = tools or []

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, str]:
        """Processes user input, generates a response, or executes a function call."""
        history, last_message = self._chat_history[:-1], self._chat_history[-1]

        result = await self._model_client.create(
            messages=self._system_messages + history + [last_message],
            tools=self._tools, 
            cancellation_token=cancellation_token
        )

        if isinstance(result.content, str):
            return False, result.content

        if isinstance(result.content, list) and all(isinstance(item, FunctionCall) for item in result.content):
            return await self._handle_function_calls(result.content, cancellation_token)

        return False, "TERMINATE"

    async def _handle_function_calls(self, function_calls: List[FunctionCall], cancellation_token: CancellationToken) -> Tuple[bool, str]:
        """Executes requested functions and generates responses."""
        for function_call in function_calls:
            tool_name, arguments = function_call.name, json.loads(function_call.arguments)
            result = self._execute_tool(tool_name, arguments)
            return False, json.dumps(result, indent=2)

    def _execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Simulated function execution for tool calls."""
        return {"status": "success", "message": f"Executed {tool_name} with {arguments}"}
