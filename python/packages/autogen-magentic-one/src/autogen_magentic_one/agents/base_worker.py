from typing import List, Tuple, Any
import json

from autogen_core.base import CancellationToken, MessageContext, TopicId
from autogen_core.components.models import (
    AssistantMessage,
    LLMMessage,
    UserMessage,
    SystemMessage,
)

from autogen_magentic_one.messages import (
    AgentEvent,
    BroadcastMessage,
    RequestReplyMessage,
    ResetMessage,
    UserContent,
)

from ..utils import message_content_to_str
from .base_agent import MagenticOneBaseAgent
from .worker_prompts import WORKER_COMPLETION_CHECK_PROMPT, WORKER_COMPLETION_CHECK_PROMPT_AUTOFORM, WORKER_SUMMARY_PROMPT, WORKER_SUMMARY_PROMPT_AUTOFORM, WORKER_SUMMARY_SYSTEM_MESSAGE, WORKER_SUMMARY_SYSTEM_MESSAGE_AUTOFORM, WORKER_TASK_COMPLETION_CHECK_SYSTEM_MESSAGE, WORKER_TASK_COMPLETION_CHECK_SYSTEM_MESSAGE_AUTOFORM


class BaseWorker(MagenticOneBaseAgent):
    """Base agent that handles the MagenticOne worker behavior protocol."""

    def __init__(
        self,
        description: str,
        handle_messages_concurrently: bool = False,
        model_client: Any = None,
        enable_multiple_turns = False,
        autoform_prompt = False
    ) -> None:
        super().__init__(description, handle_messages_concurrently=handle_messages_concurrently)
        self._chat_history: List[LLMMessage] = []
        self._model_client = model_client
        self._enable_multiple_turns = enable_multiple_turns
        self._loop_counter = 0
        self._autoform_prompt = autoform_prompt
        self._current_task = ""

    async def _handle_broadcast(self, message: BroadcastMessage, ctx: MessageContext) -> None:
        assert isinstance(message.content, UserMessage)
        self._chat_history.append(message.content)

    async def _handle_reset(self, message: ResetMessage, ctx: MessageContext) -> None:
        """Handle a reset message."""
        await self._reset(ctx.cancellation_token)

    async def _handle_request_reply(self, message: RequestReplyMessage, ctx: MessageContext) -> None:
        """Respond to a reply request."""
        self._current_task = self._chat_history[-1].content
        if self._enable_multiple_turns:
            request_halt, response = await self._execute_task_with_completion_check([], [], ctx.cancellation_token)
        else:
            request_halt, response = await self._generate_reply(ctx.cancellation_token)

        assistant_message = AssistantMessage(content=message_content_to_str(response), source=self.metadata["type"])
        self._chat_history.append(assistant_message)

        user_message = UserMessage(content=response, source=self.metadata["type"])
        topic_id = TopicId("default", self.id.key)
        await self.publish_message(
            BroadcastMessage(content=user_message, request_halt=request_halt),
            topic_id=topic_id,
            cancellation_token=ctx.cancellation_token,
        )

    async def _check_task_completion(
        self, 
        task_description: str,
        action_taken: str,
        result: Any,
        cancellation_token: CancellationToken
    ) -> Tuple[bool, str, str, bool]:
        completion_check_prompt = (WORKER_COMPLETION_CHECK_PROMPT if self._autoform_prompt else WORKER_COMPLETION_CHECK_PROMPT_AUTOFORM).format(
            agent_type=self.metadata["type"],
            chat_history=self._chat_history,
            task_description=task_description,
            action_taken=action_taken,
            result=json.dumps(result)
        )
        completion_check_response = await self._model_client.create(
            messages=[
                SystemMessage(WORKER_TASK_COMPLETION_CHECK_SYSTEM_MESSAGE_AUTOFORM if self._autoform_prompt else WORKER_TASK_COMPLETION_CHECK_SYSTEM_MESSAGE),
                UserMessage(completion_check_prompt, source=self.metadata["type"])
            ],
            json_output=True,
            cancellation_token=cancellation_token
        )
        
        completion_result = json.loads(completion_check_response.content)
        
        is_request_satisfied = completion_result["is_request_satisfied"]["answer"]
        reason = completion_result["is_request_satisfied"]["reason"]
        instruction_or_question = completion_result["instruction_or_question"]["answer"]
        is_in_loop = completion_result["is_in_loop"]["answer"]
        loop_reason = completion_result["is_in_loop"]["reason"]
        is_progress_being_made = completion_result["is_progress_being_made"]["answer"]
        is_progress_being_made_reason = completion_result["is_progress_being_made"]["reason"]
        
        return is_request_satisfied, reason, instruction_or_question, is_in_loop, loop_reason, is_progress_being_made, is_progress_being_made_reason

    async def _execute_task_with_completion_check(self, inner_chat_history, inner_response_history, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        request_halt, response = await self._generate_reply(cancellation_token)
        
        is_request_satisfied, reason, instruction_or_question, is_in_loop, loop_reason, is_progress_being_made, is_progress_being_made_reason = await self._check_task_completion(
            self._chat_history[-1].content,
            inner_chat_history,
            response,
            cancellation_token
        )

        # Update the chat history and logging
        self._chat_history.append(UserMessage(content=response, source=self.metadata["type"]))
        self._chat_history.append(UserMessage(content=f"Task completion status: {'Complete' if is_request_satisfied else 'Incomplete'}\nReason: {reason}.", source=self.metadata["type"]))
        self._chat_history.append(UserMessage(content=f"{instruction_or_question}", source=self.metadata["type"]))
        inner_chat_history.append(response)
        inner_response_history.append(response)
        inner_chat_history.append(f"Task completion status: {'Complete' if is_request_satisfied else 'Incomplete'}\nReason: {reason}.")
        inner_chat_history.append(f"{instruction_or_question}")

        if is_in_loop and not is_progress_being_made:
            self._loop_counter += 1
        else:
            self._loop_counter = 0

        if is_in_loop and self._loop_counter > 3:
            inner_chat_history.append(f"Task in loop for the following reason: {reason}. Exiting..")
            self.logger.info(
                AgentEvent(
                    f"{self.metadata['type']} (response)",
                    f"Task in loop for the following reason: {reason}. Exiting.."
                )
            )
        
        self.logger.info(
            AgentEvent(
                f"{self.metadata['type']} (response)",
                response,
            )
        )
        self.logger.info(
            AgentEvent(
                f"{self.metadata['type']} (update ledger)",
                f"""Updated Ledger:\n{json.dumps({
                "task_complete": is_request_satisfied,
                "task_complete_reason": reason,
                "self_follow_up_instruction": "None" if is_request_satisfied else instruction_or_question,
                "is_in_loop": is_in_loop,
                "is_in_loop_reason": loop_reason if is_in_loop else "None",
                "is_progress_being_made": is_progress_being_made,
                "is_progress_being_made_reason": is_progress_being_made_reason
                })}"""
            )
        )

        if not is_request_satisfied and not (is_in_loop and not is_progress_being_made and self._loop_counter > 3):
            # If the task is not complete, recursively call _execute_task_with_completion_check
            return await self._execute_task_with_completion_check(inner_chat_history, inner_response_history, cancellation_token)
        self._loop_counter = 0
        summary_inner_chat_prompt = (WORKER_SUMMARY_PROMPT_AUTOFORM if self._autoform_prompt else WORKER_SUMMARY_PROMPT).format(inner_response_history=inner_response_history, task=self._current_task)

        summary_response = await self._model_client.create(
            messages=[
                SystemMessage(WORKER_SUMMARY_SYSTEM_MESSAGE_AUTOFORM if self._autoform_prompt else WORKER_SUMMARY_SYSTEM_MESSAGE),
                UserMessage(summary_inner_chat_prompt, source=self.metadata["type"])
            ],
            cancellation_token=cancellation_token
        )

        return request_halt, summary_response.content

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """Returns (request_halt, response_message)"""
        raise NotImplementedError()

    async def _reset(self, cancellation_token: CancellationToken) -> None:
        self._chat_history = []
