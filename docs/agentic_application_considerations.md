# Multi-Agent Systems: Architecture and Implementation

## Basic Architecture
The best resource for understanding the architecture and functioning of multi-agent systems is the *Magnetic-One* paper and code by Microsoft. These systems rely on asynchronous communication between agents that send and respond to messages.

## Role of the Orchestrator
The orchestrator is the central component that:
- Receives the task from the user
- Creates an execution plan (task ledger)
- Monitors the execution of the plan
- Assigns specific instructions to agents at each step to complete different phases of the plan

## Agent Design
Agents are specialized in a single field. Several studies show that giving the LLM behind the agent a single operational scope improves performance. It is better to have multiple specialized agents rather than one general-purpose agent.

Each agent:
- Uses an LLM to reason and respond to the orchestrator’s messages
- Can access a set of tools (functions) to perform actions on external or local services
- Accesses functions through the Function Calling standard


## Function Implementation
Functions are:
- Defined by the user
- Executed locally in the application

For sensitive operations (e.g., CRUD on a database), an HIL (Human In The Loop) approach can be implemented:
- The user receives notifications about the operations the agent wants to execute
- The user can approve or reject these operations

## Error Handling and Context Management
To ensure the system works correctly:
- Errors should be descriptive, allowing agents to fix them when possible
- It is important to remind agents of the execution context
- For long conversations, creating summaries of messages and actions prevents exceeding the context window
- Reasoning phases, executed through the progress ledger, are essential to maintain the execution state of the task

## Testing
To test agent-based systems, it is necessary to:
- Create a benchmark using the real LLM as the orchestrator (do not mock LLMs)
- Mock only the functions, not the LLM itself
- Run each test multiple times, as LLMs generate different responses in each execution
- Use the benchmark to evaluate if changes improve the system

## Possible Extensions
The system can be extended to include:
- User-orchestrator conversations to better define the task (similar to OpenAI's DeepSearch)
- Different LLMs for different roles: more complex models for the orchestrator and smaller models for agents with simpler tasks

## Advantages
The main advantages of these systems are:
- Ability to plan and execute user-defined goals
- Better user experience by using natural language instead of a GUI
- The system can ask clarifying questions when the initial prompt is unclear
