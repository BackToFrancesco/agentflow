import asyncio
import json
import logging
import os
import unittest
from unittest.mock import patch
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.models._types import UserMessage
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.jira.jira_agent import JiraAgent
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env

# Set this to True if you want to skip the tests
SKIP_ORCHESTATOR_TESTS = False
SKIP_AGENTS_TESTS = True

# Set up logging
logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.CRITICAL)

class TestJiraAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.logs_dir = "./logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        self.logger = logging.getLogger(EVENT_LOGGER_NAME)
        self.logger.setLevel(logging.INFO)
        log_handler = LogHandler(filename=os.path.join(self.logs_dir, "log.jsonl"))
        self.logger.handlers = [log_handler]

        self.runtime = SingleThreadedAgentRuntime()
        self.client = create_completion_client_from_env(model="gpt-4o-mini")

    async def asyncTearDown(self):
        try:
            await self.runtime.stop_when_idle()
        except Exception as e:
            logger2.error(f"Error stopping runtime: {e}")

    @unittest.skipIf(SKIP_AGENTS_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.jira.jira_api.JiraAPI')
    async def test_get_project_issues_and_create_issue(self, mock_jira_api):
        mock_api_instance = mock_jira_api.return_value
        mock_api_instance.get_project_issues.return_value = [
            {"Key": "FER-1", "Summary": "Design car chassis", "Status": "In Progress"},
            {"Key": "FER-2", "Summary": "Implement engine control system", "Status": "To Do"}
        ]
        mock_api_instance.create_issue.return_value = {
            "id": "10001",
            "key": "FER-3",
            "name": "Create the GUI"
        }
        mock_api_instance.get_all_projects.return_value = [
            {"name": "Ferrari", "key": "FER", "id": "10000"}
        ]

        await JiraAgent.register(self.runtime, "JiraAgent", lambda: JiraAgent(model_client=self.client))
        jira_agent = AgentProxy(AgentId("JiraAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "show me all issues for project 'Ferrari' and create the issue 'Create the GUI'"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            jira_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            jira_agent.id
        )
        await self.runtime.stop_when_idle()

        mock_api_instance.get_project_issues.assert_called_once_with("Ferrari")
        mock_api_instance.create_issue.assert_called_once()

    @unittest.skipIf(SKIP_ORCHESTATOR_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.jira.jira_api.JiraAPI')
    async def test_orchestrate_jira_operations(self, mock_jira_api):
        mock_api_instance = mock_jira_api.return_value
        mock_api_instance.get_project_issues.return_value = [
            {"Key": "FER-1", "Summary": "Design car chassis", "Status": "In Progress"},
            {"Key": "FER-2", "Summary": "Implement engine control system", "Status": "To Do"}
        ]
        mock_api_instance.create_issue.return_value = {
            "id": "10001",
            "key": "FER-3",
            "name": "Create the GUI"
        }
        mock_api_instance.get_all_projects.return_value = [
            {"name": "Ferrari", "key": "FER", "id": "10000"}
        ]

        await JiraAgent.register(self.runtime, "JiraAgent", lambda: JiraAgent(model_client=self.client, jira_api=mock_api_instance))
        jira_agent = AgentProxy(AgentId("JiraAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [jira_agent]

        await LedgerOrchestrator.register(
            self.runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=self.client,
                max_rounds=5,
                max_time=60,
                return_final_answer=True,
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), self.runtime)

        self.runtime.start()

        user_request = "show me all issues for project 'Ferrari' and create the issue 'Create the GUI'. You don't need to check if the issue has been created."
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )
        await self.runtime.stop_when_idle()

        mock_api_instance.get_project_issues.assert_called_once_with("Ferrari")
        mock_api_instance.create_issue.assert_called_once()

if __name__ == "__main__":
    unittest.main()
