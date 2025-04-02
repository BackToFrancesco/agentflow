"""This example demonstrates the final agentic workflow application with all the agents. It uses the command line."""

import asyncio
import logging
import os

from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.models._types import UserMessage
from autogen_magentic_one.agents.chatgpt.chatgpt_agent import ChatGPTAgent
from autogen_magentic_one.agents.jira.jira_agent import JiraAgent
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.outlook_calendar.outlook_calendar import OutlookCalendarAgent
from autogen_magentic_one.agents.outlook_mail.outlook_mail import OutlookAgent
from autogen_magentic_one.agents.slack.slack_agent import SlackAgent
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env

# Set up logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger2 = logging.getLogger(__name__)
# logger2.setLevel(logging.INFO)

async def main() -> None:
    logs_dir = "./logs"
    # Create the runtime.
    runtime = SingleThreadedAgentRuntime()

    # Create an appropriate client
    client = create_completion_client_from_env(model="gpt-4o-mini")

    # Register agents.
    await OutlookCalendarAgent.register(runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=client))
    calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), runtime)

    await SlackAgent.register(runtime, "SlackAgent", lambda: SlackAgent(model_client=client))
    slack_agent = AgentProxy(AgentId("SlackAgent", "default"), runtime)

    await OutlookAgent.register(runtime, "OutlookMailAgent", lambda: OutlookAgent(model_client=client))
    mail_agent = AgentProxy(AgentId("OutlookMailAgent", "default"), runtime)

    await ChatGPTAgent.register(runtime, "ChatGPTAgent", lambda: ChatGPTAgent(model_client=client))
    chatgpt_agent = AgentProxy(AgentId("ChatGPTAgent", "default"), runtime)

    await JiraAgent.register(runtime, "JiraAgent", lambda: JiraAgent(model_client=client))
    jira_agent = AgentProxy(AgentId("JiraAgent", "default"), runtime)

    await UserProxy.register(
        runtime,
        "UserProxy",
        lambda: UserProxy(description="The current user interacting with you."),
    )
    user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    agent_list = [calendar_agent, slack_agent, mail_agent, chatgpt_agent, user_proxy, jira_agent]

    await LedgerOrchestrator.register(
        runtime,
        "Orchestrator",
        lambda: LedgerOrchestrator(
            agents=agent_list,
            model_client=client,
            max_rounds=30,
            max_time=25 * 60,
            return_final_answer=True,
            infinite_conversation=True
        ),
    )
    orchestrator = AgentProxy(AgentId("Orchestrator", "default"), runtime)

    runtime.start()

    # Simulate user request
    user_request = """
    Retrive unread email, for each email categorized it from a priority of 1 to 5, and then send me a message in the Slack channel #social with the summary of all the mails with priority >=3
    """

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