"""This example demonstrates the final agentic workflow application with all the agents and the GUI."""

import asyncio
import logging
import os
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import threading
import json
from unittest.mock import MagicMock
from queue import Queue

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
from mock_messages import MOCKED_CALENDAR_EVENTS, MOCKED_CREATE_EMAIL_FOLDER, MOCKED_CREATE_ISSUE, MOCKED_CREATE_MEETING, MOCKED_GET_ALL_PROJECTS, MOCKED_GET_AVAILABLE_SLOTS, MOCKED_GET_EMAIL_FOLDERS, MOCKED_GET_EMAILS, MOCKED_MESSAGES, MOCKED_MOVE_EMAIL_TO_FOLDER, MOCKED_SEARCH_EMAILS, MOCKED_SEND_MESSAGE, MOCKED_GET_CHANNEL_MESSAGES, MOCKED_SEND_PRIVATE_MESSAGE, MOCKED_GET_UNREAD_MESSAGES, MOCKED_LIST_CHANNELS

# Debug constant
DEBUG = True # Put true to use mocked APIs for the servicies
UI_DEBUG_MODE = False # Put true to use mock messages in the chat

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

runtime = None
orchestrator = None
user_proxy = None
message_queue = Queue()
processing_task = None
user_input_needed_event = asyncio.Event()

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
            print(f"Record not sent: {record}")

# Mock API calls
mock_outlook_api = MagicMock()
mock_outlook_api.get_email_folders.return_value = MOCKED_GET_EMAIL_FOLDERS
mock_outlook_api.create_email_folder.return_value = MOCKED_CREATE_EMAIL_FOLDER
mock_outlook_api.get_unread_emails.return_value = MOCKED_GET_EMAILS

mock_outlook_api.move_email_to_folder.return_value = MOCKED_MOVE_EMAIL_TO_FOLDER
mock_outlook_api.search_emails.return_value = MOCKED_SEARCH_EMAILS

mock_jira_api = MagicMock()
mock_jira_api.create_issue.return_value = MOCKED_CREATE_ISSUE
mock_jira_api.get_all_projects.return_value = MOCKED_GET_ALL_PROJECTS

# Mock Outlook Calendar API
mock_outlook_calendar_api = MagicMock()
mock_outlook_calendar_api.get_calendar_events.return_value = MOCKED_CALENDAR_EVENTS
mock_outlook_calendar_api.create_meeting.return_value = MOCKED_CREATE_MEETING
mock_outlook_calendar_api.get_available_slots.return_value = MOCKED_GET_AVAILABLE_SLOTS

# Mock Slack API
mock_slack_api = MagicMock()
mock_slack_api.send_message.return_value = MOCKED_SEND_MESSAGE
mock_slack_api.send_private_message.return_value = MOCKED_SEND_PRIVATE_MESSAGE
mock_slack_api.get_unread_messages.return_value = MOCKED_GET_UNREAD_MESSAGES
mock_slack_api.list_channels.return_value = MOCKED_LIST_CHANNELS
mock_slack_api.get_channel_messages.return_value = MOCKED_GET_CHANNEL_MESSAGES

async def initialize_runtime():
    global runtime, orchestrator, user_proxy, user_input_needed_event, user_proxy_instance, message_queue
    if runtime is None:
        print("RUNTIME INITIALIZED")
        runtime = SingleThreadedAgentRuntime()
        client = create_completion_client_from_env(model="gpt-4o")
        # Register agents with mocked APIs
        await OutlookCalendarAgent.register(runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=client, outlook_calendar_api=mock_outlook_calendar_api, enable_multiple_turns=True, autoform_prompt=autoform_setting))
        await SlackAgent.register(runtime, "SlackAgent", lambda: SlackAgent(model_client=client, slack_api=mock_slack_api, enable_multiple_turns=enable_multiple_turns_setting, autoform_prompt=autoform_setting))
        await OutlookAgent.register(runtime, "OutlookMailAgent", lambda: OutlookAgent(model_client=client, outlook_api=mock_outlook_api, enable_multiple_turns=enable_multiple_turns_setting, autoform_prompt=autoform_setting))
        await ChatGPTAgent.register(runtime, "ChatGPTAgent", lambda: ChatGPTAgent(model_client=client))
        await JiraAgent.register(runtime, "JiraAgent", lambda: JiraAgent(model_client=client, jira_api=mock_jira_api, enable_multiple_turns=enable_multiple_turns_setting, autoform_prompt=autoform_setting))

        input_event = asyncio.Event()
        await UserProxy.register(
            runtime,
            "UserProxy",
            lambda: UserProxy(
                description="The current user interacting with you.",
                message_queue=message_queue,
                input_event=input_event,
                user_input_needed_event=user_input_needed_event
            ),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), runtime)
        user_proxy_instance = await runtime._get_agent(user_proxy._agent)
        agent_list = [
            AgentProxy(AgentId("OutlookCalendarAgent", "default"), runtime),
            AgentProxy(AgentId("SlackAgent", "default"), runtime),
            AgentProxy(AgentId("OutlookMailAgent", "default"), runtime),
            AgentProxy(AgentId("ChatGPTAgent", "default"), runtime),
            #user_proxy,
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
                infinite_conversation=infinite_conversation_setting,
                autoform_prompt=autoform_setting
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), runtime)

        runtime.start()

