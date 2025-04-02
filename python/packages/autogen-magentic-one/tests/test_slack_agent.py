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
from autogen_magentic_one.agents.slack.slack_agent import SlackAgent
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env

# Set this to True if you want to skip the tests
SKIP_ORCHESTATOR_TESTS = True
SKIP_AGENTS_TESTS = True

# Set up logging
logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.CRITICAL)

class TestSlackAgent(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.logs_dir = "./logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        self.logger = logging.getLogger(EVENT_LOGGER_NAME)
        self.logger.setLevel(logging.INFO)
        log_handler = LogHandler(filename=os.path.join(self.logs_dir, "log.jsonl"))
        self.logger.handlers = [log_handler]

        self.runtime = SingleThreadedAgentRuntime()
        self.client = create_completion_client_from_env(model="gpt-4o")

    async def asyncTearDown(self):
        try:
            await self.runtime.stop_when_idle()
        except Exception as e:
            logger2.error(f"Error stopping runtime: {e}")

    @unittest.skipIf(SKIP_AGENTS_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_send_message(self, mock_slack_api):
        mock_api_instance = mock_slack_api.return_value
        mock_api_instance.send_message.return_value = {"success": True}

        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client))
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "Send a message to the #general channel saying 'Hello, team!'"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            slack_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            slack_agent.id
        )

        mock_api_instance.send_message.assert_called_once_with("general", "Hello, team!", False)

    @unittest.skipIf(SKIP_AGENTS_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_send_private_message(self, mock_slack_api):
        mock_api_instance = mock_slack_api.return_value
        mock_api_instance.send_private_message.return_value = {"success": True}

        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client))
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "Send a private message to user U123456 saying 'Hi there!'"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            slack_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            slack_agent.id
        )

        mock_api_instance.send_private_message.assert_called_once_with("U123456", "Hi there!", False)

    @unittest.skipIf(SKIP_AGENTS_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_get_unread_messages(self, mock_slack_api):
        mock_api_instance = mock_slack_api.return_value
        mock_api_instance.get_unread_messages.return_value = {
            "unread_messages": [
                {"text": "Hello", "sender": "John Doe"},
                {"text": "How are you?", "sender": "Jane Smith"}
            ]
        }

        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client))
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "Get unread messages from the #general channel"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            slack_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            slack_agent.id
        )

        mock_api_instance.get_unread_messages.assert_called_once_with("general", False)

    @unittest.skipIf(False, "Test is skipped")
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_orchestrate_slack_operations(self, mock_slack_api):
        mock_api_instance = mock_slack_api.return_value
        mock_api_instance.send_message.return_value = {"success": True}
        mock_api_instance.get_unread_messages.return_value = {
            "unread_messages": [
                {"text": "Meeting at 3 PM", "sender": "John Doe"},
                {"text": "Don't forget to submit your report", "sender": "Jane Smith"}
            ]
        }

        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client))
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [slack_agent]

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

        user_request = "Check for unread messages in #general, then send a summary to #team-updates"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )

        await self.runtime.stop_when_idle()

        mock_api_instance.get_unread_messages.assert_called_once_with("general", False)
        mock_api_instance.send_message.assert_called_once()  # You might want to check the exact arguments here

if __name__ == "__main__":
    unittest.main()
