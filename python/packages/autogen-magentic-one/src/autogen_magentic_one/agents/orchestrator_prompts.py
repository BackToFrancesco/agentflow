ORCHESTRATOR_SYSTEM_MESSAGE = ""


ORCHESTRATOR_CLOSED_BOOK_PROMPT = """Below I will present you a request. Before we begin addressing the request, please answer the following pre-survey to the best of your ability. Keep in mind that you are Ken Jennings-level with trivia, and Mensa-level with puzzles, so there should be a deep well to draw from.

Here is the request:

{task}

Here is the pre-survey:

    1. Please list any specific facts or figures that are GIVEN in the request itself. It is possible that there are none.
    2. Please list any facts that may need to be looked up, and WHERE SPECIFICALLY they might be found. In some cases, authoritative sources are mentioned in the request itself.
    3. Please list any facts that may need to be derived (e.g., via logical deduction, simulation, or computation)
    4. Please list any facts that are recalled from memory, hunches, well-reasoned guesses, etc.

When answering this survey, keep in mind that "facts" will typically be specific names, dates, statistics, etc. Your answer should use headings:

    1. GIVEN OR VERIFIED FACTS
    2. FACTS TO LOOK UP
    3. FACTS TO DERIVE
    4. EDUCATED GUESSES

DO NOT include any other headings or sections in your response. DO NOT list next steps or plans until asked to do so.
"""


ORCHESTRATOR_PLAN_PROMPT = """Fantastic. To address this request we have assembled the following team:

{team}

Based on the team composition, and known and unknown facts, please devise a short bullet-point plan for addressing the original request. Remember, there is no requirement to involve all team members -- a team member's particular expertise may not be needed for this task."""


ORCHESTRATOR_SYNTHESIZE_PROMPT = """
We are working to address the following user request:

{task}


To answer this request we have assembled the following team:

{team}


Here is an initial fact sheet to consider:

{facts}


Here is the plan to follow as best as possible:

{plan}
"""

ORCHESTRATOR_LEDGER_PROMPT = """
Recall we are working on the following request:

{task}

And we have assembled the following team:

{team}

To make progress on the request, please answer the following questions, including necessary reasoning:

    - Is the request fully satisfied? (True if complete, or False if the original request has yet to be SUCCESSFULLY and FULLY addressed)
    - Are we in a loop where we are repeating the same requests and / or getting the same responses as before? Loops can span multiple turns, and can include repeated actions like scrolling up or down more than a handful of times.
    - Are we making forward progress? (True if just starting, or recent messages are adding value. False if recent messages show evidence of being stuck in a loop or if there is evidence of significant barriers to success such as the inability to read from a required file)
    - Who should speak next? (select from: {names})
    - What SINGLE instruction or question would you give this team member? (Phrase as if speaking directly to them, and include any specific information they may need. Request only one action - do not combine multiple action since the agents can perform one action per time.)

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
        "next_speaker": {{
            "reason": string,
            "answer": string (select from: {names})
        }},
        "instruction_or_question": {{
            "reason": string,
            "answer": string
        }}
    }}
"""


ORCHESTRATOR_UPDATE_FACTS_PROMPT = """As a reminder, we are working to solve the following task:

{task}

It's clear we aren't making as much progress as we would like, but we may have learned something new. Please rewrite the following fact sheet, updating it to include anything new we have learned that may be helpful. Example edits can include (but are not limited to) adding new guesses, moving educated guesses to verified facts if appropriate, etc. Updates may be made to any section of the fact sheet, and more than one section of the fact sheet can be edited. This is an especially good time to update educated guesses, so please at least add or update one educated guess or hunch, and explain your reasoning.

Here is the old fact sheet:

{facts}
"""

ORCHESTRATOR_UPDATE_PLAN_PROMPT = """Please briefly explain what went wrong on this last run (the root cause of the failure), and then come up with a new plan that takes steps and/or includes hints to overcome prior challenges and especially avoids repeating the same mistakes. As before, the new plan should be concise, be expressed in bullet-point form, and consider the following team composition (do not involve any other outside people since we cannot contact anyone else):

{team}
"""

ORCHESTRATOR_GET_FINAL_ANSWER = """
We are working on the following task:
{task}

We have completed the task.

The above messages contain the conversation that took place to complete the task.

Based on the information gathered, provide the final answer to the original request.
The answer should be phrased as if you were speaking to the user.
"""