async def message_processor():
    global runtime, orchestrator, user_proxy, user_input_needed_event, first_message, message_queue
    print("Starting message processor")
    if not UI_DEBUG_MODE:
        await initialize_runtime()
        print("Runtime initialized")
    else:                                                                                                                                                                              
        for message in MOCKED_MESSAGES:
            socketio.emit('log_message', json.dumps(message))
            await asyncio.sleep(3)  # Add a delay between messages for a more realistic feel
        return
    while True:
        if first_message:
            print(f"Waiting for message. Queue size: {message_queue.qsize()}")
            user_request = await asyncio.get_event_loop().run_in_executor(None, message_queue.get)
            print(f"Received message: {user_request}")

        try:
            
            if first_message:
                print("Sending first message to runtime")
                await runtime.send_message(BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)), orchestrator.id)
                first_message = False
            print("Message sent to runtime")
            
            # Wait for user input if needed
            print("Waiting for user input event")
            await user_input_needed_event.wait()
            print("User input event received")
            user_input_needed_event.clear()
            print("User input event cleared")
            
        except Exception as e:
            print(f"Error processing message: {e}")
            socketio.emit('error', {'message': str(e)})

def start_message_processor():
    asyncio.run(message_processor())

@app.route('/')
def index():
    return render_template('index.html', debug=DEBUG)

@app.route('/debug')
def debug_status():
    return jsonify({"debug": DEBUG})

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('initialize')
def handle_initialize():
    global processing_task, first_message
    if processing_task is None:
        processing_task = threading.Thread(target=start_message_processor)
        processing_task.start()
        first_message = True
    print("Client initialized")

infinite_conversation_setting = False
enable_multiple_turns_setting = False
autoform_setting = False

@socketio.on('set_infinite_conversation')
def handle_set_infinite_conversation(infinite_conversation):
    global infinite_conversation_setting
    infinite_conversation_setting = infinite_conversation
    print(f"Infinite conversation set to: {infinite_conversation_setting}")

@socketio.on('set_enable_multiple_turns')
def handle_set_enable_multiple_turns(enable_multiple_turns):
    global enable_multiple_turns_setting
    enable_multiple_turns_setting = enable_multiple_turns
    print(f"Enable multiple turns set to: {enable_multiple_turns_setting}")

@socketio.on('set_autoform')
def handle_set_autoform(autoform):
    global autoform_setting
    autoform_setting = autoform
    print(f"Autoform set to: {autoform_setting}")

@socketio.on('create_new_conversation')
def handle_create_new_conversation(data):
    global runtime, orchestrator, user_proxy, processing_task, message_queue, user_input_needed_event, infinite_conversation_setting, enable_multiple_turns_setting, autoform_setting
    print(f"New conversation created, runtime reset. Infinite conversation: {data['infinite_conversation']}, Enable multiple turns: {data['enable_multiple_turns']}, Autoform: {data['autoform']}")
    infinite_conversation_setting = data['infinite_conversation']
    enable_multiple_turns_setting = data['enable_multiple_turns']
    autoform_setting = data['autoform']
    
    if runtime:
        runtime.stop()

    if processing_task:
        processing_task.join(timeout=1)
        processing_task = None
    
    runtime = None
    orchestrator = None
    user_proxy = None

    message_queue = Queue()
    user_input_needed_event = asyncio.Event()

    handle_initialize()
    print("System reinitialized")

@socketio.on('user_input')
def handle_user_input(user_input):
    global user_proxy, user_proxy_instance, message_queue
    print(f"Received user input: {user_input}")
    if not UI_DEBUG_MODE:
        message_queue.put(user_input)
        print(f"Message queue size after put: {message_queue.qsize()}")
        if isinstance(user_proxy, AgentProxy):
            user_proxy_agent = user_proxy._agent
            if isinstance(user_proxy_instance, UserProxy) and user_proxy_instance.input_event:
                user_proxy_instance.input_event.set()  # Signal that user input is available
                print("User input event set")
            else:
                print(f"Error: user_proxy_agent ({type(user_proxy_instance)}) is not a UserProxy instance or doesn't have an input_event")
        else:
            print("Error: user_proxy is not an AgentProxy instance")
    else:
        # In debug mode, just echo the user input
         socketio.emit('log_message', json.dumps({
             "source": "UserProxy",
             "timestamp": "NOW",
             "message": user_input
         }))

@socketio.on('send_message')
def handle_send_message(user_request):
    global message_queue
    print(f"Received send_message: {user_request}")
    message_queue.put(user_request)
    print(f"Message queue size after put: {message_queue.qsize()}")

if __name__ == "__main__":
    logs_dir = "./logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logger = logging.getLogger(EVENT_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    
    file_handler = LogHandler(filename=os.path.join(logs_dir, "log.jsonl"))
    socket_handler = SocketIOHandler()
    
    logger.handlers = [file_handler, socket_handler]

    print("Starting Server..")

    socketio.run(app, debug=True)
