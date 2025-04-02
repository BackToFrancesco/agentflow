import asyncio
import json
import logging
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from autogen_core.application import SingleThreadedAgentRuntime
from autogen_core.application.logging import EVENT_LOGGER_NAME
from autogen_core.base import AgentId, AgentProxy
from autogen_core.components.models._types import UserMessage
from autogen_magentic_one.agents.chatgpt.chatgpt_agent import ChatGPTAgent
from autogen_magentic_one.agents.orchestrator import LedgerOrchestrator
from autogen_magentic_one.agents.jira.jira_agent import JiraAgent
from autogen_magentic_one.agents.outlook_calendar.outlook_calendar import OutlookCalendarAgent
from autogen_magentic_one.agents.outlook_mail.outlook_mail import OutlookAgent
from autogen_magentic_one.agents.slack.slack_agent import SlackAgent
from autogen_magentic_one.agents.user_proxy import UserProxy
from autogen_magentic_one.messages import BroadcastMessage, RequestReplyMessage
from autogen_magentic_one.utils import LogHandler, create_completion_client_from_env

# Set up logging
# logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')
logger2 = logging.getLogger(__name__)
logger2.setLevel(logging.CRITICAL)

def calculate_llm_event_tokens(file_path):
    """
    Calculate the total prompt tokens, completion tokens, overall tokens,
    and cost from LLMCallEvent entries in a JSONL file.

    Args:
        file_path (str): Path to the JSONL file.

    Returns:
        dict: A dictionary with total prompt tokens, completion tokens, total tokens, and cost.
    """
    total_prompt_tokens = 0
    total_completion_tokens = 0

    # GPT-4o mini pricing (per 1M tokens)
    input_price = 0.14392  # per 1M input tokens
    output_price = 0.5757  # per 1M output tokens

    try:
        with open(file_path, 'r') as file:
            for line in file:
                try:
                    data = json.loads(line)
                    if data.get("type") == "LLMCallEvent":
                        total_prompt_tokens += data.get("prompt_tokens", 0)
                        total_completion_tokens += data.get("completion_tokens", 0)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

    total_tokens = total_prompt_tokens + total_completion_tokens
    
    # Calculate cost
    input_cost = (total_prompt_tokens / 1_000_000) * input_price
    output_cost = (total_completion_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost

    return {
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens": total_tokens,
        "total_cost": total_cost
    }

def save_execution_info(file_path, tokens_info):
    """
    Save execution information to a JSONL file.

    Args:
        file_path (str): Path to the JSONL file.
        tokens_info (dict): Dictionary containing token and cost information.
    """
    execution_info = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total_prompt_tokens": tokens_info['total_prompt_tokens'],
        "total_completion_tokens": tokens_info['total_completion_tokens'],
        "total_tokens": tokens_info['total_tokens'],
        "total_cost": tokens_info['total_cost']
    }

    with open(file_path, 'a') as file:
        json.dump(execution_info, file)
        file.write('\n')

