from autogen_core.components.tools._base import ParametersSchema, ToolSchema

TOOL_SEND_MESSAGE = ToolSchema(
    name="send_message",
    description="Send a message to a Slack channel.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "channel": {
                "type": "string",
                "description": "The name or ID of the Slack channel to send the message to.",
            },
            "message": {
                "type": "string",
                "description": "The message to send. Use Slack markdown formatting for text formatting e.g.  Use *bold*, _italic_, ~strikethrough~, - bullet points, and numbered lists (1. 2. 3.)",
            },
            "use_user_token": {
                "type": "boolean",
                "description": "If True, use the user token instead of the bot token. Defaults to False.",
            },
        },
        required=["channel", "message"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "success": {
                "type": "boolean",
                "description": "Indicates whether the operation was successful.",
            },
            "error": {
                "type": "string",
                "description": "Error message if the operation failed.",
            },
        },
        description="The result of the message sending operation.",
    )
)

TOOL_SEND_PRIVATE_MESSAGE = ToolSchema(
    name="send_private_message",
    description="Send a private message to a Slack user.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "user_id": {
                "type": "string",
                "description": "The ID of the Slack user to send the message to.",
            },
            "message": {
                "type": "string",
                "description": "The message to send. Use Slack markdown formatting for text formatting e.g.  Use *bold*, _italic_, ~strikethrough~, - bullet points, and numbered lists (1. 2. 3.)",
            },
            "use_user_token": {
                "type": "boolean",
                "description": "If True, use the user token instead of the bot token. Defaults to False.",
            },
        },
        required=["user_id", "message"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "success": {
                "type": "boolean",
                "description": "Indicates whether the operation was successful.",
            },
            "error": {
                "type": "string",
                "description": "Error message if the operation failed.",
            },
        },
        description="The result of the private message sending operation.",
    )
)

TOOL_GET_UNREAD_MESSAGES = ToolSchema(
    name="get_unread_messages",
    description="Get unread messages from a Slack channel.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "channel": {
                "type": "string",
                "description": "The name or ID of the Slack channel to get messages from.",
            },
            "use_user_token": {
                "type": "boolean",
                "description": "If True, use the user token instead of the bot token. Defaults to False.",
            },
        },
        required=["channel"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "unread_messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The content of the message.",
                        },
                        "sender": {
                            "type": "string",
                            "description": "The name of the sender.",
                        }
                    },
                },
                "description": "A list of unread message objects, each containing message details.",
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation.",
            },
        },
        description="Either a list of unread messages or an error message if the operation failed.",
    )
)

TOOL_LIST_CHANNELS = ToolSchema(
    name="list_channels",
    description="List all channels that the bot is a member of.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "use_user_token": {
                "type": "boolean",
                "description": "If True, use the user token instead of the bot token. Defaults to False.",
            },
        },
        required=[],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "channels": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "The ID of the channel.",
                        },
                        "name": {
                            "type": "string",
                            "description": "The name of the channel.",
                        },
                    },
                },
                "description": "A list of channel objects, each containing channel details.",
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation.",
            },
        },
        description="Either a list of channels or an error message if the operation failed.",
    )
)

TOOL_GET_CHANNEL_MESSAGES = ToolSchema(
    name="get_channel_messages",
    description="Retrieve all messages from a given channel.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "channel": {
                "type": "string",
                "description": "The name or ID of the Slack channel to get messages from.",
            },
            "use_user_token": {
                "type": "boolean",
                "description": "If True, use the user token instead of the bot token. Defaults to False.",
            },
        },
        required=["channel"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The content of the message.",
                        },
                        "sender": {
                            "type": "string",
                            "description": "The name of the sender.",
                        },
                    },
                },
                "description": "A list of message objects, each containing message details.",
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation.",
            },
        },
        description="Either a list of messages or an error message if the operation failed.",
    )
)
