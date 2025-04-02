from autogen_core.components.tools._base import ParametersSchema, ToolSchema

TOOL_GET_CALENDAR_EVENTS = ToolSchema(
    name="get_calendar_events",
    description="Retrieve calendar events from the Outlook calendar with optional filtering and limit.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "filter_params": {
                "type": "string",
                "description": """OData filter query string to filter calendar events. Supports logical operators (and, or, not), 
                comparison operators (eq, ne, gt, ge, lt, le), and string functions. Examples:
                - "subject eq 'Team Meeting'"
                - "start/dateTime ge '2024-01-01T00:00:00Z'"
                - "isAllDay eq true"
                - "importance eq 'high'"
                Leave empty to retrieve all events without filtering.""",
            },
        },
        required=[],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "events": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "subject": {"type": "string"},
                        "start": {"type": "object"},
                        "end": {"type": "object"},
                        "organizer": {"type": "object"},
                        "attendees": {"type": "array"}
                    }
                },
                "description": "A list of calendar events, each containing event details."
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation."
            }
        },
        description="Either a list of calendar events or an error message if the operation failed."
    )
)

TOOL_CREATE_MEETING = ToolSchema(
    name="create_meeting",
    description="Create a new meeting in the Outlook calendar.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "subject": {
                "type": "string",
                "description": "The subject of the meeting",
            },
            "start_time": {
                "type": "string",
                "description": "The start time of the meeting (in ISO 8601 format, for example 2023-06-01T10:00:00)",
            },
            "end_time": {
                "type": "string",
                "description": "The end time of the meeting (in ISO 8601 format, for example 2023-06-01T10:00:00)",
            },
            "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of attendee email addresses",
            },
            "location": {
                "type": "string",
                "description": "Optional location of the meeting",
            },
            "body": {
                "type": "string",
                "description": "Optional body content of the meeting invitation",
            },
        },
        required=["subject", "start_time", "end_time"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "id": {"type": "string"},
            "subject": {"type": "string"},
            "start": {"type": "object"},
            "end": {"type": "object"},
            "attendees": {"type": "array"},
            "location": {"type": "string"},
            "webLink": {"type": "string"},
            "error": {"type": "string"},
        },
        description="Details of the created meeting or an error message if the creation failed."
    )
)

TOOL_GET_AVAILABLE_SLOTS = ToolSchema(
    name="get_available_slots",
    description="Find available slots for meetings within a specified time range for a single day.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "start_time": {
                "type": "string",
                "description": "The start of the time range (ISO 8601 format) for the day.",
            },
            "end_time": {
                "type": "string",
                "description": "The end of the time range (ISO 8601 format) for the same day as start_time.",
            },
            "meeting_duration": {
                "type": "integer",
                "description": "Duration of the meeting in minutes (default 60)",
            },
            "buffer": {
                "type": "integer",
                "description": "Buffer time between meetings in minutes (default 0)",
            },
            "lunch_hour": {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": 2,
                "maxItems": 2,
                "description": "Tuple of (start_hour, end_hour) for lunch break (default [13, 14] for 1 PM to 2 PM)",
            },
        },
        required=["start_time", "end_time"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "available_slots": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "start": {"type": "string"},
                        "end": {"type": "string"},
                    }
                },
                "description": "A list of available time slots for the specified day, each containing start and end times in ISO 8601 format.",
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation.",
            },
        },
        description="A dictionary containing either 'available_slots' with a list of available time slots, or 'error' with an error message if the operation failed."
    )
)
