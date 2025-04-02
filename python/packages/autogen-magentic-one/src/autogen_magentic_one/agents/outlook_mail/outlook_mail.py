import json
from typing import List, Tuple

from autogen_core.base import CancellationToken
from autogen_core.components import FunctionCall, default_subscription
from autogen_core.components.models import (
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_magentic_one.agents.outlook_mail._tools import (
    TOOL_RETRIEVE_UNREAD_EMAILS,
    # TOOL_GET_ALL_EMAILS,
    TOOL_MOVE_EMAIL_TO_FOLDER,
    TOOL_GET_EMAIL_FOLDERS,
    TOOL_CREATE_EMAIL_FOLDER,
    # TOOL_GET_EMAIL_BY_ID,
    TOOL_SEARCH_EMAILS,
    # TOOL_SEND_EMAIL,
    TOOL_REPLY_TO_MAIL
)
from autogen_magentic_one.messages import AgentEvent
from ..base_worker import BaseWorker
from .outlook_api import OutlookAPI
from ..agents_prompts import OUTLOOK_CALENDAR_RESULT_PRESENTATION_MESSAGE_AUTOFORM, OUTLOOK_MAIL_RESULT_PRESENTATION_MESSAGE_AUTOFORM, OUTLOOK_MAIL_SYSTEM_MESSAGE, OUTLOOK_MAIL_RESULT_PRESENTATION_MESSAGE, OUTLOOK_MAIL_SYSTEM_MESSAGE_AUTOFORM

@default_subscription
class OutlookAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "An agent that can interact with Outlook emails. The agent is already authenticated to the Outlook account."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage(OUTLOOK_MAIL_SYSTEM_MESSAGE),
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
        outlook_api: OutlookAPI = None,
        enable_multiple_turns: bool = False,
        autoform_prompt: bool = False
    ) -> None:
        super().__init__(description, enable_multiple_turns=enable_multiple_turns, autoform_prompt=autoform_prompt)
        self._model_client = model_client
        self._system_messages = [SystemMessage(OUTLOOK_MAIL_SYSTEM_MESSAGE_AUTOFORM if autoform_prompt else OUTLOOK_MAIL_SYSTEM_MESSAGE)]
        self._tools = [
            TOOL_RETRIEVE_UNREAD_EMAILS,
            # TOOL_GET_ALL_EMAILS,
            TOOL_MOVE_EMAIL_TO_FOLDER,
            TOOL_GET_EMAIL_FOLDERS,
            TOOL_CREATE_EMAIL_FOLDER,
            # TOOL_GET_EMAIL_BY_ID,
            TOOL_SEARCH_EMAILS,
            # TOOL_SEND_EMAIL,
            TOOL_REPLY_TO_MAIL
        ]
        self._outlook_api = outlook_api or OutlookAPI()
        self._autoform_prompt = autoform_prompt

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, str]:
        history = self._chat_history[0:-1]
        last_message = self._chat_history[-1]
        assert isinstance(last_message, UserMessage)

        task_content = last_message.content

        create_result = await self._model_client.create(
            messages= self.DEFAULT_SYSTEM_MESSAGES + history + [last_message], tools=self._tools, cancellation_token=cancellation_token
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
                    error_str = f"Outlook agent encountered an error decoding JSON arguments: {e}"
                    return False, error_str

                result = None
                description = ""
                if tool_name == "get_unread_emails":
                    result = self._outlook_api.get_unread_emails()
                    if "error" in result:
                        description = f"An error occurred while retrieving unread emails: {result['error']}"
                    else:
                        unread_count = len(result["emails"])
                        description = f"I've retrieved the unread emails. There are {unread_count} unread emails in your inbox."
                elif tool_name == "get_all_emails":
                    filter_params = arguments.get("filter_params")
                    limit = arguments.get("limit")
                    result = self._outlook_api.get_all_emails(filter_params, limit)
                    if "error" in result:
                        description = f"An error occurred while retrieving emails: {result['error']}"
                    else:
                        email_count = len(result["emails"])
                        description = f"I've retrieved {email_count} emails based on your request."
                elif tool_name == "move_email_to_folder":
                    email_id = arguments["email_id"]
                    folder_id = arguments["folder_id"]
                    result = self._outlook_api.move_email_to_folder(email_id, folder_id)
                    if "error" in result:
                        description = f"An error occurred while moving the email: {result.get('error', 'Unknown error')}."
                    else:
                        description = f"I've successfully moved the email with ID {email_id} to the folder with ID {folder_id}."
                elif tool_name == "get_email_folders":
                    result = self._outlook_api.get_email_folders()
                    if "error" in result:
                        description = f"An error occurred while retrieving email folders: {result['error']}"
                    else:
                        folder_count = len(result["folders"])
                        description = f"I've retrieved your email folders. You have {folder_count} folders in total."
                elif tool_name == "create_email_folder":
                    folder_name = arguments["folder_name"]
                    result = self._outlook_api.create_email_folder(folder_name)
                    if "error" in result:
                        description = f"An error occurred while creating the email folder: {result.get('error', 'Unknown error')}."
                    else:
                        description = f"I've successfully created a new email folder named '{folder_name}'. The folder ID is {result.get('folder_id')}."
                elif tool_name == "get_email_by_id":
                    email_id = arguments["email_id"]
                    result = self._outlook_api.get_email_by_id(email_id)
                    description = f"I've retrieved the email with ID {email_id}."
                elif tool_name == "search_emails":
                    query = arguments["query"]
                    result = self._outlook_api.search_emails(query)
                    email_count = len(json.loads(result))
                    description = f"I've searched for emails using the query '{query}'. Found {email_count} matching emails."
                elif tool_name == "send_email":
                    subject = arguments["subject"]
                    body = arguments["body"]
                    to_recipients = arguments["to_recipients"]
                    result = self._outlook_api.send_email(subject, body, to_recipients)
                    if result["result"] == "success":
                        description = f"I've successfully sent the email with subject '{subject}' to {', '.join(to_recipients)}. The message body was: '{body}'. The message ID is {result['message_id']}."
                    elif result["result"] == "rejected":
                        description = f"The email with subject '{subject}' to {', '.join(to_recipients)} was not sent because: {result['message']}"
                    else:
                        description = f"An error occurred while sending the email with subject '{subject}' to {', '.join(to_recipients)}: {result['message']}"
                elif tool_name == "reply_to_mail":
                    message_id = arguments["message_id"]
                    comment = arguments["comment"]
                    result = self._outlook_api.reply_to_mail(message_id, comment)
                    if result["result"] == "success":
                        description = f"I've successfully replied to the email with message ID {message_id}. The reply content was: '{comment}'. The new message ID is {result['message_id']}."
                    elif result["result"] == "rejected":
                        description = f"The reply to email with message ID {message_id} was not sent because: {result['message']}"
                    else:
                        description = f"An error occurred while replying to the email with message ID {message_id}: {result['message']}"

                if result is not None:
                    # Call the LLM to present the result
                    print(f"---CALLED TOOL:---")
                    print(tool_name)
                    try:
                        llm_response = await self._model_client.create(
                            messages=[
                                SystemMessage(OUTLOOK_MAIL_RESULT_PRESENTATION_MESSAGE_AUTOFORM if self._autoform_prompt else OUTLOOK_MAIL_RESULT_PRESENTATION_MESSAGE),
                                UserMessage(f"Tool used: {tool_name}\nDescription: {description}\nResult: {json.dumps(result, indent=2)}", "OutlookMailAgent")
                            ],
                            cancellation_token=cancellation_token
                        )
                        return False, llm_response.content
                    except Exception as e:
                        error_str = f"Error occurred while generating LLM response: {str(e)}"
                        return False, f"{description}\n\n{error_str}\n\nRaw result:\n{json.dumps(result, indent=2)}"

        final_response = "TERMINATE"
        return False, final_response
