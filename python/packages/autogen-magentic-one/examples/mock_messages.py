import json


MOCKED_MESSAGES = [
  {
    "source": "UserProxy",
    "timestamp": "2025-02-17T10:37:23.413740",
    "message": "Retrive unread emails"
  },
  {
    "source": "Orchestrator (thought)",
    "timestamp": "2025-02-17T10:37:48.467488",
    "message": "Initial plan:\n\nWe are working to address the following user request:\n\nRetrive unread emails\n\nTo answer this request we have assembled the following team:\n\nOutlookCalendarAgent: An agent that can interact with Outlook calendar. SlackAgent: An agent that can interact with Slack. OutlookMailAgent: An agent that can interact with Outlook emails. ChatGPTAgent: A general-purpose AI assistant to be consulted only when specialized agents cannot handle a specific task or when additional analysis is required. UserProxy: The current user interacting with you. JiraAgent: An agent that can interact with Jira.\n\nHere is an initial fact sheet to consider:\n\nGIVEN OR VERIFIED FACTS\n\nThe request is to \"retrive unread emails.\"\nFACTS TO LOOK UP\n\nNone specified in the request itself, but information on how unread emails can be retrieved would typically be found in user guides or help sections of email service providers like Gmail, Outlook, or Yahoo Mail.\nFACTS TO DERIVE\n\nIt needs to be determined what email service is being used, as the method for retrieving unread emails may vary depending on the service.\nEDUCATED GUESSES\n\nThe spelling error \"retrive\" is likely meant to be \"retrieve.\"\nThe user is likely asking for a method to view or list all unread emails in their inbox.\nThe user may be using common email service providers such as Gmail, Outlook, Yahoo Mail, or similar services.\nHere is the plan to follow as best as possible:\n\nIdentify the email service being used by the user. Given the team composition, prioritize checking for unread emails via Outlook.\nUse OutlookMailAgent to retrieve unread emails from the user's Outlook account.\nIf the user is not using Outlook, and further specifics are known, consider consulting ChatGPTAgent for general guidance on how users can retrieve unread emails on other platforms.\nCommunicate any findings or next steps to the UserProxy, providing clear instructions or results accordingly.\nConfirm with the UserProxy if the retrieval meets their needs or if further assistance is required."
  },
  {
    "source": "Orchestrator (update ledger)",
    "timestamp": "2025-02-17T10:37:51.049087",
    "message": "Updated Ledger:\n{ \"is_request_satisfied\": { \"reason\": \"The request to retrieve unread emails has not ye been addressed or fulfilled.\", \"answer\": false }, \"is_in_loop\": { \"reason\": \"We are at the initial stage of processing the user request, thus no looping has occurred.\", \"answer\": false }, \"is_progress_being_made\": { \"reason\": \"We are setting up the next step to retrieve unread emails, aligning with forward progress.\", \"answer\": true }, \"next_speaker\": { \"reason\": \"The request involves accessing unread emails, which falls under the capabilities of the OutlookMailAgent.\", \"answer\": \"OutlookMailAgent\" }, \"instruction_or_question\": { \"reason\": \"The OutlookMailAgent needs to retrieve unread emails from the user's account to satisfy the request.\", \"answer\": \"Please retrieve the user's unread emails from their Outlook account.\" } }"
  },
  {
    "source": "Orchestrator (-> OutlookMailAgent)",
    "timestamp": "2025-02-17T10:37:51.049736",
    "message": "Please retrieve the user's unread emails from their Outlook account."
  },
  {
    "source": "Orchestrator (thought)",
    "timestamp": "2025-02-17T10:37:51.050226",
    "message": "Next speaker OutlookMailAgent"
  },
  {
    "source": "OutlookMailAgent",
    "timestamp": "2025-02-17T10:37:55.372553",
    "message": "I have retrieved the unread emails from your inbox. Below is a list of these emails along with their subject lines and senders:\n\nEmail ID: 101\n\nSubject: ASAP: Project Update\nFrom: manager@example.com\nEmail ID: 102\n\nSubject: Weekly Report\nFrom: team@example.com\nEmail ID: 103\n\nSubject: ASAP: Client Meeting\nFrom: client@example.com\nEmail ID: 104\n\nSubject: Office Supplies\nFrom: admin@example.com\nEmail ID: 105\n\nSubject: ASAP: Urgent Bug Fix\nFrom: dev@example.com\nThere are a total of five unread emails in your inbox."
  },
  {
    "source": "Orchestrator (update ledger)",
    "timestamp": "2025-02-17T10:37:57.845173",
    "message": "Updated Ledger:\n{ \"is_request_satisfied\": { \"reason\": \"The user's request to retrieve unread emails from Outlook has been fulfilled by listing the unread emails.\", \"answer\": true }, \"is_in_loop\": { \"reason\": \"The task was completed successfully without repeating any steps.\", \"answer\": false }, \"is_progress_being_made\": { \"reason\": \"We have provided the user with the list of unread emails, marking the completion of the request.\", \"answer\": true }, \"next_speaker\": { \"reason\": \"Since the request has been satisfied, we need to check if the user has further queries or requires additional assistance.\", \"answer\": \"UserProxy\" }, \"instruction_or_question\": { \"reason\": \"Prompt the user to see if they have any further requests or questions.\", \"answer\": \"Is there anything else you would like to do with your emails or any other assistance you need?\" } }"
  },
  {
    "source": "Orchestrator (final answer)",
    "timestamp": "2025-02-17T10:37:59.368682",
    "message": "I've retrieved your unread emails from your Outlook inbox. Here is a list of them along with their subject lines and senders:\n\nSubject: ASAP: Project Update - From: manager@example.com\nSubject: Weekly Report - From: team@example.com\nSubject: ASAP: Client Meeting - From: client@example.com\nSubject: Office Supplies - From: admin@example.com\nSubject: ASAP: Urgent Bug Fix - From: dev@example.com\nIf there's anything specific you need help with regarding these emails, feel free to let me know!"
  },
  {
    "source": "Orchestrator",
    "timestamp": "2025-02-17T10:37:59.368972",
    "message": "Request satisfied."
  },
  {
    "source": "Orchestrator (termination condition)",
    "timestamp": "2025-02-17T10:37:59.369344",
    "message": "No agent selected."
  }
]