ORCHEORCHESTRATOR_SUMMARIZE_STEPS_SYSTEM_MESSAGE = "You are an AI assistant tasked with summarizing the steps taken in a conversation."

ORCHESTRATOR_SUMMARIZE_STEPS_PROMPT = """
Review the entire conversation and create a summary of all the steps taken so far to complete the task.
For each step, provide:
1. The action taken
2. The result of that action
3. The status of the action (COMPLETED/ NOT COMPLETED)
4. The reason on the status of the action

Format the summary as a numbered list.

Original task: {task}
Entire conversation:
{conversation}
"""

ORCHESTRATOR_CREATE_COMPLETION_PLAN_SYSTEM_MESSAGE = "You are an AI assistant tasked with creating detailed plans to complete complex tasks."

ORCHESTRATOR_CREATE_COMPLETION_PLAN_PROMPT = """
Initial Request: {initial_request}

Reason why the task is not yet completed: {reason}

Create a detailed plan to complete the task. The plan should provide only the actions needed to solve why the task is not yet completed.
Don't repeat in the plan action that have been already succesfully performed

Present the plan in the following format:
PLAN:
• [Action 1]
• [Action 2]
• [Action 3]
...

Ensure that the plan is comprehensive and covers all necessary steps to fully complete the task.
"""

ORCHESTRATOR_TASK_COMPLETED_CONFIRMATION_PROMPT = """
Read the steps taken and confirm if the original request is completely satisfied.
Produce a JSON response with two fields:
1. request_satisfied: true or false
2. reason: A brief explanation of why the request is or is not satisfied

Original request: {task}
Steps taken:
{steps_summary}

Respond only with the JSON, no other text.
"""

################################################
# Autoform
################################################
ORCHESTRATOR_CLOSED_BOOK_PROMPT_AUTOFORM = """Below I will present you a request. Before we begin addressing the request, please answer the following pre-survey to the best of your ability. Keep in mind that you are Ken Jennings-level with trivia, and Mensa-level with puzzles, so there should be a deep well to draw from.

Here is the request:

{task}

Here is the pre-survey:

    1. Please list any specific facts or figures that are GIVEN in the request itself. It is possible that there are none.
    2. Please list any facts that may need to be looked up, and WHERE SPECIFICALLY they might be found. In some cases, authoritative sources are mentioned in the request itself.
    3. Please list any facts that may need to be derived (e.g., via logical deduction, simulation, or computation)
    4. Please list any facts that are recalled from memory, hunches, well-reasoned guesses, etc.

When answering this survey, keep in mind that "facts" will typically be specific names, dates, statistics, etc. Your answer should use headings:

    1. GIVEN OR VERIFIED FACTS
    2. FACTS TO LOOK UP
    3. FACTS TO DERIVE
    4. EDUCATED GUESSES

DO NOT include any other headings or sections in your response. DO NOT list next steps or plans until asked to do so.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""


ORCHESTRATOR_PLAN_PROMPT_AUTOFORM = """Fantastic. To address this request we have assembled the following team:

{team}

Based on the team composition, and known and unknown facts, please devise a short bullet-point plan for addressing the original request. Remember, there is no requirement to involve all team members -- a team member's particular expertise may not be needed for this task.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""


ORCHESTRATOR_SYNTHESIZE_PROMPT_AUTOFORM = """
We are working to address the following user request:

{task}


To answer this request we have assembled the following team:

{team}


Here is an initial fact sheet to consider:

{facts}


Here is the plan to follow as best as possible:

{plan}
"""

