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
from autogen_magentic_one.agents.outlook_mail.outlook_mail import OutlookAgent
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env

# Set this to True if you want to skip the tests
SKIP_ORCHESTATOR_TESTS = True
SKIP_AGENTS_TESTS = True

# Set up logging
# logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.CRITICAL)

class TestOutlookMail(unittest.IsolatedAsyncioTestCase):
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
    @patch('autogen_magentic_one.agents.outlook_mail.outlook_mail.OutlookAPI')
    async def test_retrieve_unread_emails(self, mock_outlook_api):
        mock_api_instance = mock_outlook_api.return_value
        mock_api_instance.get_unread_emails.return_value = [
            {"id": "1", "subject": "Test Email", "from": "sender@example.com"}
        ]

        await OutlookAgent.register(self.runtime, "OutlookAgent", lambda: OutlookAgent(model_client=self.client))
        outlook_agent = AgentProxy(AgentId("OutlookAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "Retrieve all unread outlook emails"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            outlook_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            outlook_agent.id
        )

        mock_api_instance.get_unread_emails.assert_called_once()

    @unittest.skipIf(True, "Test is skipped")
    @patch('autogen_magentic_one.agents.outlook_mail.outlook_mail.OutlookAPI')
    async def test_orchestrate_retrieve_unread_emails(self, mock_outlook_api):
        mock_api_instance = mock_outlook_api.return_value
        mock_api_instance.get_unread_emails.return_value = {"emails": [
            {"id": "1", "subject": "Urgent: Server Down", "from": "sysadmin@example.com", "body": "Our main server is down. Immediate action required."},
            {"id": "2", "subject": "Team Lunch Tomorrow", "from": "hr@example.com", "body": "Join us for a team lunch tomorrow at 12 PM."},
            {"id": "3", "subject": "Quarterly Report Due", "from": "manager@example.com", "body": "Please submit your quarterly report by end of day."},
            {"id": "4", "subject": "New Project Kickoff", "from": "projectmanager@example.com", "body": "We're starting a new project next week. Attendance is mandatory for the kickoff meeting."},
            {"id": "5", "subject": "Office Supplies Order", "from": "supplies@example.com", "body": "We're ordering office supplies. Let me know if you need anything."}
        ]}

        await OutlookAgent.register(self.runtime, "OutlookAgent", lambda: OutlookAgent(model_client=self.client, enable_multiple_turns=True))
        outlook_agent = AgentProxy(AgentId("OutlookAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [outlook_agent]

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

        user_request = "Ask to the MailAgent to get and then summarize the unread email, ask this in one message"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )

        mock_api_instance.get_unread_emails.assert_called_once()

    @unittest.skipIf(False, "Test is skipped")
    @patch('autogen_magentic_one.agents.outlook_mail.outlook_mail.OutlookAPI')
    async def test_orchestrate_move_unread_emails(self, mock_outlook_api):
        
        mock_api_instance = mock_outlook_api.return_value
        mock_api_instance.get_unread_emails.return_value = {"emails": [
            {"id": "1", "subject": "Team Lunch Tomorrow", "from": "hr@example.com", "body": "Join us for a team lunch tomorrow at 12 PM."},
            {"id": "2", "subject": "Quarterly Report Due", "from": "manager@example.com", "body": "Please submit your quarterly report by end of day."},
            {"id": "3", "subject": "Office Supplies Order", "from": "supplies@example.com", "body": "We're ordering office supplies. Let me know if you need anything."}
        ]}
        mock_api_instance.create_email_folder.return_value = {"folder_id": "folder_1", "displayName": "unread email"}
        mock_api_instance.move_email_to_folder.side_effect = [
            {"id": "1", "status": "success"},
            {"id": "2", "status": "success"},
            {"id": "3", "status": "success"}
        ]

        await OutlookAgent.register(self.runtime, "OutlookAgent", lambda: OutlookAgent(model_client=self.client, enable_multiple_turns=True))
        outlook_agent = AgentProxy(AgentId("OutlookAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [outlook_agent]

        await LedgerOrchestrator.register(
            self.runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=self.client,
                max_rounds=10,
                max_time=180,
                return_final_answer=True,
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), self.runtime)

        self.runtime.start()

        user_request = "Move the unread Outlook emails to a new created folder called 'unread email'"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )
        await self.runtime.stop_when_idle()

        print(f"get_unread_emails call count: {mock_api_instance.get_unread_emails.call_count}")                                              
        print(f"get_unread_emails calls: {mock_api_instance.get_unread_emails.mock_calls}")
        print(f"create_email_folder call count: {mock_api_instance.create_email_folder.call_count}")
        print(f"create_email_folder calls: {mock_api_instance.create_email_folder.mock_calls}")
        print(f"move_email_to_folder call count: {mock_api_instance.move_email_to_folder.call_count}")
        print(f"move_email_to_folder calls: {mock_api_instance.move_email_to_folder.mock_calls}")

        mock_api_instance.get_unread_emails.assert_called()                                                                                                                                    
        mock_api_instance.create_email_folder.assert_called()                                                                                                                                  
        mock_api_instance.move_email_to_folder.assert_called()

if __name__ == "__main__":
    unittest.main()
