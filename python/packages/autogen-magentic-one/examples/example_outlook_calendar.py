"""This example demonstrates the Outlook calendar agent performing calendar-related tasks."""

import asyncio
import logging
import os

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.models._types import UserMessage
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.outlook_calendar.outlook_calendar import OutlookCalendarAgent
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env


async def main() -> None:
    logs_dir = "./logs"
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model="gpt-4o")

    # Register agents.
    await OutlookCalendarAgent.register(runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=client))
    outlook_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), runtime)

    await UserProxy.register(
        runtime,
        "UserProxy",
        lambda: UserProxy(description="The current user interacting with you."),
    )
    user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    agent_list = [outlook_agent, user_proxy]

    await LedgerOrchestrator.register(
        runtime,
        "Orchestrator",
        lambda: LedgerOrchestrator(
            agents=agent_list,
            model_client=client,
            max_rounds=30,
            max_time=25 * 60,
            return_final_answer=True,
        ),
    )
    orchestrator = AgentProxy(AgentId("Orchestrator", "default"), runtime)

    runtime.start()

    # Simulate user request
    #user_request = "Create a meeting for the 12th of December 2025 at 10 am, the meeting have to be of 3 hours."
    user_request = "Find an available spot of 1 hour between 8 to 12 the 15th January 2025 and create a meeting"

    await runtime.send_message(BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)), orchestrator.id)

    await runtime.stop_when_idle()


if __name__ == "__main__":
    logs_dir = "./logs"

    # Ensure the log directory exists
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    log_handler = LogHandler(filename=os.path.join(logs_dir, "log.jsonl"))
    logger.handlers = [log_handler]
    asyncio.run(main())