ORCHESTRATOR_LEDGER_PROMPT_AUTOFORM = """
Recall we are working on the following request:

{task}

And we have assembled the following team:

{team}

To make progress on the request, please answer the following questions, including necessary reasoning:

    - Is the request fully satisfied? (True if complete, or False if the original request has yet to be SUCCESSFULLY and FULLY addressed)
    - Are we in a loop where we are repeating the same requests and / or getting the same responses as before? Loops can span multiple turns, and can include repeated actions like scrolling up or down more than a handful of times.
    - Are we making forward progress? (True if just starting, or recent messages are adding value. False if recent messages show evidence of being stuck in a loop or if there is evidence of significant barriers to success such as the inability to read from a required file)
    - Who should speak next? (select from: {names})
    - What SINGLE instruction or question would you give this team member? (Phrase as if speaking directly to them, and include any specific information they may need. Request only one action - do not combine multiple action since the agents can perform one action per time.)

Please output an answer in pure JSON format according to the following schema. The JSON object must be parsable as-is. DO NOT OUTPUT ANYTHING OTHER THAN JSON, AND DO NOT DEVIATE FROM THIS SCHEMA:

Remember to be concise and accurate.
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
        "next_speaker": {{
            "reason": string,
            "answer": string (select from: {names})
        }},
        "instruction_or_question": {{
            "reason": string (Use a pseudocode-like format), 
            "answer": string
        }}
    }}

IMPORTANT:
In each field that require a string, to enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses for examples structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""


ORCHESTRATOR_UPDATE_FACTS_PROMPT_AUTOFORM = """As a reminder, we are working to solve the following task:

{task}

It's clear we aren't making as much progress as we would like, but we may have learned something new. Please rewrite the following fact sheet, updating it to include anything new we have learned that may be helpful. Example edits can include (but are not limited to) adding new guesses, moving educated guesses to verified facts if appropriate, etc. Updates may be made to any section of the fact sheet, and more than one section of the fact sheet can be edited. This is an especially good time to update educated guesses, so please at least add or update one educated guess or hunch, and explain your reasoning.

IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses.
Remember to be concise and accurate.

Here is the old fact sheet:

{facts}
"""

ORCHESTRATOR_UPDATE_PLAN_PROMPT_AUTOFORM = """Please briefly explain what went wrong on this last run (the root cause of the failure), and then come up with a new plan that takes steps and/or includes hints to overcome prior challenges and especially avoids repeating the same mistakes. As before, the new plan should be concise, be expressed in bullet-point form, and consider the following team composition (do not involve any other outside people since we cannot contact anyone else):

{team}
"""

ORCHESTRATOR_GET_FINAL_ANSWER_AUTOFORM = """
We are working on the following task:
{task}

We have completed the task.

The above messages contain the conversation that took place to complete the task.

Based on the information gathered, provide the final answer to the original request.
The answer should be phrased as if you were speaking to the user.
"""

ORCHEORCHESTRATOR_SUMMARIZE_STEPS_SYSTEM_MESSAGE_AUTOFORM = """
You are an AI assistant tasked with summarizing the steps taken in a conversation.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""

ORCHESTRATOR_SUMMARIZE_STEPS_PROMPT_AUTOFORM = """
Review the entire conversation and create a summary of all the steps taken so far to complete the task.
For each step, provide:
1. The action taken
2. The result of that action
3. The status of the action (COMPLETED/ NOT COMPLETED)
4. The reason on the status of the action

Format the summary as a numbered list.

IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.

Original task: {task}
Entire conversation:
{conversation}
"""

ORCHESTRATOR_CREATE_COMPLETION_PLAN_SYSTEM_MESSAGE_AUTOFORM = """
You are an AI assistant tasked with creating detailed plans to complete complex tasks.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""

ORCHESTRATOR_CREATE_COMPLETION_PLAN_PROMPT_AUTOFORM = """
Initial Request: {initial_request}

Reason why the task is not yet completed: {reason}

Create a detailed plan to complete the task. The plan should provide only the actions needed to solve why the task is not yet completed.
Don't repeat in the plan action that have been already succesfully performed

Present the plan in the following format:
PLAN:
• [Action 1]
• [Action 2]
• [Action 3]
...

Ensure that the plan is comprehensive and covers all necessary steps to fully complete the task.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses. Suitable formats include structured data, JSON, XML or code. Choose the most appropriate format based on the nature of the query and the information you need to convey.
Remember to be concise and accurate.
"""

ORCHESTRATOR_TASK_COMPLETED_CONFIRMATION_PROMPT_AUTOFORM = """
Read the steps taken and confirm if the original request is completely satisfied.
Produce a JSON response with two fields:
1. request_satisfied: true or false
2. reason: A brief explanation of why the request is or is not satisfied

Original request: {task}
Steps taken:
{steps_summary}

Respond only with the JSON, no other text.
IMPORTANT:
To enhance clarity and eliminate ambiguities inherent in natural language, do not use natural language. Consider employing more structured and concise forms of communication for your responses.
Remember to be concise and accurate.
"""