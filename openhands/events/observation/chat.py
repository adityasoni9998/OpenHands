from dataclasses import dataclass

from openhands.events.observation.observation import Observation


@dataclass
class ChatObservation(Observation):
    npc_name: str

    @property
    def message(self) -> str:
        return f'Chat with {self.npc_name}'

    def __str__(self) -> str:
        ret = (
            '**ChatObservation**\n'
            f'NPC name: {self.npc_name}\n'
            f'NPC Response: {self.content}'
        )
        return ret
