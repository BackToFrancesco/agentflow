import json
from typing import List, Tuple

from autogen_core.base import CancellationToken
from autogen_core.components import FunctionCall, default_subscription
from autogen_core.components.models import (
    ChatCompletionClient,
    SystemMessage,
    UserMessage,
)
from autogen_magentic_one.agents.jira._tools import (
    TOOL_CREATE_ISSUE,
    TOOL_GET_PROJECT_ISSUES
)
from autogen_magentic_one.messages import AgentEvent
from ..base_worker import BaseWorker
from .jira_api import JiraAPI
from ..agents_prompts import JIRA_RESULT_PRESENTATION_MESSAGE_AUTOFORM, JIRA_SYSTEM_MESSAGE, JIRA_RESULT_PRESENTATION_MESSAGE, JIRA_SYSTEM_MESSAGE_AUTOFORM

@default_subscription
class JiraAgent(BaseWorker):
    DEFAULT_DESCRIPTION = "An agent that can interact with Jira. The agent is already authenticated to the Jira account."

    DEFAULT_SYSTEM_MESSAGES = [
        SystemMessage(JIRA_SYSTEM_MESSAGE),
    ]

    def __init__(
        self,
        model_client: ChatCompletionClient,
        description: str = DEFAULT_DESCRIPTION,
        system_messages: List[SystemMessage] = DEFAULT_SYSTEM_MESSAGES,
        jira_api: JiraAPI = None,
        enable_multiple_turns=False,
        autoform_prompt = False
    ) -> None:
        super().__init__(description, enable_multiple_turns=enable_multiple_turns, autoform_prompt=autoform_prompt)
        self._model_client = model_client
        self._system_messages = [SystemMessage(JIRA_SYSTEM_MESSAGE_AUTOFORM if autoform_prompt else JIRA_SYSTEM_MESSAGE)]
        self._tools = [
            TOOL_CREATE_ISSUE,
            TOOL_GET_PROJECT_ISSUES
        ]
        self._jira_api = jira_api or JiraAPI()
        projects = self._jira_api.get_all_projects()
        if "error" in projects:
            print(f"An error occurred while retrieving projects: {projects['error']}")
        else:
            self._chat_history.append(UserMessage(content=f"Current Projects: {projects}", source="system"))
        self._autoform_promt = autoform_prompt

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
                    error_str = f"Jira agent encountered an error decoding JSON arguments: {e}"
                    return False, error_str

                result = None
                description = ""
                if tool_name == "create_issue":
                    project_key = arguments["project_key"]
                    issue_type = arguments["issue_type"]
                    summary = arguments["summary"]
                    description = arguments["description"]
                    result = self._jira_api.create_issue(project_key, issue_type, summary, description)
                    if "error" in result:
                        description = f"An error occurred while creating the issue for project key '{project_key}': {result['error']}"
                    elif result.get("status") == "rejected":
                        description = result["message"]
                    else:
                        description = f"I've created a new issue '{summary}' with issue type '{issue_type}', description '{description}' in project '{project_key}'."
                elif tool_name == "get_project_issues":
                    project_name = arguments["project_name"]
                    result = self._jira_api.get_project_issues(project_name)
                    if isinstance(result, dict) and "error" in result:
                        description = f"An error occurred while retrieving project issues for project name '{project_name}': {result['error']}"
                    else:
                        issue_count = len(result)
                        description = f"I've retrieved {issue_count} issues from the project '{project_name}'."

                if result is not None:
                    # Call the LLM to present the result
                    try:
                        llm_response = await self._model_client.create(
                            messages=[
                                SystemMessage(JIRA_RESULT_PRESENTATION_MESSAGE_AUTOFORM if self._autoform_promt else JIRA_RESULT_PRESENTATION_MESSAGE),
                                UserMessage(f"Tool used: {tool_name}\nDescription: {description}\nResult: {json.dumps(result, indent=2)}", "JiraAgent")
                            ],
                            cancellation_token=cancellation_token
                        )
                        return False, llm_response.content
                    except Exception as e:
                        error_str = f"Error occurred while generating LLM response: {str(e)}"
                        return False, f"{description}\n\n{error_str}\n\nRaw result:\n{json.dumps(result, indent=2)}"

        final_response = "TERMINATE"
        return False, final_response
