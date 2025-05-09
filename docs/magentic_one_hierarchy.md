# Hierarchy

## BaseAgent
A foundational agent within the system responsible for handling incoming messages.

### Core Functionalities
Routes incoming messages based on their type:
- `RequestReply` (not implemented in this class)
- `Broadcast` (not implemented in this class)
- `Reset` (not implemented in this class)
- `Deactivate`: Deactivates the agent.

These functionalities are implemented in higher-level classes.

## BaseWorker (from BaseAgent)
An agent interacting with the external world, following the Magnetic-One behavior protocol.

### Features
- Maintains chat history with a list of `LLMMessage`.
- Handles:
  - **Broadcast**: Adds message to the chat.
  - **Reset**: Clears chat history.
  - **RequestReply**: Generates a response using an LLM (not implemented), appending the message as an `AssistantMessage`.
  - Converts responses to `UserMessage` for visibility to other agents.

## Coder (from BaseWorker)
A real agent powered by an LLM for coding assistance.

### Features
- **System message**: Defines agent as an AI coding assistant.
- **Model**: Specifies the LLM used.
- **Request terminate**: Triggers "TERMINATE" when the task is complete.

### Behavior
- Generates Python and Shell scripts.
- Does not execute but can debug its own code.
- Calls the LLM with system messages and chat history.
- Checks for "TERMINATE" in the response to halt execution.

## Executor (from BaseWorker)
A deterministic agent designed to execute code.

### Features
- **Check last N messages**: Identifies the first code block for execution.
- **Executor**: Runs extracted code.
- **Confirm execution**: Implements human-in-the-loop confirmation.

### Behavior
- Scans recent messages for `UserMessage` containing code.
- Extracts, executes, and returns output.
- Requests confirmation before execution (if enabled).
- Broadcasts results to the orchestrator for further action.

## FileSurfer (from BaseWorker)
An agent utilizing tools.

### Features
- **Tools**: A set of predefined functions.
- **Model**: Specifies the LLM.
- **System message**: Provides contextual information.

### Behavior
- Constructs a `UserMessage` for context and task.
- Appends messages to private chat and queries LLM.
- Handles `FunctionCall` responses, executing functions as needed.
- Broadcasts errors and updates the final browser state.

## WebSurfer (from BaseWorker)
An agent utilizing tools to navigate the web.

## BaseOrchestrator
Manages a list of `AgentProxy` instances, coordinating execution.

### Features
- **Max rounds**: Limits execution iterations.
- **Max time**: Defines execution duration.

### Behavior
- **Broadcast**: Evaluates messages, checks termination conditions, assigns tasks to agents, and sends `RequestReplyMessage`.
- **Reset**: No implemented action.
- **RequestReply**: Not applicable (orchestrator does not receive such messages).

## LedgerOrchestrator (from BaseOrchestrator)
A more advanced orchestrator implementing additional logic.

### Additional Features
- **Max stalls before replan**.
- **Max replan attempts**.
- **Chat history maintenance**.

### Behavior
- Maintains a **task ledger** as a JSON structure generated by the LLM to track progress.
- Handles `Broadcast` events and logs them in chat history.
- Selects the next agent based on the ledger's state.
- Updates and verifies task ledger information.
- Generates a **completion plan** when a task is marked as completed.
- If progress stalls, it attempts to **replan** by updating facts and creating a new plan.
- Manages multiple rounds of conversation, ensuring tasks reach completion effectively.
- Uses **prompts** to guide task execution, summarize steps, and synthesize final answers.
- Handles **final answer generation** by summarizing the task execution history when conditions are met.

## Magnetic-One Message Types
- **RequestReplyMessage**: Prompts an agent for action.
- **BroadcastMessage**: Primary agent-orchestrator communication.
- **DeactivateMessage**: Removes an agent from execution.
- **ResetMessage**: Resets an agent's state.

### Events
- **OrchestrationEvent**: Logs orchestration decisions.
- **AgentEvent**: Logs agent actions.
- **WebSurferEvent**: Logs browsing activity.

## Other Message Types (AutogenCore)
- **UserMessage**: Represents user input or agent-generated input.
- **AssistantMessage**: Response from an agent.
- **SystemMessage**: Provides execution context.
- **FunctionExecutionResultMessage**: Stores function outputs.
- **LLMMessage**: Generalized chat message format.

Each agent maintains an independent chat history synchronized through `BroadcastMessages`.
