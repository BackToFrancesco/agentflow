import json
from typing import List, Tuple

from autogen_core.base import CancellationToken
from autogen_core.components import FunctionCall, default_subscription
from autogen_core.components.models import (
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_magentic_one.agents.agents_prompts import OUTLOOK_CALENDAR_RESULT_PRESENTATION_MESSAGE, OUTLOOK_CALENDAR_SYSTEM_MESSAGE, OUTLOOK_CALENDAR_SYSTEM_MESSAGE_AUTOFORM
from autogen_magentic_one.agents.outlook_calendar._tools import (
    TOOL_GET_CALENDAR_EVENTS,
    TOOL_CREATE_MEETING,
    TOOL_GET_AVAILABLE_SLOTS
)
from autogen_magentic_one.messages import AgentEvent
from ..base_worker import BaseWorker
from .outlook_calendar_api import OutlookCalendarAPI

@default_subscription
class OutlookCalendarAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "An agent that can interact with Outlook calendar. The agent is already authenticated to the Outlook calendar account."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage(OUTLOOK_CALENDAR_SYSTEM_MESSAGE),
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
        outlook_calendar_api: OutlookCalendarAPI = None,
        enable_multiple_turns: bool = False,
        autoform_prompt: bool = False
    ) -> None:
        super().__init__(description, enable_multiple_turns=enable_multiple_turns, autoform_prompt=autoform_prompt)
        self._model_client = model_client
        self._system_messages = [SystemMessage(OUTLOOK_CALENDAR_SYSTEM_MESSAGE_AUTOFORM if autoform_prompt else OUTLOOK_CALENDAR_SYSTEM_MESSAGE)]
        self._tools = [
            TOOL_GET_CALENDAR_EVENTS,
            TOOL_CREATE_MEETING,
            TOOL_GET_AVAILABLE_SLOTS
        ]
        self._outlook_calendar_api = outlook_calendar_api or OutlookCalendarAPI()
        self._autoform_prompt = autoform_prompt

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, str]:
        history = self._chat_history[0:-1]
        last_message = self._chat_history[-1]
        assert isinstance(last_message, UserMessage)

        task_content = last_message.content

        create_result = await self._model_client.create(
            messages= self._system_messages + history + [last_message], tools=self._tools, cancellation_token=cancellation_token
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
                    error_str = f"Outlook Calendar agent encountered an error decoding JSON arguments: {e}"
                    return False, error_str

                result = None
                description = ""
                if tool_name == "get_calendar_events":
                    filter_params = arguments.get("filter_params")
                    limit = arguments.get("limit")
                    result = self._outlook_calendar_api.get_calendar_events(filter_params, limit)
                    if "error" in result:
                        description = f"An error occurred while retrieving calendar events: {result['error']}"
                    else:
                        events = result.get("events", [])
                        event_count = len(events)
                        description = f"I've retrieved {event_count} calendar events based on your request. Parameters used: filter_params={filter_params}, limit={limit}"
                elif tool_name == "create_meeting":
                    subject = arguments["subject"]
                    start_time = arguments["start_time"]
                    end_time = arguments["end_time"]
                    attendees = arguments.get("attendees")
                    location = arguments.get("location")
                    body = arguments.get("body")
                    result = self._outlook_calendar_api.create_meeting(subject, start_time, end_time, attendees, location, body)
                    if "error" in result:
                        description = f"An error occurred while creating the meeting: {result['error']}"
                    else:
                        description = f"I've created the new meeting '{subject}'. Parameters used: subject='{subject}', start_time='{start_time}', end_time='{end_time}', attendees={attendees}, location='{location}', body='{body}'"
                elif tool_name == "get_available_slots":
                    result = self._outlook_calendar_api.get_available_slots(**arguments)
                    if "error" in result:
                        description = f"An error occurred while getting available slots: {result['error']}"
                    else:
                        slots = result.get("available_slots", [])
                        slot_count = len(slots)
                        description = f"I've found {slot_count} available slots based on your request. Parameters used: {', '.join([f'{k}={v}' for k, v in arguments.items()])}"

                if result is not None:
                    # Call the LLM to present the result
                    try:
                        llm_response = await self._model_client.create(
                            messages=[
                                SystemMessage(OUTLOOK_CALENDAR_RESULT_PRESENTATION_MESSAGE if self._autoform_prompt else OUTLOOK_CALENDAR_RESULT_PRESENTATION_MESSAGE),
                                UserMessage(f"Tool used: {tool_name}\nDescription: {description}\nResult: {json.dumps(result, indent=2)}", "OutlookCalendarAgent")
                            ],
                            cancellation_token=cancellation_token
                        )
                        return False, llm_response.content
                    except Exception as e:
                        error_str = f"Error occurred while generating LLM response: {str(e)}"
                        return False, f"{description}\n\n{error_str}\n\nRaw result:\n{json.dumps(result, indent=2)}"

        final_response = "TERMINATE"
        return False, final_response
