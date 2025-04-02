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
from autogen_magentic_one.agents.outlook_calendar.outlook_calendar import OutlookCalendarAgent
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

class TestOutlookCalendar(unittest.IsolatedAsyncioTestCase):
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
    @patch('autogen_magentic_one.agents.outlook_calendar.outlook_calendar.OutlookCalendarAPI')
    async def test_get_calendar_events(self, mock_outlook_calendar_api):
        mock_api_instance = mock_outlook_calendar_api.return_value
        mock_api_instance.get_calendar_events.return_value = [
            {"id": "1", "subject": "Team Meeting", "start": {"dateTime": "2023-06-01T10:00:00"}, "end": {"dateTime": "2023-06-01T11:00:00"}}
        ]

        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client))
        outlook_calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "Get my calendar events for today"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            outlook_calendar_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            outlook_calendar_agent.id
        )

        mock_api_instance.get_calendar_events.assert_called_once()

    @unittest.skipIf(SKIP_ORCHESTATOR_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.outlook_calendar.outlook_calendar.OutlookCalendarAPI')
    async def test_orchestrate_get_calendar_events(self, mock_outlook_calendar_api):
        mock_api_instance = mock_outlook_calendar_api.return_value
        mock_api_instance.get_calendar_events.return_value = [
            {"id": "1", "subject": "Team Meeting", "start": {"dateTime": "2023-06-01T10:00:00"}, "end": {"dateTime": "2023-06-01T11:00:00"}}
        ]
        mock_api_instance.create_meeting.return_value = {
            "id": "1",
            "subject": "Test Meeting",
            "start": {"dateTime": "2023-06-02T14:00:00"},
            "end": {"dateTime": "2023-06-02T15:00:00"},
            "attendees": ["colleague1@example.com", "colleague2@example.com"],
            "location": "Conference Room A",
            "webLink": "https://teams.microsoft.com/l/meetup-join/..."
        }

        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client))
        outlook_calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [outlook_calendar_agent]

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

        user_request = "Get my calendar events for 1st June 2023 and then schedule one for the next day from 3 to 4 pm called 'Test Meeting'."
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )
        await self.runtime.stop_when_idle()

        mock_api_instance.get_calendar_events.assert_called_once()
        mock_api_instance.create_meeting.assert_called_once()

    @unittest.skipIf(SKIP_AGENTS_TESTS, "Test is skipped")
    @patch('autogen_magentic_one.agents.outlook_calendar.outlook_calendar.OutlookCalendarAPI')
    async def test_create_meeting(self, mock_outlook_calendar_api):
        mock_api_instance = mock_outlook_calendar_api.return_value
        mock_api_instance.create_meeting.return_value = {
            "id": "1",
            "subject": "Test Meeting",
            "start": {"dateTime": "2023-06-02T14:00:00"},
            "end": {"dateTime": "2023-06-02T15:00:00"},
            "attendees": ["colleague1@example.com", "colleague2@example.com"],
            "location": "Conference Room A",
            "webLink": "https://teams.microsoft.com/l/meetup-join/..."
        }

        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client))
        outlook_calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        self.runtime.start()

        user_request = "Create a new team meeting for 1st June 2023 at 2 PM for 1 hour"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            outlook_calendar_agent.id
        )
        await self.runtime.send_message(
            RequestReplyMessage(),
            outlook_calendar_agent.id
        )

        mock_api_instance.create_meeting.assert_called_once()

    @unittest.skipIf(False, "Test is skipped")
    @patch('autogen_magentic_one.agents.outlook_calendar.outlook_calendar.OutlookCalendarAPI')
    async def test_find_slot_and_create_meeting(self, mock_outlook_calendar_api):
        mock_api_instance = mock_outlook_calendar_api.return_value
        mock_api_instance.get_available_slots.return_value = {
            "available_slots": [
                {"start": "2023-06-02T14:00:00", "end": "2023-06-02T15:00:00"},
                {"start": "2023-06-02T16:00:00", "end": "2023-06-02T17:00:00"}
            ]
        }
        mock_api_instance.create_meeting.return_value = {
            "id": "1",
            "subject": "Team Discussion",
            "start": {"dateTime": "2023-06-02T14:00:00"},
            "end": {"dateTime": "2023-06-02T15:00:00"},
            "attendees": ["colleague1@example.com", "colleague2@example.com"],
            "location": "Conference Room B",
            "webLink": "https://teams.microsoft.com/l/meetup-join/..."
        }

        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client))
        outlook_calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [outlook_calendar_agent]

        await LedgerOrchestrator.register(
            self.runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=self.client,
                max_rounds=5,
                max_time=120,
                return_final_answer=True,
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), self.runtime)

        self.runtime.start()

        user_request = "Find an available slot for tomorrow and schedule a team discussion for 1 hour"
        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )

        await self.runtime.stop_when_idle()

        mock_api_instance.get_available_slots.assert_called_once()
        mock_api_instance.create_meeting.assert_called_once()

if __name__ == "__main__":
    unittest.main()
