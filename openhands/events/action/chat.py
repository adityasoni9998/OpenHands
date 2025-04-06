from dataclasses import dataclass
from typing import ClassVar

from openhands.core.schema import ActionType
from openhands.events.action.action import Action


@dataclass
class ChatAction(Action):
    content: str
    npc_name: str
    runnable: ClassVar[bool] = True
    action: str = ActionType.CHAT

    @property
    def message(self) -> str:
        return f'I am chatting with NPC user {self.npc_name}'

    def __str__(self) -> str:
        ret = '**ChatAction**\n'
        ret += f'MESSAGE: {self.content}\n'
        ret += f'NPC Name: {self.npc_name}'
        return ret