MOCKED_GET_EMAIL_FOLDERS = {
    "folders": [
        {"id": "1", "name": "Inbox"},
        {"id": "2", "name": "Sent Items"},
        {"id": "3", "name": "Drafts"}
    ]
}

MOCKED_CREATE_EMAIL_FOLDER = {"folder_id": "4", "name": "Urgent"}

MOCKED_GET_EMAILS = {
    "emails": [
        {
            "id": "101",
            "subject": "ASAP: Project Update",
            "from": "manager@example.com",
            "body": "Hi Team,\n\nWe need an urgent update on the current progress of the new feature implementation. Please provide a summary of completed tasks and any blockers by end of the day.\n\nThanks,\nManager"
        },
        {
            "id": "102",
            "subject": "Weekly Report",
            "from": "team@example.com",
            "body": "Hello,\n\nPlease find attached the weekly report detailing the team's performance metrics, completed tasks, and pending action items. Let us know if there are any questions.\n\nBest,\nTeam"
        },
        {
            "id": "103",
            "subject": "ASAP: Client Meeting",
            "from": "client@example.com",
            "body": "Dear Team,\n\nWe need to schedule a meeting as soon as possible to discuss the upcoming project deadlines and requirements. Please provide your availability for tomorrow.\n\nBest,\nClient"
        },
        {
            "id": "104",
            "subject": "Office Supplies",
            "from": "admin@example.com",
            "body": "Hello,\n\nWe are running low on some office supplies. Please review the attached list and let us know if any additional items are needed before we place the order.\n\nThanks,\nAdmin"
        },
        {
            "id": "105",
            "subject": "ASAP: Urgent Bug Fix",
            "from": "dev@example.com",
            "body": "Hey Team,\n\nWe've identified a critical bug in the production system that needs immediate attention. The issue is affecting user authentication. Please review the logs and deploy a fix as soon as possible.\n\nThanks,\nDeveloper"
        }
    ]
}

MOCKED_MOVE_EMAIL_TO_FOLDER = {"result": "success"}

MOCKED_SEARCH_EMAILS = json.dumps([
    {"id": "101", "subject": "ASAP: Project Update", "from": "manager@example.com"},
    {"id": "103", "subject": "ASAP: Client Meeting", "from": "client@example.com"},
    {"id": "105", "subject": "ASAP: Urgent Bug Fix", "from": "dev@example.com"}
])

MOCKED_CREATE_ISSUE = {"key": "PROJ-1", "status": "created"}

MOCKED_GET_ALL_PROJECTS = ["Project A"]

MOCKED_CALENDAR_EVENTS = {
  "events": [
      {
          "id": "1",
          "subject": "Team Meeting",
          "start": "2025-03-01T10:00:00Z",
          "end": "2025-03-01T11:00:00Z",
          "attendees": ["john@example.com", "jane@example.com"]
      },
      {
          "id": "2",
          "subject": "Project Review",
          "start": "2025-03-02T14:00:00Z",
          "end": "2025-03-02T15:30:00Z",
          "attendees": ["manager@example.com", "team@example.com"]
      }
  ]
}

MOCKED_CREATE_MEETING = {
    "status": "success"
}

MOCKED_GET_AVAILABLE_SLOTS = {
  "available_slots": [
      {"start": "2025-02-28T10:00:00Z", "end": "2025-03-04T11:00:00Z"},
      {"start": "2025-02-28T14:00:00Z", "end": "2025-03-04T15:00:00Z"},
      {"start": "2025-02-28T09:00:00Z", "end": "2025-03-05T10:00:00Z"},
      {"start": "2025-02-28T016:00:00Z", "end": "2025-03-05T17:00:00Z"}
  ]
}

MOCKED_SEND_MESSAGE = {"result": "success"}

MOCKED_GET_CHANNEL_MESSAGES = {
    "messages": [
        {"id": "1", "text": "Hello channel", "sender": "user1"},
        {"id": "2", "text": "Welcome everyone", "sender": "user2"}
    ]
}

MOCKED_SEND_PRIVATE_MESSAGE = {"result": "success"}

MOCKED_GET_UNREAD_MESSAGES = {
    "unread_messages": [
        {"id": "1", "text": "Hello", "sender": "user1"},
        {"id": "2", "text": "How are you?", "sender": "user2"}
    ]
}

MOCKED_LIST_CHANNELS = {
    "channels": [
        {"id": "C1", "name": "general"},
        {"id": "C2", "name": "random"}
    ]
}
