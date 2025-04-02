from autogen_core.components.tools._base import ParametersSchema, ToolSchema
from typing import Dict, Any, List

TOOL_CREATE_ISSUE = ToolSchema(
    name="create_issue",
    description="Create a new issue in Jira.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "project_key": {
                "type": "string",
                "description": "The key of the project where the issue will be created",
            },
            "issue_type": {
                "type": "string",
                "enum": ["Bug", "Task", "Story", "Epic"],
                "description": "The type of the issue",
            },
            "summary": {
                "type": "string",
                "description": "The summary (title) of the issue",
            },
            "description": {
                "type": "string",
                "description": "The description of the issue",
            },
        },
        required=["project_key", "issue_type", "summary", "description"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "id": {"type": "string"},
            "key": {"type": "string"},
            "name": {"type": "string"},
            "error": {"type": "string"},
        },
        description="Details of the created issue or an error message if the creation failed."
    )
)

TOOL_GET_PROJECT_ISSUES = ToolSchema(
    name="get_project_issues",
    description="Retrieve all issues for a specific project in Jira.",
    parameters=ParametersSchema(
        type="object",
        properties={
            "project_name": {
                "type": "string",
                "description": "The name of the project to retrieve issues from",
            },
        },
        required=["project_key"],
    ),
    returns=ParametersSchema(
        type="object",
        properties={
            "issues": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Key": {"type": "string"},
                        "Summary": {"type": "string"},
                        "Project": {"type": "string"},
                        "Issue Type": {"type": "string"},
                        "Priority": {"type": "string"},
                        "Status": {"type": "string"},
                        "Created": {"type": "string"},
                        "Updated": {"type": "string"},
                        "Due Date": {"type": "string"},
                    }
                },
                "description": "A list of issues in the specified project, each containing issue details."
            },
            "error": {
                "type": "string",
                "description": "Error message if an error occurred during the operation."
            }
        },
        description="Either a list of project issues or an error message if the operation failed."
    )
)

