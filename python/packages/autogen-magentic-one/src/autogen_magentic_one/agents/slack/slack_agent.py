import json
from typing import List, Tuple

from autogen_core.base import CancellationToken
from autogen_core.components import FunctionCall, default_subscription
from autogen_core.components.models import (
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_magentic_one.agents.slack._tools import (
    TOOL_SEND_MESSAGE,
    # TOOL_SEND_PRIVATE_MESSAGE,
    # TOOL_GET_UNREAD_MESSAGES,
    TOOL_LIST_CHANNELS,
    TOOL_GET_CHANNEL_MESSAGES
)
from autogen_magentic_one.messages import AgentEvent
from ..base_worker import BaseWorker
from .slack_api import SlackAPI
from ..agents_prompts import SLACK_RESULT_PRESENTATION_MESSAGE_AUTOFORM, SLACK_SYSTEM_MESSAGE, SLACK_RESULT_PRESENTATION_MESSAGE, SLACK_SYSTEM_MESSAGE_AUTOFORM

import re

def transform_bold_to_jira_bold(message):
    return re.sub(r'\*\*(.+?)\*\*', r'*\1*', message)

@default_subscription
class SlackAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "An agent that can interact with Slack. The agent is already authenticated to the Slack account."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage(SLACK_SYSTEM_MESSAGE),
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
        slack_api: SlackAPI = None,
        enable_multiple_turns: bool = False,
        autoform_prompt: bool = False
    ) -> None:
        super().__init__(description, enable_multiple_turns=enable_multiple_turns, autoform_prompt=autoform_prompt)
        self._model_client = model_client
        self._system_messages = [SystemMessage(SLACK_SYSTEM_MESSAGE_AUTOFORM if autoform_prompt else SLACK_SYSTEM_MESSAGE)]
        self._tools = [
            TOOL_SEND_MESSAGE,
            # TOOL_SEND_PRIVATE_MESSAGE,
            # TOOL_GET_UNREAD_MESSAGES,
            TOOL_LIST_CHANNELS,
            TOOL_GET_CHANNEL_MESSAGES
        ]
        self._slack_api = slack_api or SlackAPI()
        self._autoform_prompt = autoform_prompt

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, str]:
        history = self._chat_history[0:-1]
        last_message = self._chat_history[-1]
        assert isinstance(last_message, UserMessage)

        task_content = last_message.content

        create_result = await self._model_client.create(
            messages=self._system_messages + history + [last_message], tools=self._tools, cancellation_token=cancellation_token
        )

        response = create_result.content

        # self.logger.info(
        #     AgentEvent(
        #         f"{self.metadata['type']} (LLM API RESPONSE)",
        #         str(response),
        #     )
        # )

        if isinstance(response, str):
            return False, response

        elif isinstance(response, list) and all(isinstance(item, FunctionCall) for item in response):
            function_calls = response
            for function_call in function_calls:
                tool_name = function_call.name

                try:
                    arguments = json.loads(function_call.arguments)
                except json.JSONDecodeError as e:
                    error_str = f"Slack agent encountered an error decoding JSON arguments: {e}"
                    return False, error_str

                result = None
                description = ""
                if tool_name == "send_message":
                    channel = arguments["channel"]
                    message = arguments["message"]
                    formatted_message = transform_bold_to_jira_bold(message=message)
                    use_user_token = arguments.get("use_user_token", False)

                    result = self._slack_api.send_message(channel, formatted_message, use_user_token)
                    if "error" in result:
                        description = f"An error occurred while sending the message: {result['error']}"
                    else:
                        description = f"I've sent the message to the channel '{channel}'. Parameters used: channel='{channel}', message='{message}', use_user_token={use_user_token}"
                elif tool_name == "send_private_message":
                    user_id = arguments["user_id"]
                    message = arguments["message"]
                    use_user_token = arguments.get("use_user_token", False)
                    result = self._slack_api.send_private_message(user_id, message, use_user_token)
                    if "error" in result:
                        description = f"An error occurred while sending the private message: {result['error']}"
                    else:
                        description = f"I've sent a private message to the user with ID '{user_id}'. Parameters used: user_id='{user_id}', message='{message}', use_user_token={use_user_token}"
                elif tool_name == "get_unread_messages":
                    channel = arguments["channel"]
                    use_user_token = arguments.get("use_user_token", False)
                    result = self._slack_api.get_unread_messages(channel, use_user_token)
                    if "error" in result:
                        description = f"An error occurred while getting unread messages: {result['error']}"
                    else:
                        unread_messages = result.get("unread_messages", [])
                        message_count = len(unread_messages)
                        description = f"I've retrieved {message_count} unread messages from the channel '{channel}'. Parameters used: channel='{channel}', use_user_token={use_user_token}"
                elif tool_name == "list_channels":
                    use_user_token = arguments.get("use_user_token", False)
                    result = self._slack_api.list_channels(use_user_token)
                    if "error" in result:
                        description = f"An error occurred while listing channels: {result['error']}"
                    else:
                        channels = result.get("channels", [])
                        channel_count = len(channels)
                        description = f"I've retrieved a list of {channel_count} channels. Parameters used: use_user_token={use_user_token}"
                elif tool_name == "get_channel_messages":
                    channel = arguments["channel"]
                    use_user_token = arguments.get("use_user_token", False)
                    result = self._slack_api.get_channel_messages(channel, use_user_token)
                    if "error" in result:
                        description = f"An error occurred while getting channel messages: {result['error']}"
                    else:
                        messages = result.get("messages", [])
                        message_count = len(messages)
                        description = f"I've retrieved {message_count} messages from the channel '{channel}'. Parameters used: channel='{channel}', use_user_token={use_user_token}"

                if result is not None:
                    # Call the LLM to present the result
                    try:
                        llm_response = await self._model_client.create(
                            messages=[
                                SystemMessage(SLACK_RESULT_PRESENTATION_MESSAGE_AUTOFORM if self._autoform_prompt else SLACK_RESULT_PRESENTATION_MESSAGE),
                                UserMessage(f"Tool used: {tool_name}\nDescription: {description}\nResult: {json.dumps(result, indent=2)}", "SlackAgent")
                            ],
                            cancellation_token=cancellation_token
                        )
                        return False, llm_response.content
                    except Exception as e:
                        error_str = f"Error occurred while generating LLM response: {str(e)}"
                        return False, f"{description}\n\n{error_str}\n\nRaw result:\n{json.dumps(result, indent=2)}"

        final_response = "TERMINATE"
        return False, final_response
