WORKER_COMPLETION_CHECK_PROMPT = """
You are the {agent_type} and you are working in collaboration with other agents.
You can see the ongoing chat with other agents here: {chat_history}.

Now this is your turn and you are working to solve the following Task:
{task_description}
You are having a inner dialogue with yourself to complete the task. This is the dialogue so far:
{action_taken}
This is the result of the last action you have made:
{result}

IMPORTANT:
- Always attempt all possible actions to achieve the best outcome for the task.
- If at any point a message in the conversation explicitly states that the requested task cannot be fully performed and suggests moving to another agent, consider the task fully completed (since no further actions can be taken).

Is the requested task "{task_description}" fully completed? Respond with a JSON object containing:
    - Is the request fully satisfied? (True if complete, or False if the task has yet to be SUCCESSFULLY and FULLY addressed)
    - Are we in a loop where we are repeating the same requests and / or getting the same responses as before? Loops can span multiple turns, and can include repeated actions like scrolling up or down more than a handful of times.
    - Are we making forward progress? (True if just starting, or recent messages are adding value. False if recent messages show evidence of being stuck in a loop or if there is evidence of significant barriers to success such as the inability to read from a required file)
    - What instruction or question would you give to solve the task? (Phrase as if speaking directly to yourself include any specific information needed)

Please output an answer in pure JSON format according to the following schema. The JSON object must be parsable as-is. DO NOT OUTPUT ANYTHING OTHER THAN JSON, AND DO NOT DEVIATE FROM THIS SCHEMA:
{{
"is_request_satisfied": {{
        "reason": string,
        "answer": boolean
    }},
    "is_in_loop": {{
        "reason": string,
        "answer": boolean
    }},
    "is_progress_being_made": {{
        "reason": string,
        "answer": boolean
    }},
    "instruction_or_question": {{
        "reason": string,
        "answer": string
    }}
}}
"""

WORKER_SUMMARY_PROMPT = """
You have been assigned to the following task: {task}
You have performed some action listed in the chat below, now you have to comunicate the actions performed and their results to other agents to complete the task.
Provide a comprehensive summary of the operations performed and their results based on the following chat history:
{inner_response_history}
"""

WORKER_TASK_COMPLETION_CHECK_SYSTEM_MESSAGE = """
You are an AI assistant tasked with determining if a task is complete.
"""

WORKER_SUMMARY_SYSTEM_MESSAGE = """
You are an AI assistant specialized in analyzing and summarizing complex task executions.
Your role is to provide clear, concise, and structured summaries of operations performed and their outcomes.
Focus on accuracy and completeness, ensuring that all key information is captured and presented in a logical order.
"""

################################################
# Autoform
################################################
WORKER_COMPLETION_CHECK_PROMPT_AUTOFORM = """
You are the {agent_type} and you are working in collaboration with other agents.
You can see the ongoing chat with other agents here: {chat_history}.

Now this is your turn and you are working to solve the following Task:
{task_description}
You are having a inner dialogue with yourself to complete the task. This is the dialogue so far:
{action_taken}
This is the result of the last action you have made:
{result}

IMPORTANT:
- Always attempt all possible actions to achieve the best outcome for the task.
- If at any point a message in the conversation explicitly states that the requested task cannot be fully performed and suggests moving to another agent, consider the task fully completed (since no further actions can be taken).

Is the requested task "{task_description}" fully completed? Respond with a JSON object containing:
    - Is the request fully satisfied? (True if complete, or False if the task has yet to be SUCCESSFULLY and FULLY addressed)
    - Are we in a loop where we are repeating the same requests and / or getting the same responses as before? Loops can span multiple turns, and can include repeated actions like scrolling up or down more than a handful of times.
    - Are we making forward progress? (True if just starting, or recent messages are adding value. False if recent messages show evidence of being stuck in a loop or if there is evidence of significant barriers to success such as the inability to read from a required file)
    - What instruction or question would you give to solve the task? (Phrase as if speaking directly to yourself include any specific information needed)

Please output an answer in pure JSON format according to the following schema. The JSON object must be parsable as-is. DO NOT OUTPUT ANYTHING OTHER THAN JSON, AND DO NOT DEVIATE FROM THIS SCHEMA:
{{
"is_request_satisfied": {{
        "reason": string,
        "answer": boolean
    }},
    "is_in_loop": {{
        "reason": string,
        "answer": boolean
    }},
    "is_progress_being_made": {{
        "reason": string,
        "answer": boolean
    }},
    "instruction_or_question": {{
        "reason": string,
        "answer": string
    }}
}}
IMPORTANT:
In each field that require a string, to enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses for examples structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""

WORKER_SUMMARY_PROMPT_AUTOFORM = """
You have been assigned to the following task: {task}
You have performed some action listed in the chat below, now you have to comunicate the actions performed and their results to other agents to complete the task.
Provide a comprehensive summary of the operations performed and their results based on the following chat history:
{inner_response_history}
"""

WORKER_TASK_COMPLETION_CHECK_SYSTEM_MESSAGE_AUTOFORM = """
You are an AI assistant tasked with determining if a task is complete.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
"""

WORKER_SUMMARY_SYSTEM_MESSAGE_AUTOFORM = """
You are an AI assistant specialized in analyzing and summarizing complex task executions.
Your role is to provide clear, concise, and structured summaries of operations performed and their outcomes.
Focus on accuracy and completeness, ensuring that all key information is captured and presented in a logical order.

IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""