from autogen_core.components.tools._base import ParametersSchema, ToolSchema

TOOL_RETRIEVE_UNREAD_EMAILS = ToolSchema(
    name="get_unread_emails",
    description="Retrieve unread emails from the Outlook inbox.",
    parameters=ParametersSchema(
        type="object",
        properties={},
        required=[],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "emails": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "sender": {"type": "object"},
                        "toRecipients": {"type": "array"},
                        "subject": {"type": "string"},
                        "bodyPreview": {"type": "string"}
                    }
                },
                "description": "A list of unread email objects, each containing email details."
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation."
            }
        },
        description="Either a list of unread emails or an error message if the operation failed."
    )
)

TOOL_GET_ALL_EMAILS = ToolSchema(
    name="get_all_emails",
    description="Retrieve all emails from the Outlook inbox with optional filtering and limit.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "filter_params": {
                "type": "string",
                "description": """OData filter query string to filter emails. Supports logical operators (and, or, not), 
                comparison operators (eq, ne, gt, ge, lt, le), and string functions. Examples:
                - "from/emailAddress/address eq 'sender@example.com'"
                - "subject eq 'Meeting Notes'"
                - "receivedDateTime ge 2024-01-01T00:00:00Z"
                - "hasAttachments eq true"
                - "importance eq 'high'"
                Leave empty to retrieve all emails without filtering.""",
            },
            "limit": {
                "type": "integer",
                "description": "Optional limit on the number of emails to retrieve.",
            },
        },
        required=[],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "emails": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "sender": {"type": "object"},
                        "toRecipients": {"type": "array"},
                        "subject": {"type": "string"},
                        "bodyPreview": {"type": "string"}
                    }
                },
                "description": "A list of email objects, each containing email details."
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation."
            }
        },
        description="Either a list of emails or an error message if the operation failed."
    )
)

TOOL_MOVE_EMAIL_TO_FOLDER = ToolSchema(
    name="move_email_to_folder",
    description="Move an email to a specified folder.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "email_id": {
                "type": "string",
                "description": "The ID of the email to move.",
            },
            "folder_id": {
                "type": "string",
                "description": "The ID of the destination folder.",
            },
        },
        required=["email_id", "folder_id"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "success": {
                "type": "boolean",
                "description": "Indicates whether the operation was successful."
            },
            "error": {
                "type": "string",
                "description": "Error message if the operation failed."
            }
        },
        description="The result of the move operation."
    )
)

TOOL_GET_EMAIL_FOLDERS = ToolSchema(
    name="get_email_folders",
    description="Retrieve all email folders in the Outlook account.",
    parameters=ParametersSchema(
        type="object",
        properties={},
        required=[],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "folders": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "displayName": {"type": "string"}
                    }
                },
                "description": "A list of folder objects, each containing folder details."
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation."
            }
        },
        description="Either a list of email folders or an error message if the operation failed."
    )
)

TOOL_CREATE_EMAIL_FOLDER = ToolSchema(
    name="create_email_folder",
    description="Create a new email folder in the Outlook account.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "folder_name": {
                "type": "string",
                "description": "The name of the new folder to create.",
            },
        },
        required=["folder_name"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "success": {
                "type": "boolean",
                "description": "Indicates whether the operation was successful."
            },
            "folder_id": {
                "type": "string",
                "description": "The ID of the newly created folder."
            },
            "error": {
                "type": "string",
                "description": "Error message if the operation failed."
            }
        },
        description="The result of the folder creation operation."
    )
)

TOOL_GET_EMAIL_BY_ID = ToolSchema(
    name="get_email_by_id",
    description="Retrieve a specific email by its ID.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "email_id": {
                "type": "string",
                "description": "The ID of the email to retrieve.",
            },
        },
        required=["email_id"],
    ),
)

TOOL_SEARCH_EMAILS = ToolSchema(
    name="search_emails",
    description="Search for emails using a query string.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "query": {
                "type": "string",
                "description": "The search query to find emails.",
            },
        },
        required=["query"],
    ),
)

TOOL_SEND_EMAIL = ToolSchema(
    name="send_email",
    description="Send an email.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "subject": {
                "type": "string",
                "description": "The subject of the email.",
            },
            "body": {
                "type": "string",
                "description": "The main content of the email, format it using HTML to enhance structure and readability.",
            },
            "to_recipients": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of email addresses for the primary recipients.",
            }
        },
        required=["subject", "body", "to_recipients"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "result": {
                "type": "string",
                "description": "The result of the email sending operation.",
            },
            "message_id": {
                "type": "string",
                "description": "The ID of the sent email (only present if result is 'success').",
            },
            "message": {
                "type": "string",
                "description": "Additional information or error message.",
            },
        },
        description="The result of the email sending operation."
    ),
)

TOOL_REPLY_TO_MAIL = ToolSchema(
    name="reply_to_mail",
    description="Reply to an existing email.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "message_id": {
                "type": "string",
                "description": "The ID of the email to reply to.",
            },
            "comment": {
                "type": "string",
                "description": "Text to include in the reply.",
            },
        },
        required=["message_id", "comment"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "result": {
                "type": "string",
                "description": "The result of the email reply operation.",
            },
            "message_id": {
                "type": "string",
                "description": "The ID of the email replied to (only present if result is 'success').",
            },
            "message": {
                "type": "string",
                "description": "Additional information or error message.",
            },
        },
        description="The result of the email reply operation."
    ),
)
