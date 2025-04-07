import asyncio
import json
import os
import uuid

import aiohttp
from aiohttp.client import ClientSession, ClientWebSocketResponse

from openhands.events.action import ChatAction
from openhands.events.observation import ChatObservation, ErrorObservation, Observation


class ChatEnv:
    def __init__(self):
        TOKEN = str(uuid.uuid4())
        self.websocket_url: str = os.environ.get(
            'WEBSOCKET_URL', f'ws://localhost:8080/ws/simulation?token={TOKEN}'
        )
        self.scenarios_file: str = os.environ.get(
            'SCENARIOS_FILE', '/npc/scenarios.json'
        )
        self.session: ClientSession = aiohttp.ClientSession()
        self.started_env: bool = False
        self.agents: list[str] = []
        self.websocket: ClientWebSocketResponse | None = None

    async def start_simulation(self):
        if not os.path.exists(self.scenarios_file):
            return True

        with open(self.scenarios_file, 'r') as f:
            data: dict = json.load(f)

        self.websocket = await self.session.ws_connect(self.websocket_url)
        agent_profiles = data['agent_profiles']
        self.agents = [str(k) for k in agent_profiles.keys()]

        agent_profile_list: list = [profile for profile in agent_profiles.values()]
        agent_scenarios = data['scenarios']
        agent_goals = [
            agent_scenarios[agent]['goal']
            + ' <extra_info>'
            + agent_scenarios[agent]['extra_info']
            + '</extra_info> <strategy_hint>'
            + agent_scenarios[agent]['strategy_hint']
            + '</strategy_hint>'
            for agent in self.agents
        ]
        if 'agent_models' not in data:
            agent_models = ['gpt-4o'] * len(self.agents)
        else:
            agent_models = [model for model in data['agent_models'].values()]

        environment_scenario: str = data['environment']
        env_profile = {
            'codename': str(uuid.uuid1()),
            'scenario': environment_scenario,
            'agent_goals': agent_goals,
        }

        start_message = {
            'type': 'START_SIM',
            'data': {
                'agent_models': agent_models,
                'env_profile_dict': env_profile,
                'agent_profile_dicts': agent_profile_list,
            },
        }

        await self.websocket.send_json(start_message)
        try:
            confirmation_msg = await self.websocket.receive_json()
        except Exception:
            return True
        # FIXME: a neat way to exit
        if confirmation_msg.get('type', '') != 'SERVER_MSG':
            return True

        self.agents.append('all')
        return False

    # def return_timeout_error(args) -> Observation:
    #     return ErrorObservation('Person took too long to respond')

    # # FIXME: should we have re-tries here?
    # @tenacity.retry(
    #         wait=tenacity.wait_exponential(min=20, max=100),
    #         stop=tenacity.stop_after_attempt(1) | stop_if_should_exit(),
    #         retry_error_callback=return_timeout_error,
    # )
    async def send_message_receive_response(self, npc_msg: dict):
        # npc_name: str = npc_msg['data']['to']
        if self.websocket is not None:
            await self.websocket.send_json(npc_msg)
        max_cnt = 3
        for _ in range(max_cnt):
            if self.websocket is not None:
                msg = await self.websocket.receive_json()
            else:
                break
            # print(msg)
            if msg['type'] == 'SERVER_MSG':
                messages = msg['data']['messages']
                last_msg: list[str] = messages[-1][0]
                # print(last_msg)
                # FIXME: do we want to check if the person who responded is same as the person we sent message to?
                if last_msg[0] == 'redis_agent':
                    continue
                else:
                    content: str = last_msg[-1]
                    try:
                        content = content.split('said:')[-1].strip()
                        content = content.split(f'{content[0]} to ')[0].strip()
                    except Exception:
                        content = last_msg[-1]
                    return ChatObservation(content=content, npc_name=last_msg[0])
        return ErrorObservation('Person took too long to respond')


async def chat(action: ChatAction, chat_env: ChatEnv) -> Observation:
    if chat_env.started_env is False or chat_env.websocket is None:
        error = await chat_env.start_simulation()
        if error:
            return ErrorObservation(
                'Failed to send start simulation message to websocket server'
            )
        chat_env.started_env = True
        # FIXME: NEED THIS HACK TO AVOID SENDING MSG JUST AFTER STARTING THE ENV
        await asyncio.sleep(20)
        # print(chat_env.websocket)

    if chat_env.websocket is None:
        return ErrorObservation('Websocket connection does not exist')
    agent_name = action.npc_name
    msg = action.content

    if agent_name not in chat_env.agents:
        return ErrorObservation(
            f'{agent_name} does not exist. You can interact only with the following agents: {', '.join(chat_env.agents[:-1])} or broadcast your message to all the agents by sending a message to {chat_env.agents[-1]}'
        )

    npc_msg = {
        'type': 'CLIENT_MSG',
        'data': {
            'content': msg,
            'to': agent_name,
        },
    }
    obs: Observation = await chat_env.send_message_receive_response(npc_msg)
    if isinstance(obs, ErrorObservation):
        obs = ErrorObservation(content=f'{agent_name} took too long to respond.')
    return obs