# Control variables for skipping tests
###################################################################################################################
SKIP_EMAIL_PRIORITIZATION_TEST = True
SKIP_EMAIL_REVIEW_TEST = True
SKIP_EMAIL_FOLDER_AND_JIRA_TEST = False
# multi steps
ENABLE_AGENTS_MULTITURN = True
ENABLE_DOUBLE_CHECK = False
#autoform
ENABLE_AUTOFORM = False
LLM_MODEL = "gpt-4o"
###################################################################################################################
class TestAllAgents(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.logs_dir = "./logs"
        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

        # Set up the main event logger
        self.logger = logging.getLogger(EVENT_LOGGER_NAME)
        self.logger.setLevel(logging.INFO)
        log_handler = LogHandler(filename=os.path.join(self.logs_dir, "log.jsonl"))
        self.logger.handlers = [log_handler]


        self.runtime = SingleThreadedAgentRuntime()
        self.client = create_completion_client_from_env(model=LLM_MODEL)

    async def asyncTearDown(self):
        try:
            await self.runtime.stop_when_idle()
        except Exception as e:
            logger2.error(f"Error stopping runtime: {e}")

    @unittest.skipIf(SKIP_EMAIL_PRIORITIZATION_TEST, "Skipping email prioritization test")
    @patch('autogen_magentic_one.agents.outlook_mail.outlook_mail.OutlookAPI')
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_email_prioritization_and_slack_summary(self, mock_slack_api, mock_outlook_api):
        # Mock Outlook Mail API
        mock_outlook_instance = mock_outlook_api.return_value
        mock_outlook_instance.get_unread_emails.return_value = {"emails": [
            {"id": "1", "subject": "Urgent: Server Down", "from": "sysadmin@example.com", "body": "Our main server is down. Immediate action required."},
            {"id": "2", "subject": "Team Lunch Tomorrow", "from": "hr@example.com", "body": "Join us for a team lunch tomorrow at 12 PM."},
            {"id": "3", "subject": "Quarterly Report Due", "from": "manager@example.com", "body": "Please submit your quarterly report by end of day."},
            {"id": "4", "subject": "New Project Kickoff", "from": "projectmanager@example.com", "body": "We're starting a new project next week. Attendance is mandatory for the kickoff meeting."},
            {"id": "5", "subject": "Office Supplies Order", "from": "supplies@example.com", "body": "We're ordering office supplies. Let me know if you need anything."}
        ]}

        # Mock Slack API
        mock_slack_instance = mock_slack_api.return_value
        mock_slack_instance.send_message.return_value = {"success": True}

        # Register agents
        await OutlookAgent.register(self.runtime, "MailAgent", lambda: OutlookAgent(model_client=self.client, outlook_api=mock_outlook_instance, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client, slack_api=mock_slack_instance, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await ChatGPTAgent.register(self.runtime, "ChatGPT", lambda: ChatGPTAgent(model_client=self.client))
        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await JiraAgent.register(self.runtime, "JiraAgent", lambda: JiraAgent(model_client=self.client, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))

        mail_agent = AgentProxy(AgentId("MailAgent", "default"), self.runtime)
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)
        chatgpt_agent = AgentProxy(AgentId("ChatGPT", "default"), self.runtime)
        calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)
        jira_agent = AgentProxy(AgentId("JiraAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [mail_agent, slack_agent, chatgpt_agent, jira_agent, calendar_agent]

        await LedgerOrchestrator.register(
            self.runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=self.client,
                max_rounds=10,
                max_time=320,
                return_final_answer=False,
                final_check=ENABLE_DOUBLE_CHECK,
                autoform_prompt=ENABLE_AUTOFORM
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), self.runtime)

        self.runtime.start()

        user_request = """
        Retrieve unread emails, categorize each email from a priority of 1 to 5 based on the following level of priority:
        - 1: No action required, purely for awareness (e.g., announcements, automated emails).
        - 2: No immediate action needed, just for reference (e.g., newsletters, non-urgent requests).
        - 3: Important but can wait (e.g., follow-ups, general work updates).
        - 4: Requires action soon but not immediate (e.g., scheduled meetings, important tasks).
        - 5: Needs urgent response or action (e.g., critical issues, deadlines).
        Finally, send in the Slack channel #social only the summary of all the emails with priority >=3.
        """

        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )
        await self.runtime.stop_when_idle()

        # Assert that all expected API calls were made
        mock_outlook_instance.get_unread_emails.assert_called()
        mock_slack_instance.send_message.assert_called()

        # Analyze LLM events
        tokens_info = calculate_llm_event_tokens("./logs/log.jsonl")
        total_prompt_tokens = tokens_info['total_prompt_tokens']
        total_completion_tokens = tokens_info['total_completion_tokens']
        total_tokens = tokens_info['total_tokens']
        total_cost = tokens_info['total_cost']
        print(f"Total prompt tokens: {total_prompt_tokens}")
        print(f"Total completion tokens: {total_completion_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Total cost: ${total_cost:.4f}")

        # Save execution information
        save_execution_info("./logs/execution_info.jsonl", tokens_info)
        
        # You can add assertions here if you want to enforce token usage limits
        # self.assertLess(total_prompt_tokens, 1000, "Prompt tokens exceeded limit")
        # self.assertLess(total_completion_tokens, 500, "Completion tokens exceeded limit")

    @unittest.skipIf(SKIP_EMAIL_REVIEW_TEST, "Skipping email review and Jira task creation test")
    @patch('autogen_magentic_one.agents.outlook_mail.outlook_mail.OutlookAPI')
    @patch('autogen_magentic_one.agents.jira.jira_agent.JiraAPI')
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_email_review_reply_and_jira_task_creation(self, mock_jira_api, mock_outlook_api, slack_api):
        # Mock Outlook Mail API
        mock_outlook_instance = mock_outlook_api.return_value
        mock_outlook_instance.get_unread_emails.return_value = {"emails": [
            {"id": "1", "subject": "Urgent: Client Meeting", "from": "client@example.com", "body": "Can we schedule a meeting ASAP to discuss the project? Best regards, Luca"},
            {"id": "2", "subject": "Weekly Report", "from": "manager@example.com", "body": "Please submit your weekly report by EOD. Best regards, Stefano"},
            {"id": "3", "subject": "Server Maintenance", "from": "it@example.com", "body": "Server maintenance scheduled for tonight. Any concerns? Best regards, Francesco"},
            {"id": "4", "subject": "Office Plant Care", "from": "facilities@example.com", "body": "Remember to water your office plants this week. Best regards, Michele"},
            {"id": "5", "subject": "Company Newsletter", "from": "marketing@example.com", "body": "Check out this month's company newsletter!"},
            {"id": "6", "subject": "Casual Friday Reminder", "from": "hr@example.com", "body": "Don't forget, tomorrow is Casual Friday. Best regards, Carola"}
        ]}
        
        # Mock the reply_to_mail method to return a unique message_id each time it's called
        reply_counter = 0
        def mock_reply_to_mail(*args, **kwargs):
            nonlocal reply_counter
            reply_counter += 1
            res = {"result": "success", "message_id": f"reply_{reply_counter}"}
            return res
        
        mock_outlook_instance.reply_to_mail.side_effect = mock_reply_to_mail
        mock_outlook_instance.send_email = mock_reply_to_mail

        # Mock Jira API
        mock_jira_instance = mock_jira_api.return_value
        jira_counter = 0
        def mock_create_issue(*args, **kwargs):
            nonlocal jira_counter
            jira_counter += 1
            return {"key": f"PROJ-{jira_counter}", "status": "created", "project": "Project A"}
        
        mock_jira_instance.create_issue.side_effect = mock_create_issue
        mock_jira_instance.get_all_projects.return_value = ["Project A"]

        # Register agents
        await OutlookAgent.register(self.runtime, "MailAgent", lambda: OutlookAgent(model_client=self.client, outlook_api=mock_outlook_instance, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await JiraAgent.register(self.runtime, "JiraAgent", lambda: JiraAgent(model_client=self.client, jira_api=mock_jira_instance, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await ChatGPTAgent.register(self.runtime, "ChatGPT", lambda: ChatGPTAgent(model_client=self.client))
        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM, slack_api = slack_api))
        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))

        mail_agent = AgentProxy(AgentId("MailAgent", "default"), self.runtime)
        jira_agent = AgentProxy(AgentId("JiraAgent", "default"), self.runtime)
        chatgpt_agent = AgentProxy(AgentId("ChatGPT", "default"), self.runtime)
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)
        calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [mail_agent, jira_agent, chatgpt_agent, slack_agent, calendar_agent]

        await LedgerOrchestrator.register(
            self.runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=self.client,
                max_rounds=10,
                max_time=320,
                return_final_answer=False,
                final_check=ENABLE_DOUBLE_CHECK,
                autoform_prompt=ENABLE_AUTOFORM
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), self.runtime)

        self.runtime.start()

        user_request = """
            Review my unread emails, identify any that require immediate response, reply to those emails, and create a Jira task for each reply to track follow-ups.
            Emails that requires immediate response are:
            - Emails from clients or supervisors asking for urgent action (e.g., scheduling a meeting, submitting reports).
            - Emails about IT maintenance, security concerns, or system failures requiring immediate attention.
            - Emails mentioning same-day or near-immediate deadlines that impact work progress.
        """

        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )
        await self.runtime.stop_when_idle()

        # Analyze LLM events
        tokens_info = calculate_llm_event_tokens("./logs/log.jsonl")
        total_prompt_tokens = tokens_info['total_prompt_tokens']
        total_completion_tokens = tokens_info['total_completion_tokens']
        total_tokens = tokens_info['total_tokens']
        total_cost = tokens_info['total_cost']
        print(f"Total prompt tokens: {total_prompt_tokens}")
        print(f"Total completion tokens: {total_completion_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Total cost: ${total_cost:.4f}")

        # Save execution information
        save_execution_info("./logs/execution_info.jsonl", tokens_info)

        # Assert that all expected API calls were made
        mock_outlook_instance.get_unread_emails.assert_called()
        
        # Check that reply_to_mail was called (probably 3 times for the important emails)
        assert mock_outlook_instance.reply_to_mail.call_count > 0, "reply_to_mail was not called"
        
        # Check that create_issue was called for each reply
        assert mock_jira_instance.create_issue.call_count == mock_outlook_instance.reply_to_mail.call_count, \
            "Number of Jira issues created doesn't match number of email replies"

    @unittest.skipIf(SKIP_EMAIL_FOLDER_AND_JIRA_TEST, "Skipping email folder management and Jira task creation test")
    @patch('autogen_magentic_one.agents.outlook_mail.outlook_mail.OutlookAPI')
    @patch('autogen_magentic_one.agents.jira.jira_agent.JiraAPI')
    @patch('autogen_magentic_one.agents.slack.slack_agent.SlackAPI')
    async def test_email_folder_management_and_jira_task_creation(self, mock_jira_api, mock_outlook_api, slack_api):
        # Mock Outlook Mail API
        mock_outlook_instance = mock_outlook_api.return_value
        mock_outlook_instance.get_email_folders.return_value = {
            "folders": [
                {"id": "1", "name": "Inbox"},
                {"id": "2", "name": "Sent Items"},
                {"id": "3", "name": "Drafts"}
            ]
        }
        mock_outlook_instance.create_email_folder.return_value = {"folder_id": "4", "name": "Urgent"}
        mock_outlook_instance.get_unread_emails.return_value = {
            "emails": [
                {"id": "101", "subject": "ASAP: Project Update", "from": "manager@example.com"},
                {"id": "102", "subject": "Weekly Report", "from": "team@example.com"},
                {"id": "103", "subject": "ASAP: Client Meeting", "from": "client@example.com"},
                {"id": "104", "subject": "Office Supplies", "from": "admin@example.com"},
                {"id": "105", "subject": "ASAP: Urgent Bug Fix", "from": "dev@example.com"}
            ]
        }
        mock_outlook_instance.move_email_to_folder.side_effect = [
            {"result": "success"},
            {"result": "success"},
            {"result": "success"}
        ]
        mock_outlook_instance.search_emails.return_value = json.dumps([
            {"id": "101", "subject": "ASAP: Project Update", "from": "manager@example.com"},
            {"id": "103", "subject": "ASAP: Client Meeting", "from": "client@example.com"},
            {"id": "105", "subject": "ASAP: Urgent Bug Fix", "from": "dev@example.com"}
        ])

        # Mock Jira API
        mock_jira_instance = mock_jira_api.return_value
        mock_jira_instance.create_issue.return_value = {"key": "PROJ-1", "status": "created"}
        mock_jira_instance.get_all_projects.return_value = ["Project A"]

        # Register agents
        await OutlookAgent.register(self.runtime, "MailAgent", lambda: OutlookAgent(model_client=self.client, outlook_api=mock_outlook_instance, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await JiraAgent.register(self.runtime, "JiraAgent", lambda: JiraAgent(model_client=self.client, jira_api=mock_jira_instance, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))
        await ChatGPTAgent.register(self.runtime, "ChatGPT", lambda: ChatGPTAgent(model_client=self.client))
        await SlackAgent.register(self.runtime, "SlackAgent", lambda: SlackAgent(model_client=self.client, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM, slack_api = slack_api))
        await OutlookCalendarAgent.register(self.runtime, "OutlookCalendarAgent", lambda: OutlookCalendarAgent(model_client=self.client, enable_multiple_turns=ENABLE_AGENTS_MULTITURN, autoform_prompt=ENABLE_AUTOFORM))

        mail_agent = AgentProxy(AgentId("MailAgent", "default"), self.runtime)
        jira_agent = AgentProxy(AgentId("JiraAgent", "default"), self.runtime)
        chatgpt_agent = AgentProxy(AgentId("ChatGPT", "default"), self.runtime)
        slack_agent = AgentProxy(AgentId("SlackAgent", "default"), self.runtime)
        calendar_agent = AgentProxy(AgentId("OutlookCalendarAgent", "default"), self.runtime)

        await UserProxy.register(
            self.runtime,
            "UserProxy",
            lambda: UserProxy(description="The current user interacting with you."),
        )
        user_proxy = AgentProxy(AgentId("UserProxy", "default"), self.runtime)

        agent_list = [mail_agent, jira_agent, chatgpt_agent, slack_agent, calendar_agent]

        await LedgerOrchestrator.register(
            self.runtime,
            "Orchestrator",
            lambda: LedgerOrchestrator(
                agents=agent_list,
                model_client=self.client,
                max_rounds=10,
                max_time=320,
                return_final_answer=False,
                final_check=ENABLE_DOUBLE_CHECK, 
                autoform_prompt=ENABLE_AUTOFORM
            ),
        )
        orchestrator = AgentProxy(AgentId("Orchestrator", "default"), self.runtime)

        self.runtime.start()

        user_request = """
        Get my email folders, create a new folder called 'Urgent', move any unread emails with 'ASAP' in the subject to this folder, and create a Jira task to review these emails.
        """

        await self.runtime.send_message(
            BroadcastMessage(content=UserMessage(content=user_request, source=user_proxy.id.type)),
            orchestrator.id
        )
        await self.runtime.stop_when_idle()

        # Assert that all expected API calls were made
        #mock_outlook_instance.get_email_folders.assert_called_once()
        mock_outlook_instance.create_email_folder.assert_called_once_with("Urgent")
        self.assertEqual(mock_outlook_instance.move_email_to_folder.call_count, 3)  # Three emails with "ASAP" in the subject
        mock_jira_instance.create_issue.assert_called()

        # Analyze LLM events
        tokens_info = calculate_llm_event_tokens("./logs/log.jsonl")
        total_prompt_tokens = tokens_info['total_prompt_tokens']
        total_completion_tokens = tokens_info['total_completion_tokens']
        total_tokens = tokens_info['total_tokens']
        total_cost = tokens_info['total_cost']
        print(f"Total prompt tokens: {total_prompt_tokens}")
        print(f"Total completion tokens: {total_completion_tokens}")
        print(f"Total tokens: {total_tokens}")
        print(f"Total cost: ${total_cost:.4f}")

        # Save execution information
        save_execution_info("./logs/execution_info.jsonl", tokens_info)

if __name__ == "__main__":
    unittest.main()
