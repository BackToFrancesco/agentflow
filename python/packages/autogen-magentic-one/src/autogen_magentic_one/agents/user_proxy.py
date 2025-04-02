import asyncio
import sys
from typing import Tuple
from queue import Queue

from autogen_core.base import CancellationToken
from autogen_core.components import default_subscription

from ..messages import UserContent
from .base_worker import BaseWorker


@default_subscription
class UserProxy(BaseWorker):
    """An agent that allows the user to play the role of an agent in the conversation via input."""

    DEFAULT_DESCRIPTION = "A human user."

    def __init__(
        self,
        description: str = DEFAULT_DESCRIPTION,
        message_queue: Queue = None,
        input_event: asyncio.Event = None,
        user_input_needed_event: asyncio.Event = None
    ) -> None:
        super().__init__(description)
        self.message_queue = message_queue
        self.input_event = input_event
        self.user_input_needed_event = user_input_needed_event

    async def _generate_reply(self, cancellation_token: CancellationToken) -> Tuple[bool, UserContent]:
        """Respond to a reply request."""
        if self.message_queue is not None and self.input_event is not None:
            if self.user_input_needed_event:
                self.user_input_needed_event.set()
            await self.input_event.wait()
            response = self.message_queue.get()
            self.input_event.clear()
        else:
            response = await self.ainput("User input ('exit' to quit): ")
        
        response = response.strip()
        return response == "exit", response

    async def ainput(self, prompt: str) -> str:
        print(prompt, end='', flush=True)
        raw_input = await asyncio.to_thread(sys.stdin.read, 1)
        if raw_input == '\n':
            return ''
        while True:
            char = await asyncio.to_thread(sys.stdin.read, 1)
            if char == '\n':
                break
            raw_input += char
        return raw_input.strip()
