"""This example demonstrates the final agentic workflow application with all the agents."""

import asyncio
import logging
import os
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading

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

app = Flask(__name__)
socketio = SocketIO(app)

# Set up logging
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.CRITICAL)

import json

class SocketIOHandler(logging.Handler):
    def emit(self, record):
        record = self.format(record)
        try:
            message_data = json.loads(record)
            print(f"message_data: {message_data}")
            if message_data.get("source") and message_data.get("message") and message_data.get("timestamp"):
                socketio.emit('log_message', json.dumps(message_data))
            else:
                print(f"Message NOT SET: {message_data}")
        except json.JSONDecodeError:
            # If the message is not in JSON format, send it as is
            #socketio.emit('log_message', record)
            print(f"Record not sent: {record}")

async def initialize_runtime():
    runtime = SingleThreadedAgentRuntime()
    client = create_completion_client_from_env(model="gpt-4o-mini")

    # Register agents.
    await OutlookCalendarAgent.register(runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=client))
    await SlackAgent.register(runtime, "SlackAgent", lambda: SlackAgent(model_client=client))
    await OutlookAgent.register(runtime, "OutlookMailAgent", lambda: OutlookAgent(model_client=client))
    await ChatGPTAgent.register(runtime, "ChatGPTAgent", lambda: ChatGPTAgent(model_client=client))
    await JiraAgent.register(runtime, "JiraAgent", lambda: JiraAgent(model_client=client))
    await UserProxy.register(
        runtime,
        "UserProxy",
        lambda: UserProxy(description="The current user interacting with you."),
    )
    user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)

    agent_list = [
        AgentProxy(AgentId("OutlookCalendarAgent", "default"), runtime),
        AgentProxy(AgentId("SlackAgent", "default"), runtime),
        AgentProxy(AgentId("OutlookMailAgent", "default"), runtime),
        AgentProxy(AgentId("ChatGPTAgent", "default"), runtime),
        user_proxy,
        AgentProxy(AgentId("JiraAgent", "default"), runtime)
    ]

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
    return runtime, orchestrator, user_proxy

async def process_message(user_request):
    runtime, orchestrator, user_proxy = await initialize_runtime()
    await runtime.send_message(BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)), orchestrator.id)
    await runtime.stop_when_idle()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def handle_send_message(user_request):
    asyncio.run(process_message(user_request))

if __name__ == "__main__":
    logs_dir = "./logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    
    file_handler = LogHandler(filename=os.path.join(logs_dir, "log.jsonl"))
    socket_handler = SocketIOHandler()
    
    logger.handlers = [file_handler, socket_handler]

    socketio.run(app, debug=True)
